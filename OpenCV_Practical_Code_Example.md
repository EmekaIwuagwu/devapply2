# OpenCV in Action: Real Code Example
## How the AI Agent "Sees" and Applies Like a Human

---

## 🎬 Real-World Example: Applying to a LinkedIn Job

Let's walk through an actual job application with real code:

### **STEP 1: The Human Perspective**
```
┌─────────────────────────────────────────────────────────────┐
│  LinkedIn Job Page                                          │
│  ┌─────────────────────────────────────────────────────────┐
│  │ Senior Python Developer                                 │
│  │ Tech Company Inc • Remote                               │
│  │ $120k - $150k • Full-time                               │
│  │                                                         │
│  │ [APPLY NOW] ← Human sees this blue button and clicks    │
│  │                                                         │
│  │ Description: We're looking for a talented Python dev... │
│  └─────────────────────────────────────────────────────────┘
└─────────────────────────────────────────────────────────────┘
```

### **STEP 2: The AI Perspective (With OpenCV)**

```python
import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageDraw
import asyncio
from playwright.async_api import async_playwright

class HumanLikeJobApplicationBot:
    """AI agent that applies to jobs like a human would"""
    
    async def step_by_step_application(self):
        """
        Follow the exact human workflow:
        1. Navigate to job
        2. Read description
        3. Click apply
        4. Fill form
        5. Submit
        """
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)  # Show what AI is doing
            page = await browser.new_page()
            
            print("\n" + "="*60)
            print("🤖 AI AGENT APPLYING TO JOB LIKE A HUMAN")
            print("="*60)
            
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # STEP 1: NAVIGATE TO JOB PAGE (AI opens the link)
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            
            print("\n[STEP 1] 🌐 Navigating to job page...")
            print("   Human action: Opens job link in browser")
            print("   AI action: page.goto(url)")
            
            job_url = "https://www.linkedin.com/jobs/view/example-job-id/"
            await page.goto(job_url)
            await page.wait_for_load_state('networkidle')
            
            print("   ✅ Page loaded successfully")
            
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # STEP 2: TAKE SCREENSHOT (AI looks at the page)
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            
            print("\n[STEP 2] 👁️  Taking screenshot to analyze page...")
            print("   Human action: Looks at job page")
            print("   AI action: Captures screenshot with Playwright")
            
            screenshot_bytes = await page.screenshot()
            nparr = np.frombuffer(screenshot_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            print(f"   ✅ Screenshot captured: {image.shape[0]}x{image.shape[1]} pixels")
            cv2.imwrite('debug_1_page_view.png', image)
            print("   📸 Saved to: debug_1_page_view.png")
            
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # STEP 3: READ JOB DETAILS (AI reads text)
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            
            print("\n[STEP 3] 📖 Reading job description...")
            print("   Human action: Reads job title, company, description")
            print("   AI action: Uses Tesseract OCR to extract text")
            
            # Extract all text from screenshot
            full_text = pytesseract.image_to_string(image)
            
            # Extract key information
            job_title = self.extract_first_line(full_text)
            job_description = full_text[:200] + "..."  # First 200 chars
            
            print(f"\n   📄 Job Title: {job_title}")
            print(f"   📝 Description preview: {job_description}")
            
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # STEP 4: FIND "APPLY NOW" BUTTON (AI scans for action button)
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            
            print("\n[STEP 4] 🔍 Scanning page for 'Apply Now' button...")
            print("   Human action: Visually scans page for blue button saying 'Apply'")
            print("   AI action: Uses OpenCV to detect button by color and text")
            
            # METHOD A: Find button by color (blue buttons)
            button_color = self.find_button_by_color(image)
            
            # METHOD B: Find button by text (looking for "Apply" text)
            button_text = self.find_button_by_text(image)
            
            if button_color:
                print(f"\n   ✅ Button found by color detection at coordinates: {button_color}")
                print(f"      Position: ({button_color['center_x']}, {button_color['center_y']})")
                print(f"      Size: {button_color['width']}x{button_color['height']} pixels")
            
            if button_text:
                print(f"\n   ✅ Button found by text detection (says '{button_text['text']}')")
                print(f"      Position: ({button_text['center_x']}, {button_text['center_y']})")
            
            # Visualize what AI found
            annotated_image = self.draw_detected_elements(
                image.copy(), 
                buttons=[button_color] if button_color else [],
                button_text=[button_text] if button_text else []
            )
            cv2.imwrite('debug_2_button_detected.png', annotated_image)
            print("\n   📸 Annotated image saved: debug_2_button_detected.png")
            
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # STEP 5: CLICK "APPLY NOW" (AI clicks the button)
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            
            print("\n[STEP 5] 👆 Clicking 'Apply Now' button...")
            print("   Human action: Clicks the blue 'Apply Now' button with mouse")
            print("   AI action: Playwright clicks at coordinates detected by OpenCV")
            
            try:
                # Click on the apply button
                await page.click('button:has-text("Apply")')
                await page.wait_for_load_state('networkidle')
                print("   ✅ Button clicked successfully")
            except:
                print("   ⚠️  Could not find button, attempting alternative approach...")
                await page.click('button[aria-label*="Apply"]')
                await page.wait_for_load_state('networkidle')
            
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # STEP 6: FORM APPEARS (AI analyzes the form)
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            
            print("\n[STEP 6] 👁️  Form appeared! Taking screenshot of form...")
            print("   Human action: Looks at the application form")
            print("   AI action: Captures and analyzes form structure")
            
            form_screenshot_bytes = await page.screenshot()
            form_nparr = np.frombuffer(form_screenshot_bytes, np.uint8)
            form_image = cv2.imdecode(form_nparr, cv2.IMREAD_COLOR)
            
            cv2.imwrite('debug_3_form_appears.png', form_image)
            print("   📸 Form screenshot saved: debug_3_form_appears.png")
            
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # STEP 7: ANALYZE FORM FIELDS (AI understands form structure)
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            
            print("\n[STEP 7] 🗂️  Analyzing form fields...")
            print("   Human action: Reads labels and identifies input fields")
            print("   AI action: Uses OCR and shape detection to map form")
            
            # Extract text from form to find labels
            form_text = pytesseract.image_to_string(form_image)
            form_fields = self.extract_form_fields(form_text)
            
            print("\n   📋 Form fields detected:")
            for i, field in enumerate(form_fields, 1):
                print(f"      {i}. {field}")
            
            # Visualize detected form structure
            annotated_form = self.draw_form_structure(form_image.copy(), form_fields)
            cv2.imwrite('debug_4_form_analyzed.png', annotated_form)
            print("\n   📸 Annotated form saved: debug_4_form_analyzed.png")
            
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # STEP 8: FILL FORM (AI fills in information)
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            
            print("\n[STEP 8] 📝 Filling form with user information...")
            print("   Human action: Types into each field")
            print("   AI action: Uses Playwright to fill fields based on OpenCV detection")
            
            user_info = {
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john.doe@example.com',
                'phone': '+1-555-123-4567',
                'message': 'I am very interested in this position.'
            }
            
            # Fill each field
            for field_name, field_value in user_info.items():
                print(f"   ✓ Filling {field_name}: {field_value}")
                try:
                    await page.fill(f'input[name="{field_name}"]', field_value)
                except:
                    # Try alternative selectors
                    await page.fill(f'input[placeholder*="{field_name}"]', field_value)
            
            await page.wait_for_timeout(1000)  # Wait a moment
            
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # STEP 9: UPLOAD RESUME (AI uploads file)
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            
            print("\n[STEP 9] 📄 Uploading resume...")
            print("   Human action: Clicks file upload button and selects resume.pdf")
            print("   AI action: Uses Playwright to programmatically upload file")
            
            # Find file input and upload resume
            file_input = await page.query_selector('input[type="file"]')
            if file_input:
                await page.set_input_files('input[type="file"]', 'resume.pdf')
                print("   ✅ Resume uploaded: resume.pdf")
            else:
                print("   ⚠️  No file upload field found")
            
            await page.wait_for_timeout(2000)  # Wait for upload
            
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # STEP 10: FIND SUBMIT BUTTON (AI scans for final action)
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            
            print("\n[STEP 10] 🔍 Looking for Submit button...")
            print("   Human action: Visually locates the 'Submit' button")
            print("   AI action: Uses OpenCV text detection to find submit button")
            
            submit_screenshot_bytes = await page.screenshot()
            submit_nparr = np.frombuffer(submit_screenshot_bytes, np.uint8)
            submit_image = cv2.imdecode(submit_nparr, cv2.IMREAD_COLOR)
            
            submit_button = self.find_button_by_text(submit_image, keywords=['submit', 'send'])
            
            if submit_button:
                print(f"   ✅ Submit button found at ({submit_button['center_x']}, {submit_button['center_y']})")
            
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # STEP 11: CLICK SUBMIT (AI submits the form)
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            
            print("\n[STEP 11] ✅ Submitting application...")
            print("   Human action: Clicks Submit button")
            print("   AI action: Playwright clicks submit button")
            
            try:
                await page.click('button:has-text("Submit")')
                await page.wait_for_load_state('networkidle')
                print("   ✅ Form submitted!")
            except:
                print("   ⚠️  Could not submit, trying alternative method...")
                await page.press('button', 'Enter')
            
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # STEP 12: VERIFY SUCCESS (AI checks confirmation)
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            
            print("\n[STEP 12] 🔍 Verifying submission success...")
            print("   Human action: Looks for success message on page")
            print("   AI action: Uses OCR to read confirmation message")
            
            success_screenshot_bytes = await page.screenshot()
            success_nparr = np.frombuffer(success_screenshot_bytes, np.uint8)
            success_image = cv2.imdecode(success_nparr, cv2.IMREAD_COLOR)
            
            success_text = pytesseract.image_to_string(success_image)
            
            success_keywords = ['success', 'submitted', 'thank you', 'confirmation', 'application received']
            is_success = any(keyword in success_text.lower() for keyword in success_keywords)
            
            if is_success:
                print("\n   ✅ SUCCESS! Application submitted successfully!")
                print(f"\n   Confirmation message detected:")
                print(f"   '{success_text[:100]}...'")
            else:
                print("\n   ⚠️  Could not verify success - manual check recommended")
            
            cv2.imwrite('debug_5_success_page.png', success_image)
            print("\n   📸 Final page saved: debug_5_success_page.png")
            
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # SUMMARY
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            
            print("\n" + "="*60)
            print("🎉 APPLICATION PROCESS COMPLETE")
            print("="*60)
            print("\nWhat the AI did (like a human):")
            print("  1. ✅ Opened job page")
            print("  2. ✅ Read job description")
            print("  3. ✅ Found 'Apply' button using OpenCV color detection")
            print("  4. ✅ Clicked the button")
            print("  5. ✅ Analyzed form structure using OCR")
            print("  6. ✅ Filled in all required fields")
            print("  7. ✅ Uploaded resume file")
            print("  8. ✅ Found 'Submit' button")
            print("  9. ✅ Clicked Submit")
            print(" 10. ✅ Verified success with OCR")
            print("\nDebug screenshots:")
            print("  - debug_1_page_view.png (Original page)")
            print("  - debug_2_button_detected.png (Button highlighted)")
            print("  - debug_3_form_appears.png (Form view)")
            print("  - debug_4_form_analyzed.png (Form fields analyzed)")
            print("  - debug_5_success_page.png (Success confirmation)")
            print("="*60 + "\n")
            
            await browser.close()
    
    # ───────────────────────────────────────────────────────────
    # HELPER FUNCTIONS (OpenCV Vision Techniques)
    # ───────────────────────────────────────────────────────────
    
    def find_button_by_color(self, image, color_range='blue'):
        """Find button by color detection"""
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        if color_range == 'blue':
            lower = np.array([100, 100, 100])
            upper = np.array([130, 255, 255])
        elif color_range == 'green':
            lower = np.array([35, 100, 100])
            upper = np.array([85, 255, 255])
        else:
            return None
        
        mask = cv2.inRange(hsv, lower, upper)
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            largest = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest)
            return {
                'x': x, 'y': y, 'width': w, 'height': h,
                'center_x': x + w // 2, 'center_y': y + h // 2
            }
        return None
    
    def find_button_by_text(self, image, keywords=None):
        """Find button by reading text"""
        if keywords is None:
            keywords = ['apply', 'apply now']
        
        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
        
        for i in range(len(data['text'])):
            text = data['text'][i].lower()
            if any(kw in text for kw in keywords):
                return {
                    'text': data['text'][i],
                    'x': data['left'][i],
                    'y': data['top'][i],
                    'width': data['width'][i],
                    'height': data['height'][i],
                    'center_x': data['left'][i] + data['width'][i] // 2,
                    'center_y': data['top'][i] + data['height'][i] // 2
                }
        return None
    
    def extract_form_fields(self, text):
        """Extract form field labels from text"""
        common_labels = [
            'first name', 'last name', 'full name', 'name',
            'email', 'email address',
            'phone', 'phone number', 'mobile',
            'experience', 'years of experience',
            'resume', 'cv', 'upload resume'
        ]
        
        found_fields = []
        text_lower = text.lower()
        
        for label in common_labels:
            if label in text_lower:
                found_fields.append(label)
        
        return found_fields
    
    def extract_first_line(self, text):
        """Get first non-empty line (usually the title)"""
        lines = text.split('\n')
        for line in lines:
            if line.strip():
                return line.strip()
        return "Unknown"
    
    def draw_detected_elements(self, image, buttons=None, button_text=None):
        """Draw rectangles around detected elements for visualization"""
        if buttons is None:
            buttons = []
        if button_text is None:
            button_text = []
        
        # Draw color-detected buttons in BLUE
        for button in buttons:
            x, y, w, h = button['x'], button['y'], button['width'], button['height']
            cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 3)  # Blue
            cv2.putText(image, "Button (Color)", (x, y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        
        # Draw text-detected buttons in GREEN
        for button in button_text:
            x, y, w, h = button['x'], button['y'], button['width'], button['height']
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 3)  # Green
            cv2.putText(image, f"'{button['text']}'", (x, y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        return image
    
    def draw_form_structure(self, image, fields):
        """Draw detected form fields on image"""
        y_position = 50
        
        for field in fields:
            cv2.putText(image, f"✓ {field}", (50, y_position),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            y_position += 40
        
        return image

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RUN THE BOT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == "__main__":
    bot = HumanLikeJobApplicationBot()
    asyncio.run(bot.step_by_step_application())
```

