import cv2
import numpy as np
import pytesseract
from PIL import Image
from typing import List, Dict

# Note: pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def detect_buttons(screenshot_path: str) -> List[Dict]:
    """Detect potential buttons like 'Apply', 'Submit', 'Next' using OCR."""
    image = cv2.imread(screenshot_path)
    if image is None:
        return []
        
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Use pytesseract to find text and its coordinates
    d = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
    
    buttons = []
    target_words = ["apply", "submit", "next", "continue", "upload"]
    
    n_boxes = len(d['level'])
    for i in range(n_boxes):
        text = d['text'][i].lower()
        if any(word in text for word in target_words):
            (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
            buttons.append({
                "text": text,
                "x": x + w // 2, # Center
                "y": y + h // 2,
                "box": (x, y, w, h)
            })
            
    return buttons

def is_captcha_present(screenshot_path: str) -> bool:
    """Basic check for CAPTCHA like keywords or patterns."""
    image = Image.open(screenshot_path)
    text = pytesseract.image_to_string(image).lower()
    
    captcha_keywords = ["captcha", "robot", "security check", "verify you are human"]
    return any(kw in text for kw in captcha_keywords)
