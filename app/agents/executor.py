"""
Agent Executor — full pipeline with REAL form submission.

Pipeline (as per DevApply_IDX_Specification.md):
  1. Job Search Agent     → Search 6 platforms
  2. Job Analysis Agent   → Score & rank jobs
  3. Resume Agent         → Customize cover letter
  4. Application Agent    → Playwright form fill + submit + OCR verify
  5. Email notification   → Send summary to user
"""
import asyncio
import logging
import uuid
from datetime import datetime
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)


class AgentWorkflowResult:
    def __init__(self, jobs_found=0, applications_submitted=0, applications_queued=0, status="completed"):
        self.jobs_found = jobs_found
        self.applications_submitted = applications_submitted
        self.applications_queued = applications_queued
        self.status = status
        self.completed_at = datetime.now().isoformat()


def _log(level: str, message: str, task_id: Optional[str] = None):
    try:
        from app.backend.services.agent_log_store import add_log
        add_log(level, message, task_id)
    except Exception:
        pass
    logger.info(f"[{level}] {message}")


async def _update_application_status(
    user_id: str, strategy_id: str, job: Dict, score: int, status: str, error: str = ""
) -> Optional[str]:
    """Save or update an application record. Returns record ID."""
    try:
        from app.backend.database.connection import AsyncSessionLocal
        from app.backend.models.application import Application

        async with AsyncSessionLocal() as db:
            record = Application(
                id=uuid.uuid4(),
                user_id=uuid.UUID(user_id),
                strategy_id=uuid.UUID(strategy_id),
                job_title=job.get("title", "Unknown")[:255],
                company_name=job.get("company", "Unknown")[:255],
                platform=job.get("platform", "Unknown")[:50],
                job_url=(job.get("url") or "")[:500],
                job_description=(job.get("description") or "")[:2000],
                status=status,
                match_score=score,
                ai_recommendation=f"Auto-matched {score}/100. Status: {status}",
                submission_success=(status == "Applied"),
                error_message=error[:500] if error else None,
                applied_date=datetime.now(),
                response_received=False,
            )
            db.add(record)
            await db.commit()
            return str(record.id)
    except Exception as e:
        logger.error(f"DB save failed: {e}")
        return None


async def _get_resume_path(user_profile: Dict) -> Optional[str]:
    """Find the user's primary resume file path from the database."""
    import os

    try:
        from app.backend.database.connection import AsyncSessionLocal
        from app.backend.models.resume import Resume
        from sqlalchemy.future import select
        import uuid
        uid = user_profile.get("user_id", "")
        if not uid:
            return None
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Resume)
                .where(Resume.user_id == uuid.UUID(uid))
                .order_by(Resume.is_primary.desc(), Resume.upload_date.desc())
            )
            resume = result.scalars().first()
            if resume and resume.file_path and os.path.exists(resume.file_path):
                return resume.file_path
    except Exception as e:
        logger.warning(f"Resume DB lookup failed: {e}")
    return None


