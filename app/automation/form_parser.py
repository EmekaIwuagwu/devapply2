from bs4 import BeautifulSoup
from typing import List, Dict

def parse_application_form(html_content: str) -> List[Dict]:
    """Identify form fields and their types from HTML."""
    soup = BeautifulSoup(html_content, "html.parser")
    fields = []
    
    # Common form elements
    selectors = [
        "input[type='text']", 
        "input[type='email']", 
        "input[type='tel']",
        "textarea",
        "select"
    ]
    
    for selector in selectors:
        for element in soup.select(selector):
            name = element.get("name") or element.get("id") or element.get("placeholder") or "unknown"
            label = ""
            
            # Try to find associated label
            if element.get("id"):
                label_tag = soup.find("label", attrs={"for": element.get("id")})
                if label_tag:
                    label = label_tag.text.strip()
            
            fields.append({
                "type": element.name if element.name != "input" else element.get("type"),
                "name": name,
                "label": label,
                "placeholder": element.get("placeholder", ""),
                "required": element.has_attr("required")
            })
            
    return fields

def identify_resume_upload(html_content: str) -> Dict:
    """Find the resume upload input field."""
    soup = BeautifulSoup(html_content, "html.parser")
    upload_inputs = soup.select("input[type='file']")
    
    for inp in upload_inputs:
        text_context = inp.parent.text.lower() if inp.parent else ""
        if "resume" in text_context or "cv" in text_context:
            return {
                "name": inp.get("name"),
                "id": inp.get("id")
            }
    return None
