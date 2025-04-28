from flask import Flask, request, render_template, Response
import os
import docx
import re
import json
from datetime import datetime, timedelta
import pytesseract
from PIL import Image

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Eğer Windows kullanıyorsan, Tesseract yolu
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_content(file_path):
    if file_path.endswith('.docx'):
        doc = docx.Document(file_path)
        text = ''
        for para in doc.paragraphs:
            text += para.text + '\n'
        return text
    elif file_path.endswith('.txt'):
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        return text
    elif file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
        img = Image.open(file_path)
        text = pytesseract.image_to_string(img, lang='tur')
        return text
    else:
        raise ValueError("Desteklenmeyen dosya türü. Sadece .docx, .txt, .png, .jpg yükleyin.")

def temizle_ders_programi(ders_programi):
    temiz_liste = []
    for satir in ders_programi:
        satir_lower = satir.lower()

        # Çöp kelimeleri belirle
        cop_kelime_listesi = [
            "kodu", "ders adı", "tarih", "kamp", "kampüs", "kat", 
            "vadi", "üniversite", "diş", "hastane", "online",
            "çalışma", "sınav", "saat"
        ]

        # Eğer satır çöp içeriyorsa ➔ atla
        if any(cop in satir_lower for cop in cop_kelime_listesi):
            continue

        # Eğer satırda tarih formatı varsa ➔ atla
        if re.search(r"\d{1,2}\.\d{1,2}\.\d{4}", satir):
            continue

        # Eğer satırda saat formatı varsa ➔ atla
        if re.search(r"\d{1,2}:\d{2}", satir):
            continue

        # Eğer satır sadece sayı veya noktalama içeriyorsa ➔ atla
        if not any(c.isalpha() for c in satir):
            continue

        # Eğer satır çok kısaysa ➔ atla
        if len(satir.split()) <= 1:
            continue

        temiz_liste.append(satir)
    return temiz_liste


def parse_content(text):
    ders_programi = []
    sinav_takvimi = []

    gunler_listesi = ["pazartesi", "salı", "çarşamba", "perşembe", "cuma", "cumartesi", "pazar"]

    satirlar = text.split("\n")
    temiz_satirlar = [satir.strip() for satir in satirlar if satir.strip()]

    gunler_bulundu = any(any(gun in satir.lower() for gun in gunler_listesi) for satir in temiz_satirlar)

    for satir in temiz_satirlar:
        satir_lower = satir.lower()

        # Tarih satırı mı?
        if re.match(r"^\d{1,2}\.\d{1,2}\.\d{4}", satir) or re.match(r"^\d{1,2}\s\w+\s\d{4}", satir):
            sinav_takvimi.append(satir)
            continue

        # Eğer ders günleri bulunmuşsa
        if gunler_bulundu:
            if any(gun in satir_lower for gun in gunler_listesi):
                ders_programi.append(satir)
        else:
            ders_programi.append(satir)

    # Ders listesini filtrele
    ders_programi = temizle_ders_programi(ders_programi)

    return ders_programi, sinav_takvimi

def create_study_schedule(ders_programi, sinav_takvimi, priority=None, baslangic_tarihi=None):
    if baslangic_tarihi is None:
        baslangic_tarihi = datetime.today()

    gunler_listesi = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]

    gun_ders_map = {}
    for satir in ders_programi:
        parcalar = satir.strip().split()
        if parcalar and parcalar[0].capitalize() in gunler_listesi:
            gun = parcalar[0].capitalize()
            ders = " ".join(parcalar[1:])
            gun_ders_map[gun] = ders

    sinavlar = []
    for satir in sinav_takvimi:
        tarih_eslesme = re.search(r"(\d{1,2})\.(\d{1,2})\.(\d{4})", satir)
        if tarih_eslesme:
            gun, ay, yil = tarih_eslesme.groups()
            tarih = datetime(int(yil), int(ay), int(gun))
            parcalar = satir.split()
            ders_adi = " ".join(parcalar[2:]) if len(parcalar) > 2 else "Sınav"
            sinavlar.append({"tarih": tarih, "ders": ders_adi})

    program = []
    son_tarih = max([s["tarih"] for s in sinavlar], default=baslangic_tarihi + timedelta(days=14))
    gun = baslangic_tarihi

    index = 0
    while gun <= son_tarih:
        gun_adi = gun.strftime("%A")
        gun_adi_tr = gun_adi.replace("Monday", "Pazartesi").replace("Tuesday", "Salı") \
            .replace("Wednesday", "Çarşamba").replace("Thursday", "Perşembe") \
            .replace("Friday", "Cuma").replace("Saturday", "Cumartesi").replace("Sunday", "Pazar")

        gun_plan = []

        if gun_adi_tr in gun_ders_map:
            gun_plan.append(f"{gun_ders_map[gun_adi_tr]} çalış")
        elif index < len(ders_programi):
            gun_plan.append(f"{ders_programi[index]} çalış")
            index += 1

        for sinav in sinavlar:
            kalan_gun = (sinav["tarih"] - gun).days
            if 0 <= kalan_gun <= 7:
                gun_plan.append(f"{sinav['ders']} tekrar yap")

        if priority and priority.lower() != "yok":
            gun_plan.append(f"{priority} dersi ağırlıklı çalış")

        if gun_plan:
            program.append({
                "tarih": gun.strftime("%d %B %Y %A"),
                "yapilacaklar": gun_plan
            })

        gun += timedelta(days=1)

    return program

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        files = request.files.getlist('file')
        priority = request.form.get('priority', '').strip()

        ders_programi = []
        sinav_takvimi = []

        for file in files:
            filename = file.filename
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

            try:
                content = extract_content(filepath)
            except Exception as e:
                print(f"Hata: {e}")
                continue

            dersler, sinavlar = parse_content(content)

            if len(sinavlar) > len(dersler):
                sinav_takvimi += sinavlar + dersler
            else:
                ders_programi += dersler + sinavlar

        program = create_study_schedule(ders_programi, sinav_takvimi, priority)

        response_data = {
            "ders_programi": ders_programi,
            "sinav_takvimi": sinav_takvimi,
            "calisma_programi": program
        }
        response_json = json.dumps(response_data, ensure_ascii=False)
        return Response(response=response_json, status=200, mimetype="application/json")
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
