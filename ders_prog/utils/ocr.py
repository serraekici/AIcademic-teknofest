import pytesseract
from PIL import Image
import cv2
import numpy as np
import os

# Eğer Windows'taysan şunu aktif et
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def preprocess_image(image_path):
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Görsel okunamadı: {image_path}")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)
    cleaned_path = image_path.replace(".jpg", "_cleaned.png").replace(".jpeg", "_cleaned.png").replace(".png", "_cleaned.png")
    cv2.imwrite(cleaned_path, thresh)
    return cleaned_path

def extract_text_from_image(image_path):
    cleaned_path = preprocess_image(image_path)
    image = Image.open(cleaned_path)
    text = pytesseract.image_to_string(image, lang='tur')
    return text
