from flask import Flask, request, jsonify, send_from_directory
import json
import unicodedata
import re
from openai_chat import analyze_user_message
from yok import filtrele_json_programlar
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Verileri yükle
with open(os.path.join(BASE_DIR, "data", "uni_video_links.json"), "r", encoding="utf-8") as f:
    uni_video_links = json.load(f)

with open(os.path.join(BASE_DIR, "data", "universities.json"), "r", encoding="utf-8") as f:
    universities_data = json.load(f)


def normalize(text):
    text = unicodedata.normalize("NFKD", text).encode("ASCII", "ignore").decode()
    text = text.replace("ı", "i")
    text = text.upper()
    text = re.sub(r"[^A-ZÇGIOSU ]+", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def fuzzy_match(uni_name_norm, json_name_norm):
    return all(part in json_name_norm for part in uni_name_norm.split() if len(part) > 3)


def make_clickable(link):
    link = link.strip()
    if link.startswith("http://") or link.startswith("https://"):
        return link
    if link.startswith("www."):
        return "https://" + link
    # Doğrudan isim verilmişse (örn: sbu.edu.tr)
    return "https://" + link



app = Flask(__name__, static_folder="static", static_url_path="")

@app.route("/")
def index():
    return app.send_static_file('index.html')

@app.route("/analyze", methods=["POST"])
def analyze_and_recommend():
    data = request.json
    mesaj = data.get("message", "")

    if not mesaj:
        return jsonify({"error": "Mesaj boş olamaz."}), 400

    try:
        analiz = json.loads(mesaj) if mesaj.strip().startswith("{") else analyze_user_message(mesaj)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    session = {}
    for key in ["sınava_girdi", "puan_turu", "ilgi_alani", "siralama", "sehirler"]:
        if analiz.get(key) is not None:
            session[key] = analiz[key]

    try:
        siralama_raw = session.get("siralama")
        if siralama_raw is not None and str(siralama_raw).strip() != "":
            siralama_kullanici = float(str(siralama_raw).replace(".", "").replace(",", ".").strip())
        else:
            siralama_kullanici = None
    except:
        siralama_kullanici = None

    sehir_filtresi = None if session.get("sehirler") == "yok" else session.get("sehirler")

    tercihler = filtrele_json_programlar(
        puan_turu=session.get("puan_turu"),
        ilgi_alani=session.get("ilgi_alani"),
        siralama_kullanici=siralama_kullanici,
        sehirler=sehir_filtresi
    )

    if not tercihler and siralama_kullanici:
        tercihler = filtrele_json_programlar(
        puan_turu=session.get("puan_turu"),
        ilgi_alani=session.get("ilgi_alani"),
        siralama_kullanici=siralama_kullanici,
        sehirler=sehir_filtresi,
        sinava_girdi=session.get("sinava_girdi", True)
    )


    sonuc = []
    for t in tercihler:
        uni_adi_norm = normalize(t['üniversite'])

        video_link = next(
            (url for title, url in uni_video_links.items() if uni_adi_norm in normalize(title)),
            ""
        )
        print(f"🎥 Uni: {t['üniversite']} → Video: {video_link}")

        web_link = ""
        for u in universities_data:
            name_norm = normalize(u.get("name", ""))
            if uni_adi_norm in name_norm or name_norm in uni_adi_norm:
                web_link = u.get("web", "")
                break
            if fuzzy_match(uni_adi_norm, name_norm):
                web_link = u.get("web", "")
                break

        print(f"🌐 {t['üniversite']} → Web: {web_link}")


        if web_link:
            web_link = make_clickable(web_link)

        sonuc.append({
            "üniversite": t['üniversite'],
            "bölüm": t['bölüm'],
            "şehir": t['şehir'],
            "puan": t.get('puan', ''),
            "sıralama": t.get('sıralama', ''),
            "burs": t.get('burs', ''),
            "video_link": video_link,
            "web_site": web_link
        })


    return jsonify({"tercihler": sonuc})

@app.route("/university-detail", methods=["POST"])
def university_detail():
    data = request.json
    name = data.get("name", "")

    if not name:
        return jsonify({"error": "Üniversite ismi boş olamaz."}), 400

    normalized_query = normalize(name)
    query_words = normalized_query.split()

    city_words = ["ISTANBUL", "ANKARA", "AFYON", "IZMIR", "BURSA", "GAZIANTEP", "ESKISEHIR", "KONYA"]
    city_in_query = next((city for city in city_words if city in query_words), None)

    if city_in_query:
        query_words.remove(city_in_query)

    found_universities = []

    for uni in universities_data:
        normalized_uni_name = normalize(uni.get("name", ""))
        normalized_uni_address = normalize(uni.get("address", ""))

        matched_words = sum(1 for word in query_words if word in normalized_uni_name)
        match_ratio = matched_words / len(query_words) if query_words else 0

        if match_ratio >= 0.6:
            if city_in_query:
                if city_in_query in normalized_uni_address or city_in_query in normalized_uni_name:
                    found_universities.append(uni)
            else:
                found_universities.append(uni)

    if found_universities:
        return jsonify({"universiteler": found_universities})
    else:
        return jsonify({"error": "Üniversite bulunamadı."}), 404

if __name__ == "__main__":
    app.run(debug=True)
