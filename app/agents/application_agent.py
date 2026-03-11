"""
Application Agent — the "hands" of DevApply.

Follows the exact spec from DevApply_IDX_Specification.md + OpenCV guides:

  1. Navigate to job URL (Playwright)
  2. Screenshot + OCR (OpenCV/Tesseract) to "see" page
  3. Detect "Apply" button — color + text detection
  4. Click Apply (human-like mouse movement)
  5. Screenshot form + detect fields (DOM-first, OCR fallback)
  6. Fill fields with user profile data
  7. Upload resume PDF
  8. Take screenshot to find Submit button
  9. Submit + verify success via OCR
  10. Log outcome to DB + send screenshot proof

Hot tip from spec: DOM parsing is faster and more reliable than pure OCR.
OCR (Tesseract) is used as a fallback when DOM parsing fails.
"""
import asyncio
import logging
import os
import random
import re
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ── Constants ─────────────────────────────────────────────────────────────────
APPLY_KEYWORDS = ["apply now", "apply", "easy apply", "quick apply", "apply for job"]
SUBMIT_KEYWORDS = ["submit", "submit application", "send", "send application", "complete"]
SUCCESS_KEYWORDS = ["thank you", "thanks", "submitted", "success", "application received",
                    "we received", "confirmation", "applied", "application sent"]

FIELD_MAP = {
    # field_label_keywords → user_profile_key
    ("first name", "firstname", "given name"):         "first_name",
    ("last name", "lastname", "surname", "family name"): "last_name",
    ("full name", "name", "your name"):                 "full_name",
    ("email", "e-mail", "email address"):               "email",
    ("phone", "telephone", "mobile", "contact number"): "phone",
    ("location", "city", "address", "current location"):  "location",
    ("linkedin", "linkedin url", "linkedin profile"):   "linkedin_url",
    ("github", "github url", "portfolio"):              "github_url",
    ("website", "personal website", "portfolio url"):   "portfolio_url",
    ("years of experience", "experience", "years exp"): "years_of_experience",
    ("cover letter", "cover letter text", "motivation"): "cover_letter",
    ("salary", "expected salary", "desired salary"):    "expected_salary",
}


class HumanBehaviorSimulator:
    """Mimics human typing speed and mouse behaviour to evade bot detection."""

    @staticmethod
    async def human_type(page, selector: str, text: str):
        """Type with variable speed, occasional micro-pauses between words."""
        try:
            await page.click(selector)
            await page.wait_for_timeout(random.randint(200, 500))
            # Clear existing content
            await page.fill(selector, "")
            await page.wait_for_timeout(100)
            # Type character by character
            for char in text:
                await page.type(selector, char, delay=random.randint(40, 130))
                if char == " " and random.random() < 0.1:
                    await page.wait_for_timeout(random.randint(100, 300))
        except Exception as e:
            logger.debug(f"human_type fallback for {selector}: {e}")
            try:
                await page.fill(selector, text)
            except Exception:
                pass

    @staticmethod
    async def human_click(page, selector: str):
        """Click with a small random offset and pre-click hover."""
        try:
            elem = page.locator(selector).first
            await elem.hover()
            await page.wait_for_timeout(random.randint(150, 400))
            await elem.click()
            await page.wait_for_timeout(random.randint(300, 800))
        except Exception as e:
            logger.debug(f"human_click fallback for {selector}: {e}")
            try:
                await page.click(selector)
            except Exception:
                pass

    @staticmethod
    async def random_delay(min_ms: int = 800, max_ms: int = 2500):
        await asyncio.sleep(random.uniform(min_ms / 1000, max_ms / 1000))