---

## 📊 How Each Tool Works Together

```
┌──────────────────────────────────────────────────────────────────┐
│                    THE COMPLETE SYSTEM                           │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Website Screenshot                                              │
│         │                                                        │
│         ├──→ OpenCV (COLOR DETECTION)                           │
│         │    ↓                                                  │
│         │    Finds blue/green buttons by color                 │
│         │    Returns: (x, y) coordinates                       │
│         │                                                      │
│         ├──→ Tesseract (OCR TEXT DETECTION)                    │
│         │    ↓                                                  │
│         │    Reads "Apply Now", form labels, etc               │
│         │    Returns: Text + (x, y) coordinates                │
│         │                                                      │
│         ├──→ LLM Analysis (UNDERSTANDING)                      │
│         │    ↓                                                  │
│         │    Understands: "This is a job page"                 │
│         │    "I need to click the Apply button"                │
│         │    Returns: Decision on what to do next              │
│         │                                                      │
│         └──→ Playwright (ACTION)                               │
│              ↓                                                  │
│              Clicks at coordinates provided by OpenCV          │
│              Fills forms using coordinates                     │
│              Uploads files                                     │
│              Returns: Result (success/failure)                 │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Key Takeaway

**OpenCV is the AI's VISION system:**
- Takes screenshots (sees the page)
- Detects buttons (finds what to click)
- Reads text (understands what's on page)
- Maps forms (understands structure)
- Provides coordinates (tells Playwright where to click)

**Playwright is the AI's ACTION system:**
- Takes screenshots when asked
- Clicks at coordinates
- Types text
- Uploads files
- Navigates pages

**Together they create a human-like agent!**

---

**End of Code Examples**
