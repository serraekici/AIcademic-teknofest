from flask_cors import CORS
from flask import Flask, request, jsonify
import json
import unicodedata
import re
from app.openai_chat import analyze_user_message
from app.yok import filtrele_json_programlar

app = Flask(__name__)

# Veri dosyalarını yükle
with open("uni_video_links.json", "r", encoding="utf-8") as f:
    uni_video_links = json.load(f)

with open("universities.json", "r", encoding="utf-8") as f:
    universities_data = json.load(f)

# Yardımcı Fonksiyonlar
def normalize(text):
    text = unicodedata.normalize("NFKD", text).encode("ASCII", "ignore").decode("ASCII").upper()
    text = text.replace("-", " ")
    text = re.sub(r"ÜNİVERSİTESİ", "", text)
    text = re.sub(r"UNIVERSITESI", "", text)
    text = re.sub(r"ÜNİVERSITE", "", text)
    text = re.sub(r"UNIVERSITE", "", text)
    text = re.sub(r"[^A-ZÇĞİÖŞÜ ]+", "", text)
    return text.strip()

def find_university_website(university_name):
    hedef = normalize(university_name)
    for uni in universities_data:
        aday = normalize(uni.get("name", ""))
        if hedef in aday or aday in hedef:
            return uni.get("web", "Resmi web sitesi bulunamadı")
    return "Resmi web sitesi bulunamadı"

def make_clickable(link):
    if link.startswith("http"):
        return link
    else:
        return "http://" + link

def find_university_video(university_name):
    uni_adi_norm = normalize(university_name)
    for title, url in uni_video_links.items():
        if uni_adi_norm in normalize(title):
            return url
    return "Tanıtım videosu bulunamadı"

# 🔥 API Rotaları
@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_message = request.json.get("message")
        session = {}

        analiz = analyze_user_message(user_message)
        if "hata" in analiz:
            return jsonify({"error": analiz["hata"]}), 400

        for key in ["sınava_girdi", "puan_turu", "ilgi_alani", "siralama", "sehirler"]:
            value = analiz.get(key)
            if value is not None:
                session[key] = value

        if "sınava_girdi" not in session or "ilgi_alani" not in session:
            return jsonify({"error": "Eksik bilgi: sınava_girdi veya ilgi_alani eksik."}), 400

        siralama_kullanici = (
            float(session.get("siralama")) if isinstance(session.get("siralama"), (int, float)) else None
        )
        sehir_filtresi = None if session.get("sehirler") == "yok" else session.get("sehirler")

        tercihler = filtrele_json_programlar(
            puan_turu=session.get("puan_turu"),
            ilgi_alani=session.get("ilgi_alani"),
            siralama_kullanici=siralama_kullanici,
            sehirler=sehir_filtresi
        )

        sonuc = []
        for tercih in tercihler:
            sonuc.append({
                "üniversite": tercih["üniversite"],
                "bölüm": tercih["bölüm"],
                "puan": tercih["puan"],
                "sıralama": tercih["sıralama"],
                "burs": tercih["burs"],
                "şehir": tercih["şehir"],
                "video": find_university_video(tercih["üniversite"]),
                "website": make_clickable(find_university_website(tercih["üniversite"]))
            })

        return jsonify({"tercihler": sonuc})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Ana Çalıştırma
if __name__ == "__main__":
    app.run(debug=True)
