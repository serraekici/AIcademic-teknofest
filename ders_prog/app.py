import os
from dotenv import load_dotenv
from openai import OpenAI
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# .env dosyasından API anahtarını al
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def examlari_api_ile_cek(token):
    """
    Eğer dersler frontend'den gelmeyecekse, JWT ile veri tabanından çek.
    API'den dönen JSON'da difficulty alanı da olmalı!
    """
    url = "http://127.0.0.1:8000/api/exam-schedules/"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        exams = response.json()
        dersler = []
        for e in exams:
            dersler.append({
                "ders": e["course_name"],
                "tarih": e["exam_date"],
                "zorluk": e.get("difficulty", "orta")  # Default 'orta'
            })
        return dersler
    else:
        print("API'dan veri alınamadı! (Status code:", response.status_code, ")")
        print("Hata:", response.text)
        return []

def plan_prompt_olustur(dersler, yontem):
    ders_bilgisi = "\n".join([f"- {d['ders']} ({d['zorluk']}): {d['tarih']}" for d in dersler])
    prompt = f"""
Sen bir yapay zeka destekli eğitim danışmanısın.
Öğrencinin sınav tarihleri, derslerin zorluk seviyeleri ve tercih ettiği çalışma yöntemi aşağıda verilmiştir.

🧠 Çalışma Yöntemi: {yontem.upper()}
📆 Sınav Takvimi ve Zorluklar:
{ders_bilgisi}

Kurallar:
- Plan, {yontem} yöntemine uygun hazırlanmalı.
- Derslerin zorluk seviyelerine göre daha zor derslere daha fazla tekrar ve çalışma süresi ayrılmalı.
- Günlük plan sade, uygulanabilir ve öğrenci dostu olsun.
- Eğer Pomodoro ise: 25 dakika çalışma + 5 dakika mola, 4 setten sonra uzun mola.
- Eğer Blok ise: 60-90 dakikalık odaklanmış seanslar öner.
- Eğer Klasik ise: her ders için belirli gün ve saat öner.
- Eğer Yoğun Tekrar ise: sınava yakın dönemde tekrar odaklı plan yap.
- Planı haftalık ya da günlük olarak listele.

Şimdi bu bilgilere göre detaylı ve kişiselleştirilmiş bir çalışma planı oluştur.
"""
    return prompt

def plan_olustur(dersler, calisma_yontemi):
    prompt = plan_prompt_olustur(dersler, calisma_yontemi)
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Sen kişiye özel çalışma planı hazırlayan bir eğitim danışmanısın."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

@app.route('/api/generate-study-plan/', methods=['POST'])
def generate_study_plan():
    data = request.get_json()
    study_method = data.get('study_method')
    jwt_token = data.get('jwt_token')
    custom_request = data.get('custom_request')  # <- ekledik!
    dersler = []

    if "exams" in data and isinstance(data["exams"], list) and len(data["exams"]) > 0:
        for e in data["exams"]:
            dersler.append({
                "ders": e["course_name"],
                "tarih": e["exam_date"],
                "zorluk": e.get("difficulty", "orta")
            })
    elif jwt_token:
        dersler = examlari_api_ile_cek(jwt_token)

    if not dersler:
        return jsonify({'error': 'Ders verisi alınamadı.'}), 400

    prompt = plan_prompt_olustur(dersler, study_method)
    # Özel istek varsa prompt'a ekle!
    if custom_request:
        prompt += f"\nKullanıcının ekstra isteği: {custom_request}\n"
        prompt += "Ek istekleri mutlaka dikkate al."

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Sen kişiye özel çalışma planı hazırlayan bir eğitim danışmanısın."},
            {"role": "user", "content": prompt}
        ]
    )
    plan = response.choices[0].message.content
    return jsonify({'plan': plan})
if __name__ == "__main__":
    app.run(port=5000, debug=True)