class DomFormAnalyzer:
    """
    DOM-first form field detector.
    Reads <label>, placeholder, aria-label, name attributes.
    Much more reliable than OCR for web forms.
    """

    @staticmethod
    async def get_form_fields(page) -> List[Dict]:
        """Return a list of fillable fields with their selector and detected purpose."""
        fields = await page.evaluate("""
        () => {
            const results = [];
            // All visible text inputs, textareas, selects
            const inputs = document.querySelectorAll(
                'input:not([type="hidden"]):not([type="submit"]):not([type="button"]):not([type="file"]), textarea, select'
            );
            inputs.forEach((el, idx) => {
                // Skip invisible elements
                const style = window.getComputedStyle(el);
                if (style.display === 'none' || style.visibility === 'hidden') return;

                let label = '';
                // 1. Associated <label>
                if (el.id) {
                    const labelEl = document.querySelector(`label[for="${el.id}"]`);
                    if (labelEl) label = labelEl.textContent.trim();
                }
                // 2. Wrapping <label>
                if (!label) {
                    const parentLabel = el.closest('label');
                    if (parentLabel) label = parentLabel.textContent.trim();
                }
                // 3. aria-label
                if (!label) label = el.getAttribute('aria-label') || '';
                // 4. placeholder
                if (!label) label = el.getAttribute('placeholder') || '';
                // 5. name attribute
                if (!label) label = el.getAttribute('name') || '';

                results.push({
                    idx,
                    tag: el.tagName.toLowerCase(),
                    type: el.getAttribute('type') || '',
                    id: el.id || '',
                    name: el.getAttribute('name') || '',
                    placeholder: el.getAttribute('placeholder') || '',
                    ariaLabel: el.getAttribute('aria-label') || '',
                    label: label.toLowerCase().trim(),
                    selector: el.id ? `#${el.id}` :
                              (el.name ? `[name="${el.name}"]` : null)
                });
            });
            return results;
        }
        """)
        return fields or []

    @staticmethod
    def match_field_to_profile(label: str, placeholder: str, name: str) -> Optional[str]:
        """Return the user_profile key that best matches this field."""
        haystack = f"{label} {placeholder} {name}".lower()
        for keywords, profile_key in FIELD_MAP.items():
            if any(kw in haystack for kw in keywords):
                return profile_key
        return None

    @staticmethod
    async def find_file_input(page) -> bool:
        """Check if page has a file upload input."""
        result = await page.evaluate("""
        () => !!document.querySelector('input[type="file"]')
        """)
        return bool(result)

    @staticmethod
    async def find_apply_button(page) -> Optional[str]:
        """Find the Apply button selector using DOM + text content."""
        for keyword in APPLY_KEYWORDS:
            # Try buttons, links, and divs with role=button
            for selector_tpl in [
                f'button:has-text("{keyword}")',
                f'a:has-text("{keyword}")',
                f'[role="button"]:has-text("{keyword}")',
            ]:
                try:
                    elem = page.locator(selector_tpl).first
                    count = await elem.count()
                    if count > 0:
                        return selector_tpl
                except Exception:
                    pass
        return None

    @staticmethod
    async def find_submit_button(page) -> Optional[str]:
        """Find Submit button."""
        for keyword in SUBMIT_KEYWORDS:
            for selector_tpl in [
                f'button:has-text("{keyword}")',
                f'input[type="submit"]:has-text("{keyword}")',
                f'[role="button"]:has-text("{keyword}")',
            ]:
                try:
                    count = await page.locator(selector_tpl).count()
                    if count > 0:
                        return selector_tpl
                except Exception:
                    pass
        # Fallback — any submit input
        try:
            c = await page.locator('input[type="submit"]').count()
            if c > 0:
                return 'input[type="submit"]'
        except Exception:
            pass
        return None


