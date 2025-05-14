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

# 📚 Cache'ler
book_cache = {}
article_cache = {}

# 🧠 Mesajı analiz et
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
    result = {"type": "kitap", "topic": "bilinmiyor", "level": None}
    for line in lines:
        if "Tür:" in line:
            type_value = line.split(":", 1)[1].strip().lower()
            result["type"] = type_value if type_value in ["kitap", "makale"] else "kitap"
        elif "Konu:" in line:
            result["topic"] = line.split(":", 1)[1].strip()
        elif "Seviye:" in line:
            seviye = line.split(":", 1)[1].strip().lower()
            if seviye in ["başlangıç", "orta", "ileri"]:
                result["level"] = seviye
    return result

# 📚 GPT'den kitap öner
def get_book_titles_from_gpt(topic, level, limit=10):
    prompt = f"""
Kullanıcı senden '{topic}' konusunda {level or 'her seviyede'} akademik kitaplar istiyor.
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

# 📚 Google Books

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
        "publishedDate": info.get("publishedDate", "Tarih yok"),
        "link": info.get("infoLink", "#")
    }

# 📄 Semantic Scholar

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

# 🧠 Seviye tahmini
def guess_level_with_gpt(text):
    beginner_keywords = ["introductory", "for beginners", "elementary", "easy to understand"]
    advanced_keywords = ["advanced", "in-depth", "for experienced", "comprehensive study"]
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
            return "başlangıç"
    for word in advanced_keywords:
        if word in text_lower:
            return "ileri"
    return gpt_guess

# 💬 Chat endpoint
@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "")
    if not user_message:
        return jsonify({"reply": "Lütfen bir mesaj girin."})

    analysis = analyze_user_message(user_message)
    topic = analysis["topic"]
    level = analysis["level"]
    item_type = analysis["type"]

    if item_type == "kitap":
        cache = book_cache
        if topic not in cache or not cache[topic]:
            cache[topic] = []
            titles = get_book_titles_from_gpt(topic, level, limit=10)
            for title, author in titles:
                info = fetch_google_books_info(title, author)
                if info:
                    level_guess = guess_level_with_gpt(info["description"]).lower()
                    info["level"] = level_guess
                    cache[topic].append(info)

        books = cache[topic]
        filtered_books = [book for book in books if level is None or book["level"] == level]

        if not filtered_books and level == "ileri":
            filtered_books = [book for book in books if book["level"] == "orta"]

        if not filtered_books:
            return jsonify({"reply": f"'{topic}' konusunda uygun seviyede kitap bulunamadı."})

        reply = f"📚 <b>'{topic}'</b> konusunda kitaplar:\n\n"
        for idx, book in enumerate(filtered_books, 1):
            reply += (
                f"{idx}. 📘 <a href=\"{book['link']}\" target=\"_blank\">{book['title']}</a>\n"
                f"👤 {book['authors']} | 📅 {book['publishedDate']}\n"
                + (f"🧠 Seviye: <b>{book['level'].capitalize()}</b>\n" if book.get("level") else "") +
                f"📝 {book['description'][:200]}...\n\n"
            )
        return jsonify({"reply": reply})

    elif item_type == "makale":
        cache = article_cache
        if topic not in cache or not cache[topic]:
            cache[topic] = []
            new_articles = get_articles_from_semantic_scholar(topic, limit=10)
            for art in new_articles:
                level_guess = guess_level_with_gpt(art["abstract"]).lower()
                art["level"] = level_guess
                cache[topic].append(art)

        articles = cache[topic]
        filtered_articles = [art for art in articles if level is None or art["level"] == level]

        if not filtered_articles and level == "ileri":
            filtered_articles = [art for art in articles if art["level"] == "orta"]

        if not filtered_articles:
            return jsonify({"reply": f"'{topic}' konusunda uygun seviyede makale bulunamadı."})

        reply = f"📄 <b>'{topic}'</b> konusunda makaleler:\n\n"
        for idx, art in enumerate(filtered_articles, 1):
            reply += (
                f"{idx}. 📄 <b>{art['title']}</b>\n"
                f"👤 {art['authors']} | 📅 {art['year']} | 🧠 Seviye: <b>{art['level'].capitalize()}</b>\n"
                f"📚 {art['venue']}\n"
                f"🔗 <a href=\"{art['url']}\" target=\"_blank\">Makale Linki</a>\n"
                f"📝 {art['abstract'][:200]}...\n\n"
            )
        return jsonify({"reply": reply})

    return jsonify({"reply": "Şu anda sadece kitap ve makale önerisi yapılabiliyor."})

# 🚀 Sunucuyu başlat
if __name__ == "__main__":
    app.run(debug=True)
