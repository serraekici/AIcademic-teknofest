from flask import Flask, request, render_template, Response
import os
import docx
import re
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

import pytesseract
from PIL import Image
import cv2
import numpy as np

from openai import OpenAI

# .env dosyasını yükle
load_dotenv()

# OpenAI API
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Windows için Tesseract OCR yolu
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# OCR öncesi görseli iyileştir
def preprocess_image(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return None

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(
        blur, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11, 2
    )
    return thresh

# OCR veya metin okuma
def extract_text(file_path):
    if file_path.endswith('.docx'):
        doc = docx.Document(file_path)
        return "\n".join(para.text for para in doc.paragraphs)
    elif file_path.endswith('.txt'):
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    elif file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
        processed_img = preprocess_image(file_path)
        if processed_img is not None:
            return pytesseract.image_to_string(processed_img, lang='tur')
        return ""
    else:
        return ""

# GPT ile sadece ders olanları tespit et
def is_ders_satiri(line):
    prompt = f"""
Satırı oku ve türünü belirle:

- Eğer satırda ders adı geçiyorsa veya gün adıyla başlayan bir satırsa (örneğin 'Pazartesi Sistem Programlama', 'Sağlıkta İletişim') → {{ "tur": "ders" }}
- Eğer satırda sınav tarihi varsa (örneğin '12.06.2025 Bilgisayar Ağları') → {{ "tur": "sinav" }}
- Eğer satır bina adı, kampüs bilgisi, saat bilgisi gibi ders/sınav olmayan bir şeyse → {{ "tur": "cop" }}

Satır: "{line}"

Sadece şu formatta kısa bir JSON döndür: {{ "tur": "..." }}
"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Satırları sınıflandıran yardımcı bir asistansın. Sadece JSON döndür."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        result = response.choices[0].message.content.strip()
        return json.loads(result)["tur"] == "ders"
    except Exception as e:
        print("GPT Hatası:", e)
        return False

# Flask route
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/dersleri-ayikla', methods=['POST'])
def dersleri_ayikla():
    uploaded_file = request.files.get('file')
    if not uploaded_file:
        return Response("Dosya yüklenmedi", status=400)

    filename = uploaded_file.filename
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    uploaded_file.save(file_path)

    text = extract_text(file_path)
    lines = [line.strip() for line in text.split('\n') if line.strip()]

    dersler = []
    for line in lines:
        if is_ders_satiri(line):
            dersler.append(line)

    return Response(json.dumps({"tespit_edilen_dersler": dersler}, ensure_ascii=False), mimetype="application/json")

if __name__ == '__main__':
    app.run(debug=True)
