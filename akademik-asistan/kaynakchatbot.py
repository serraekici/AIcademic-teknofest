import os
import re
import requests
import time
import random
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI

# 🔐 Ortam değişkenlerini yükle
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# 🚀 Flask başlat
app = Flask(__name__)
CORS(app)

# 📚 Çok konulu cache'ler
book_cache = {}
article_cache = {}

# 🧠 Kullanıcı mesajını analiz et
def analyze_user_message(message):
    prompt = f"""
Kullanıcının yazdığı cümlede ne tür kaynak istediğini, konusunu ve seviyesini çıkar.

Cümle: \"{message}\"

Cevabı sadece şu formatta ver:
Tür: kitap/makale
Konu: ...
Seviye: başlangıç/orta/ileri
"""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Sen bir akademik analiz aracısısın."},
            {"role": "user", "content": prompt}
        ],
        temperature=0,
        max_tokens=60
    )
    content = response.choices[0].message.content.strip()
    lines = content.split("\n")
    result = {"type": "kitap", "topic": "bilinmiyor", "level": "orta"}
    for line in lines:
        if "Tür:" in line:
            type_value = line.split(":", 1)[1].strip().lower()
            if type_value in ["kitap", "makale"]:
                result["type"] = type_value
            else:
                print(f"⚠️ Uyarı: Geçersiz tür bulundu: {type_value}. Kitap olarak varsayılıyor.")
                result["type"] = "kitap"
        elif "Konu:" in line:
            result["topic"] = line.split(":", 1)[1].strip()
        elif "Seviye:" in line:
            result["level"] = line.split(":", 1)[1].strip()
    return result

# 📚 GPT'den kitap adları al (limit=10)
def get_book_titles_from_gpt(topic, level, limit=10):
    prompt = f"""
Kullanıcı senden '{topic}' konusunda {level} seviyesinde akademik kitaplar istiyor.
Sadece {limit} kitap öner. Her biri şu formatta olsun:
1. Kitap Adı – Yazar
"""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Sen sadece akademik kitap önerileri yapan bir asistansın."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5,
        max_tokens=500
    )
    content = response.choices[0].message.content.strip()
    titles = []
    for line in content.split("\n"):
        match = re.match(r"^\s*(?:\d+[.\)]|•)?\s*(.*?)\s*[-–]\s*(.*)$", line.strip())
        if match:
            title = match.group(1).strip()
            author = match.group(2).strip()
            titles.append((title, author))
        if len(titles) == limit:
            break
    return titles

# 📚 Google Books'tan bilgi çek
def fetch_google_books_info(title, author):
    query = f"intitle:{title} inauthor:{author}"
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults=1"
    response = requests.get(url)
    if response.status_code != 200:
        return None
    items = response.json().get("items")
    if not items:
        return None
    info = items[0]["volumeInfo"]
    return {
        "title": info.get("title", "Bilinmeyen"),
        "authors": ", ".join(info.get("authors", ["Bilinmiyor"])),
        "description": info.get("description", "Açıklama bulunamadı."),
        "publisher": info.get("publisher", "Bilinmiyor"),
        "publishedDate": info.get("publishedDate", "Tarih yok")
    }

# 📚 Semantic Scholar'dan makale bilgisi çek
def get_articles_from_semantic_scholar(topic, limit=10, retries=3):
    base_url = "https://api.semanticscholar.org/graph/v1/paper/search"
    fields = "title,authors,year,url,abstract,venue"
    params = {"query": topic, "limit": limit, "fields": fields}

    for attempt in range(retries):
        response = requests.get(base_url, params=params)
        if response.status_code == 429:
            time.sleep(2 * (attempt + 1))
            continue
        if response.status_code != 200:
            return []
        results = response.json().get("data", [])
        articles = []
        for paper in results:
            articles.append({
                "title": paper.get("title", "Başlık yok"),
                "authors": ", ".join([a["name"] for a in paper.get("authors", [])]),
                "year": paper.get("year", "Yıl yok"),
                "url": paper.get("url", "#"),
                "abstract": paper.get("abstract") or "Özet bulunamadı.",
                "venue": paper.get("venue", "Dergi bilgisi yok")
            })
        random.shuffle(articles)
        return articles[:limit]
    return []

