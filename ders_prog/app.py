from flask import Flask, request, render_template, Response
import os
import docx
import re
import json
from datetime import datetime, timedelta
import pytesseract
from PIL import Image
from openai import OpenAI
from dotenv import load_dotenv

# .env yükle
load_dotenv()

# OpenAI Client
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Tesseract OCR yolu
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Satırları GPT ile sınıflandır
def classify_line_with_gpt(line):
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
        return json.loads(result)["tur"]
    except Exception as e:
        print(f"GPT Hatası: {e}")
        return "cop"

# Dosya içeriğini oku
def extract_content(file_path):
    if file_path.endswith('.docx'):
        doc = docx.Document(file_path)
        return "\n".join(para.text for para in doc.paragraphs)
    elif file_path.endswith('.txt'):
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    elif file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
        img = Image.open(file_path)
        return pytesseract.image_to_string(img, lang='tur')
    else:
        raise ValueError("Desteklenmeyen dosya türü.")

# İçeriği GPT ile ayrıştır
def parse_content(text, yukleme_tipi):
    ders_programi = []
    sinav_takvimi = []

    satirlar = text.split("\n")
    temiz_satirlar = [satir.strip() for satir in satirlar if satir.strip()]

    for satir in temiz_satirlar:
        tur = classify_line_with_gpt(satir)

        if yukleme_tipi == "ders_programi" and tur == "ders":
            ders_programi.append(satir)
        elif yukleme_tipi == "sinav_takvimi" and tur == "sinav":
            sinav_takvimi.append(satir)

    return ders_programi, sinav_takvimi

# Çalışma planı oluştur
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
            gun_ders_map.setdefault(gun, []).append(ders)

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

    while gun <= son_tarih:
        gun_adi = gun.strftime("%A")
        gun_adi_tr = gun_adi.replace("Monday", "Pazartesi").replace("Tuesday", "Salı") \
                             .replace("Wednesday", "Çarşamba").replace("Thursday", "Perşembe") \
                             .replace("Friday", "Cuma").replace("Saturday", "Cumartesi").replace("Sunday", "Pazar")

        gun_plan = []

        dersler = gun_ders_map.get(gun_adi_tr, [])
        for ders in dersler:
            gun_plan.append(f"{ders} çalış")

        if len(dersler) < 3:
            for sinav in sinavlar:
                kalan_gun = (sinav["tarih"] - gun).days
                if 0 <= kalan_gun <= 7:
                    gun_plan.append(f"{sinav['ders']} tekrar yap")

        if priority and priority.lower() not in ["", "hayır", "yok", "reset", "istemiyorum", "farketmez", "önemli değil", "no"]:
            gun_plan.append(f"{priority} dersi ağırlıklı çalış")

        if gun_plan:
            program.append({
                "tarih": gun.strftime("%d %B %Y %A"),
                "yapilacaklar": gun_plan
            })

        gun += timedelta(days=1)

    return program

# Ana route
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        files = request.files.getlist('file')
        yukleme_tipi = request.form.get('yukleme_tipi', '').strip().lower()
        priority = request.form.get('priority', '').strip().lower()

        if priority in ["", "hayır", "yok", "reset", "istemiyorum", "farketmez", "önemli değil", "no"]:
            priority = None

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

            dersler, sinavlar = parse_content(content, yukleme_tipi)

            ders_programi += dersler
            sinav_takvimi += sinavlar

        program = create_study_schedule(ders_programi, sinav_takvimi, priority)

        response_data = {
            "ders_programi": ders_programi,
            "sinav_takvimi": sinav_takvimi,
            "calisma_programi": program
        }
        response_json = json.dumps(response_data, ensure_ascii=False)
        return Response(response=response_json, status=200, mimetype="application/json")

    return render_template('index.html')

# Server başlat
if __name__ == '__main__':
    app.run(debug=True)
