import asyncio
from app.automation.browser import BrowserManager
from app.automation.form_parser import parse_application_form, identify_resume_upload
from app.automation.vision import detect_buttons
from app.automation.human_simulation import human_like_typing, simulate_human_mouse_movement

async def apply_to_job(job_url: str, resume_path: str, user_data: dict):
    """Orchestrates the application process for a single job."""
    manager = BrowserManager(headless=False) # Headless=False for debugging/visibility
    await manager.start()
    page = await manager.get_page()
    
    try:
        await page.goto(job_url)
        await asyncio.sleep(2) # Wait for load
        
        # 1. Look for 'Apply' button
        await page.screenshot(path="tmp/job_page.png")
        buttons = detect_buttons("tmp/job_page.png")
        
        apply_btn = next((b for b in buttons if "apply" in b['text']), None)
        if apply_btn:
            # Shift coordinates based on scroll if needed, but for now click center
            await page.mouse.click(apply_btn['x'], apply_btn['y'])
            await asyncio.sleep(3)
        
        # 2. Parse form
        content = await page.content()
        fields = parse_application_form(content)
        
        # 3. Fill fields
        for field in fields:
            value = user_data.get(field['name']) or user_data.get(field['label'].lower().replace(" ", "_"))
            if value:
                selector = f"[name='{field['name']}']" if field['name'] != "unknown" else None
                if selector:
                    await page.focus(selector)
                    await human_like_typing(page, selector, value)
        
        # 4. Upload resume
        upload_field = identify_resume_upload(content)
        if upload_field and resume_path:
            selector = f"input[name='{upload_field['name']}']"
            await page.set_input_files(selector, resume_path)
            
        # 5. Submit
        await page.screenshot(path="tmp/form_filled.png")
        buttons = detect_buttons("tmp/form_filled.png")
        submit_btn = next((b for b in buttons if "submit" in b['text']), None)
        if submit_btn:
            await page.mouse.click(submit_btn['x'], submit_btn['y'])
            await asyncio.sleep(5)
            
        return "Application submitted (Simulated/Vision-assisted)"
        
    except Exception as e:
        return f"Application failed: {str(e)}"
    finally:
        await manager.stop()