# 🧠 Açıklamadan seviye tahmini (GPT + Kelime kontrolü)
def guess_level_with_gpt(text):
    beginner_keywords = ["introductory", "for beginners", "no prior knowledge", "elementary", "easy to understand"]
    advanced_keywords = ["advanced", "in-depth", "for experienced", "for advanced readers", "comprehensive study"]

    prompt = f"""
Aşağıdaki açıklamaya göre bu içeriğin akademik seviyesini belirt:
Seçenekler: Başlangıç, Orta, İleri.
Sadece bir kelimeyle cevap ver.

{text}
"""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Sen bir akademik içerik seviye tahmin aracısısın."},
            {"role": "user", "content": prompt}
        ],
        temperature=0,
        max_tokens=10
    )
    gpt_guess = response.choices[0].message.content.strip().lower()

    text_lower = text.lower()

    for word in beginner_keywords:
        if word in text_lower:
            print(f"🔍 Anahtar kelime bulundu (başlangıç): {word}")
            return "başlangıç"

    for word in advanced_keywords:
        if word in text_lower:
            print(f"🔍 Anahtar kelime bulundu (ileri): {word}")
            return "ileri"

    return gpt_guess

# 📡 Ana chat endpoint
@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "")
    if not user_message:
        return jsonify({"reply": "Lütfen bir mesaj girin."})

    analysis = analyze_user_message(user_message)
    topic = analysis["topic"]
    level = analysis["level"].lower()
    item_type = analysis["type"]

    print(f"📥 Gelen mesaj: {user_message}")
    print(f"🧠 Analiz sonucu: Tür={item_type}, Konu={topic}, Seviye={level}")

    if item_type == "kitap":
        cache = book_cache
        if topic not in cache:
            cache[topic] = []

        books = cache[topic]
        filtered_books = [book for book in books if book["level"] == level]

        if not filtered_books:
            print(f"🚨 Kitap bulunamadı, yeni kitaplar çekiliyor: {topic}")
            titles = get_book_titles_from_gpt(topic, level, limit=10)
            for title, author in titles:
                info = fetch_google_books_info(title, author)
                if info:
                    level_guess = guess_level_with_gpt(info["description"]).lower()
                    books.append({
                        "title": info["title"],
                        "authors": info["authors"],
                        "description": info["description"],
                        "publishedDate": info["publishedDate"],
                        "link": info.get("infoLink", "#"),  # 📎 Link bilgisini de ekliyoruz!
                        "level": level_guess
                    })
            cache[topic] = books
            filtered_books = [book for book in books if book["level"] == level]

        if not filtered_books and level == "ileri":
            print("🔄 İleri seviye bulunamadı, orta seviye aranıyor...")
            filtered_books = [book for book in books if book["level"] == "orta"]

        if not filtered_books:
            return jsonify({"reply": f"'{topic}' konusunda uygun seviyede kitap bulunamadı."})

        reply = f"🔎 İşte '{topic}' için {level} seviyesinde bulduğum kitaplar:\n\n"
        for idx, book in enumerate(filtered_books, 1):
            reply += (
                f"{idx}. 📘 <a href=\"{book['link']}\" target=\"_blank\">{book['title']}</a> – {book['authors']} ({book['publishedDate']})\n"
                f"📝 {book['description'][:150]}...\n\n"
            )
        return jsonify({"reply": reply})

    elif item_type == "makale":
        cache = article_cache
        if topic not in cache:
            cache[topic] = []

        articles = cache[topic]
        filtered_articles = [art for art in articles if guess_level_with_gpt(art["abstract"]) == level]

        if not filtered_articles:
            print(f"🚨 Makale bulunamadı, yeni makaleler çekiliyor: {topic}")
            new_articles = get_articles_from_semantic_scholar(topic, limit=10)
            for art in new_articles:
                level_guess = guess_level_with_gpt(art["abstract"]).lower()
                art["level"] = level_guess
                articles.append(art)
            cache[topic] = articles
            filtered_articles = [art for art in articles if art["level"] == level]

        if not filtered_articles and level == "ileri":
            print("🔄 İleri seviye makale bulunamadı, orta seviye aranıyor...")
            filtered_articles = [art for art in articles if art["level"] == "orta"]

        if not filtered_articles:
            return jsonify({"reply": f"'{topic}' konusunda uygun seviyede makale bulunamadı."})

        reply = f"🔎 İşte '{topic}' için {level} seviyesinde bulduğum makaleler:\n\n"
        for idx, art in enumerate(filtered_articles, 1):
            reply += (
                f"{idx}. 📄 {art['title']} – {art['authors']} ({art['year']})\n"
                f"📚 {art['venue']}\n"
                f"🔗 <a href=\"{art['url']}\" target=\"_blank\">Makale Linki</a>\n"
                f"📝 {art['abstract'][:200]}...\n\n"
    )
        return jsonify({"reply": reply})

    else:
        return jsonify({"reply": "Şu anda sadece kitap ve makale önerisi yapılabilmektedir."})

# 🚀 Server'ı çalıştır
if __name__ == "__main__":
    app.run(debug=True)