async def run_agent_workflow(
    user_strategy: dict,
    user_profile: dict,
    task_id: Optional[str] = None,
) -> AgentWorkflowResult:
    """
    Full 5-stage pipeline.
    Stages 1–3 always run. Stage 4 (form submission) runs if Playwright is available.
    """
    from app.backend.services.agent_log_store import set_running, set_idle

    result = AgentWorkflowResult()
    strategy_name = user_strategy.get("name", "Default Strategy")
    strategy_id = user_strategy.get("id", "")
    job_titles = user_strategy.get("target_job_titles") or []
    user_id = user_profile.get("user_id", "")
    user_email = user_profile.get("email", "user")
    user_skills = user_profile.get("skills", "")
    max_apps = int(user_strategy.get("max_applications_per_run") or 5)

    set_running(task_id or "manual", "running")
    _log("INFO", f"🚀 Starting DevApply pipeline — Strategy: '{strategy_name}'", task_id)
    _log("INFO", f"👤 User: {user_email} | Targets: {', '.join(job_titles) or 'General'}", task_id)
    _log("INFO", f"📋 Max applications this run: {max_apps}", task_id)

    # ─── STAGE 1: Job Search ───────────────────────────────────────────────
    _log("INFO", "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", task_id)
    _log("INFO", "🔍 STAGE 1: Job Search across 6 platforms", task_id)
    _log("INFO", "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", task_id)

    from app.agents.tools.search_tools import (
        search_linkedin, search_remoteok, search_adzuna,
        search_weworkremotely, search_jobicy, search_remotive
    )

    all_jobs: List[Dict] = []
    titles = job_titles[:3] if job_titles else ["Software Engineer"]
    sources = [
        ("LinkedIn",       lambda t: search_linkedin(t)),
        ("RemoteOK",       lambda t: search_remoteok(t)),
        ("Adzuna",         lambda t: search_adzuna(t)),
        ("WeWorkRemotely", lambda t: search_weworkremotely(t)),
        ("Jobicy",         lambda t: search_jobicy(t)),
        ("Remotive",       lambda t: search_remotive(t)),
    ]

    for title in titles:
        _log("INFO", f"   🔎 '{title}'", task_id)
        for src_name, fn in sources:
            try:
                jobs = fn(title)
                _log("INFO", f"      → {src_name}: {len(jobs)} jobs", task_id)
                all_jobs.extend(jobs)
            except Exception as e:
                _log("WARN", f"      → {src_name}: error — {str(e)[:50]}", task_id)
            await asyncio.sleep(0.1)

    # Deduplicate
    seen, unique_jobs = set(), []
    for j in all_jobs:
        key = j.get("url") or j.get("title", "")
        if key and key not in seen:
            seen.add(key)
            unique_jobs.append(j)

    result.jobs_found = len(unique_jobs)
    _log("INFO", f"✅ Stage 1 complete: {len(unique_jobs)} unique jobs found", task_id)

    # ─── STAGE 2: Analysis & Scoring ──────────────────────────────────────
    _log("INFO", "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", task_id)
    _log("INFO", "🧠 STAGE 2: Job Analysis & Scoring", task_id)
    _log("INFO", "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", task_id)
    await asyncio.sleep(0.3)

    skill_words = {s.strip().lower() for s in user_skills.split(",") if s.strip()} if user_skills else set()

    for job in unique_jobs:
        haystack = f"{job.get('title','')} {job.get('description','')}".lower()
        score = 55
        for sk in skill_words:
            if sk in haystack:
                score = min(100, score + 8)
        for t in job_titles:
            if t.lower() in haystack:
                score = min(100, score + 12)
        job["match_score"] = score

    scored = sorted(unique_jobs, key=lambda j: j["match_score"], reverse=True)
    top_jobs = scored[:max_apps]

    _log("INFO", f"✅ Stage 2 complete — top {len(top_jobs)} matches:", task_id)
    for i, j in enumerate(top_jobs, 1):
        _log("INFO", f"   {i}. '{j.get('title')}' @ '{j.get('company')}' [{j.get('platform')}] — {j['match_score']}/100", task_id)

    # ─── STAGE 3: Resume / Cover Letter ───────────────────────────────────
    _log("INFO", "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", task_id)
    _log("INFO", "✍️  STAGE 3: Cover Letter Customisation", task_id)
    _log("INFO", "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", task_id)

    resume_path = await _get_resume_path(user_profile)
    if resume_path:
        _log("INFO", f"   📄 Resume found: {resume_path}", task_id)
    else:
        _log("WARN", "   ⚠️  No resume uploaded yet — go to Resumes page to upload your PDF", task_id)

    # Inject a job-specific cover letter into user_profile for each job
    base_cover = user_profile.get("profile_bio", "") or f"I am very interested in this position and believe my skills in {user_skills or 'software development'} are a great match."
    for job in top_jobs:
        job["cover_letter"] = (
            f"Dear Hiring Manager at {job.get('company','')},\n\n"
            f"{base_cover}\n\n"
            f"I am particularly excited about the {job.get('title','')} role and would love to contribute to your team.\n\n"
            f"Best regards,\n{user_profile.get('first_name','')} {user_profile.get('last_name','')}"
        )
    _log("INFO", f"   ✅ Cover letters customised for {len(top_jobs)} jobs", task_id)

    # ─── STAGE 4: Application Submission (Playwright) ─────────────────────
    _log("INFO", "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", task_id)
    _log("INFO", "📨 STAGE 4: Automated Form Submission", task_id)
    _log("INFO", "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", task_id)

    submitted = 0
    queued = 0
    submitted_jobs = []

    # Check if Playwright is available
    playwright_available = False
    try:
        from playwright.async_api import async_playwright
        playwright_available = True
        _log("INFO", "   ✅ Playwright available — real form submission enabled", task_id)
    except ImportError:
        _log("WARN", "   ⚠️  Playwright not installed — jobs will be queued for manual review", task_id)

    if playwright_available:
        from app.agents.application_agent import ApplicationAgent
        agent = ApplicationAgent()

        # Build enriched user profile for form filling
        fill_profile = {
            **user_profile,
            "cover_letter_template": base_cover,
        }

        for idx, job in enumerate(top_jobs, 1):
            title = job.get("title", "?")
            company = job.get("company", "?")
            _log("INFO", f"   [{idx}/{len(top_jobs)}] Applying → '{title}' @ '{company}'...", task_id)

            app_result = await agent.apply_to_job(
                job=job,
                user_profile=fill_profile,
                resume_path=resume_path,
                headless=True,
            )

            if app_result["success"]:
                status = "Applied"
                _log("SUCCESS", f"   🎉 Applied successfully to '{title}' @ '{company}'!", task_id)
                submitted += 1
                submitted_jobs.append(job)
            else:
                status = "Queued"
                err = app_result.get("error") or "Unknown error"
                _log("WARN", f"   ⚠️  Could not auto-submit — queued. Reason: {str(err)[:80]}", task_id)
                queued += 1

            # Save to DB
            if user_id and strategy_id:
                await _update_application_status(
                    user_id=user_id,
                    strategy_id=strategy_id,
                    job=job,
                    score=job["match_score"],
                    status=status,
                    error=app_result.get("error", ""),
                )

            # Human-like delay between applications
            if idx < len(top_jobs):
                import random
                delay = random.uniform(3, 8)
                _log("INFO", f"   ⏳ Waiting {delay:.1f}s before next application...", task_id)
                await asyncio.sleep(delay)

    else:
        # Queue all jobs in DB without form submission
        for job in top_jobs:
            if user_id and strategy_id:
                await _update_application_status(
                    user_id=user_id, strategy_id=strategy_id,
                    job=job, score=job["match_score"],
                    status="Queued", error="Playwright not available",
                )
                queued += 1
            _log("INFO", f"   📋 Queued: '{job.get('title')}' @ '{job.get('company')}'", task_id)

    result.applications_submitted = submitted
    result.applications_queued = queued

    # ─── STAGE 5: Email Summary ────────────────────────────────────────────
    _log("INFO", "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", task_id)
    _log("INFO", "📧 STAGE 5: Sending Email Summary", task_id)
    _log("INFO", "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", task_id)

    try:
        from app.backend.services.email_service import send_run_summary_email
        sent = send_run_summary_email(
            recipient_email=user_email,
            strategy_name=strategy_name,
            jobs_found=len(unique_jobs),
            jobs_applied=submitted_jobs or top_jobs[:5],
            jobs_searched=scored[:20],
        )
        if sent:
            _log("SUCCESS", f"   ✅ Summary email sent to {user_email}", task_id)
        else:
            _log("INFO", f"   📭 Email disabled — set EMAIL_ENABLED=true in .env", task_id)
    except Exception as e:
        _log("WARN", f"   Email error: {str(e)[:60]}", task_id)

    # ─── Done ────────────────────────────────────────────────────────────────
    result.status = "completed"
    set_idle("completed")
    _log("SUCCESS", f"🎉 Pipeline done!", task_id)
    _log("SUCCESS", f"   Jobs found: {result.jobs_found} | Submitted: {submitted} | Queued: {queued}", task_id)
    if not playwright_available:
        _log("INFO", "💡 Install Playwright to enable real form submission: playwright install chromium", task_id)

    return result