class ScreenshotManager:
    """Saves debug screenshots for audit trail and verification."""

    def __init__(self, base_dir: str = "screenshots"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    async def capture(self, page, name: str) -> str:
        """Take and save a screenshot, return path."""
        fname = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{name}.png"
        path = str(self.base_dir / fname)
        await page.screenshot(path=path, full_page=False)
        logger.info(f"📸 Screenshot saved: {path}")
        return path

    @staticmethod
    def ocr_read(screenshot_path: str) -> str:
        """Use Tesseract OCR to extract text from screenshot (optional)."""
        try:
            import pytesseract
            from PIL import Image
            img = Image.open(screenshot_path)
            return pytesseract.image_to_string(img).lower()
        except ImportError:
            logger.debug("Tesseract not installed — OCR skipped")
            return ""
        except Exception as e:
            logger.debug(f"OCR failed: {e}")
            return ""


class ApplicationAgent:
    """
    The core form-filling agent.
    Implements Agent 4 from DevApply_IDX_Specification.md.

    Workflow:
      navigate → screenshot → find Apply btn → click → analyze form
      → fill fields → upload resume → submit → verify → log
    """

    def __init__(self):
        self.human = HumanBehaviorSimulator()
        self.dom = DomFormAnalyzer()
        self.screenshots = ScreenshotManager()

    def _build_user_info(self, user_profile: Dict) -> Dict:
        """Build the complete user info dict for form filling."""
        first = user_profile.get("first_name", "")
        last = user_profile.get("last_name", "")
        return {
            "first_name": first,
            "last_name": last,
            "full_name": f"{first} {last}".strip() or user_profile.get("email", ""),
            "email": user_profile.get("email", ""),
            "phone": user_profile.get("phone", ""),
            "location": user_profile.get("location", ""),
            "linkedin_url": user_profile.get("linkedin_url", ""),
            "github_url": user_profile.get("github_url", ""),
            "portfolio_url": user_profile.get("portfolio_url", ""),
            "years_of_experience": str(user_profile.get("years_of_experience", "3")),
            "cover_letter": user_profile.get("cover_letter_template", ""),
            "expected_salary": user_profile.get("expected_salary", ""),
        }

    async def apply_to_job(
        self,
        job: Dict,
        user_profile: Dict,
        resume_path: Optional[str] = None,
        headless: bool = True,
    ) -> Dict:
        """
        Full application pipeline for a single job.
        Returns result dict: {success, status, screenshot, error}
        """
        job_url = job.get("url", "")
        job_title = job.get("title", "Unknown")
        company = job.get("company", "Unknown")

        if not job_url:
            return {"success": False, "status": "no_url", "error": "No job URL provided"}

        logger.info(f"🤖 Starting application — '{job_title}' @ '{company}'")
        logger.info(f"   URL: {job_url}")

        try:
            from playwright.async_api import async_playwright
        except ImportError:
            return {
                "success": False,
                "status": "playwright_missing",
                "error": "Playwright not installed. Run: playwright install chromium",
            }

        user_info = self._build_user_info(user_profile)
        result = {"success": False, "status": "unknown", "screenshot": None, "error": None}

        # ── Outer try wraps the entire Playwright context startup ──────────
        # async_playwright().__aenter__() itself can raise NotImplementedError
        # (asyncio child-watcher not attached, subprocess unsupported, or
        # browser binary missing) — this must be caught OUTSIDE the inner try.
        try:
            async with async_playwright() as p:
                try:
                    # ── Launch browser (stealth mode) ─────────────────────────
                    browser = await p.chromium.launch(
                        headless=headless,
                        args=[
                            "--no-sandbox",
                            "--disable-blink-features=AutomationControlled",
                            "--disable-infobars",
                        ],
                    )
                    context = await browser.new_context(
                        viewport={"width": 1920, "height": 1080},
                        user_agent=(
                            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/122.0.0.0 Safari/537.36"
                        ),
                        extra_http_headers={"Accept-Language": "en-US,en;q=0.9"},
                    )
                    # Remove webdriver fingerprint
                    await context.add_init_script(
                        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
                    )
                    page = await context.new_page()

                    # ── STEP 1: Navigate ───────────────────────────────────────
                    logger.info(f"   [1/9] Navigating to job page...")
                    await page.goto(job_url, wait_until="domcontentloaded", timeout=30000)
                    await self.human.random_delay(1000, 2500)
                    ss1 = await self.screenshots.capture(page, "1_job_page")
                    result["screenshot"] = ss1

                    # ── STEP 2: Find Apply button ─────────────────────────────
                    logger.info(f"   [2/9] Locating 'Apply' button...")
                    apply_selector = await self.dom.find_apply_button(page)

                    if not apply_selector:
                        # Try LinkedIn Easy Apply
                        try:
                            count = await page.locator('.jobs-apply-button').count()
                            if count > 0:
                                apply_selector = '.jobs-apply-button'
                        except Exception:
                            pass

                    if not apply_selector:
                        logger.info(f"   ⚠️  No Apply button found — this job may require external application")
                        result["status"] = "no_apply_button"
                        result["error"] = "Apply button not found on page"
                        await browser.close()
                        return result

                    logger.info(f"   ✅ Apply button found: {apply_selector}")

                    # ── STEP 3: Click Apply ───────────────────────────────────
                    logger.info(f"   [3/9] Clicking Apply button...")
                    await self.human.human_click(page, apply_selector)
                    await self.human.random_delay(1500, 3000)
                    ss2 = await self.screenshots.capture(page, "2_after_apply_click")

                    # ── STEP 4: Detect form fields ────────────────────────────
                    logger.info(f"   [4/9] Analyzing form structure...")
                    form_fields = await self.dom.get_form_fields(page)
                    logger.info(f"   ✅ {len(form_fields)} form fields detected")

                    # ── STEP 5: Fill form ─────────────────────────────────────
                    logger.info(f"   [5/9] Filling form fields...")
                    filled_count = 0
                    for field in form_fields:
                        profile_key = self.dom.match_field_to_profile(
                            field.get("label", ""),
                            field.get("placeholder", ""),
                            field.get("name", ""),
                        )
                        if not profile_key:
                            continue
                        value = user_info.get(profile_key, "")
                        if not value:
                            continue
                        selector = field.get("selector")
                        if not selector:
                            continue
                        try:
                            await self.human.human_type(page, selector, value)
                            logger.info(f"   ✓ {field.get('label','?')} → '{value[:30]}'")
                            filled_count += 1
                        except Exception as e:
                            logger.debug(f"   · Could not fill {selector}: {e}")

                    logger.info(f"   ✅ Filled {filled_count} fields")

                    # ── STEP 6: Upload resume ─────────────────────────────────
                    if resume_path and os.path.exists(resume_path):
                        logger.info(f"   [6/9] Uploading resume: {resume_path}")
                        has_file_input = await self.dom.find_file_input(page)
                        if has_file_input:
                            try:
                                await page.set_input_files('input[type="file"]', resume_path)
                                await self.human.random_delay(1000, 2000)
                                logger.info(f"   ✅ Resume uploaded")
                            except Exception as e:
                                logger.warning(f"   ⚠️  Resume upload failed: {e}")
                        else:
                            logger.info(f"   ⚪ No file input found on form")
                    else:
                        logger.info(f"   [6/9] No resume path provided — skipping upload")

                    ss3 = await self.screenshots.capture(page, "3_form_filled")

                    # ── STEP 7: Find submit button ────────────────────────────
                    logger.info(f"   [7/9] Locating Submit button...")
                    submit_selector = await self.dom.find_submit_button(page)
                    if not submit_selector:
                        logger.info(f"   ⚠️  Submit button not found automatically")
                        result["status"] = "no_submit_button"
                        result["error"] = "Could not find submit button"
                        await browser.close()
                        return result

                    logger.info(f"   ✅ Submit button: {submit_selector}")

                    # ── STEP 8: Submit ────────────────────────────────────────
                    logger.info(f"   [8/9] Submitting application...")
                    await self.human.human_click(page, submit_selector)
                    await self.human.random_delay(2000, 4000)
                    ss4 = await self.screenshots.capture(page, "4_after_submit")

                    # ── STEP 9: Verify success ────────────────────────────────
                    logger.info(f"   [9/9] Verifying submission...")
                    page_text = await page.inner_text("body")

                    # Try OCR as well if text extraction fails
                    ocr_text = ""
                    if hasattr(ss4, '__str__'):
                        ocr_text = self.screenshots.ocr_read(ss4)

                    combined = (page_text + " " + ocr_text).lower()
                    is_success = any(kw in combined for kw in SUCCESS_KEYWORDS)

                    if is_success:
                        logger.info(f"   🎉 SUCCESS — Application submitted to '{company}'!")
                        result["success"] = True
                        result["status"] = "submitted"
                        result["screenshot"] = ss4
                    else:
                        logger.warning(f"   ⚠️  Could not confirm success — manual review recommended")
                        result["success"] = False
                        result["status"] = "unverified"
                        result["screenshot"] = ss4
                        result["error"] = "Could not verify submission success"

                    await browser.close()
                    return result

                except Exception as e:
                    logger.error(f"Application agent error for '{job_title}': {e}")
                    result["success"] = False
                    result["status"] = "error"
                    result["error"] = str(e)[:200]
                    try:
                        await browser.close()
                    except Exception:
                        pass
                    return result

        except Exception as e:
            # Catches failures from async_playwright().__aenter__() itself:
            # – NotImplementedError: asyncio subprocess not supported on this loop
            # – Error: browser binary not installed (run: playwright install chromium)
            # – Any other startup-level failure
            err_name = type(e).__name__
            err_detail = str(e) or "Failed to start browser. Run: playwright install chromium"
            logger.error(f"Playwright startup failed for '{job_title}': {err_name}: {err_detail}")
            result["success"] = False
            result["status"] = "playwright_startup_error"
            result["error"] = f"{err_name}: {err_detail}"
            return result

        return result  # defensive fallback


async def run_application_batch(
    jobs: List[Dict],
    user_profile: Dict,
    resume_path: Optional[str] = None,
    max_applications: int = 5,
    headless: bool = True,
    log_fn=None,
) -> List[Dict]:
    """
    Submit applications to a batch of jobs.
    Returns list of result dicts.
    """
    agent = ApplicationAgent()
    results = []

    def _log(msg: str):
        logger.info(msg)
        if log_fn:
            log_fn(msg)

    for idx, job in enumerate(jobs[:max_applications]):
        title = job.get("title", "Unknown")
        company = job.get("company", "Unknown")
        _log(f"🤖 [{idx+1}/{min(len(jobs), max_applications)}] Applying to '{title}' @ '{company}'...")

        result = await agent.apply_to_job(
            job=job,
            user_profile=user_profile,
            resume_path=resume_path,
            headless=headless,
        )
        result["job"] = job
        results.append(result)

        if result["success"]:
            _log(f"   ✅ Applied successfully!")
        else:
            _log(f"   ⚠️  Status: {result['status']} — {result.get('error','')[:80]}")

        if idx < max_applications - 1:
            delay = random.uniform(3, 8)
            _log(f"   ⏳ Waiting {delay:.1f}s before next application...")
            await asyncio.sleep(delay)

    return results
