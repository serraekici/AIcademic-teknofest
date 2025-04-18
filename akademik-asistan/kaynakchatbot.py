import os
import re
import requests
import time
import random
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

app = Flask(__name__)
CORS(app)

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
            result["type"] = line.split(":", 1)[1].strip()
        elif "Konu:" in line:
            result["topic"] = line.split(":", 1)[1].strip()
        elif "Seviye:" in line:
            result["level"] = line.split(":", 1)[1].strip()
    return result

def get_book_titles_from_gpt(topic, level, limit=5):
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
        max_tokens=300
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

def get_articles_from_semantic_scholar(topic, limit=5, retries=3):
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

def guess_level_with_gpt(text):
    prompt = f"Aşağıdaki açıklamaya göre bu içeriğin akademik seviyesini belirt:\nSeçenekler: Başlangıç, Orta, İleri.\nSadece bir kelimeyle cevap ver.\n\n{text}"
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Sen bir akademik içerik seviye tahmin aracısısın."},
            {"role": "user", "content": prompt}
        ],
        temperature=0,
        max_tokens=10
    )
    return response.choices[0].message.content.strip()

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
        titles = get_book_titles_from_gpt(topic, level, limit=5)
        results = []
        for title, author in titles:
            info = fetch_google_books_info(title, author)
            if info:
                level_guess = guess_level_with_gpt(info["description"])
                print(f"📘 GPT kitap seviyesi: {level_guess} (Kullanıcı seviyesi: {level})")
                results.append(
                    f"📘 {info['title']} – {info['authors']} ({info['publishedDate']})\n"
                    f"🧠 Seviye: {level_guess}\n"
                    f"📝 {info['description'][:150]}...\n"
                )
        if not results:
            return jsonify({"reply": "Kitap bulunamadı."})
        return jsonify({"reply": "\n\n".join(results)})

    elif item_type == "makale":
        articles = get_articles_from_semantic_scholar(topic, limit=5)
        results = []
        for article in articles:
            level_guess = guess_level_with_gpt(article["abstract"])
            print(f"📄 GPT makale seviyesi: {level_guess} (Kullanıcı seviyesi: {level})")
            results.append(
                f"📄 {article['title']} – {article['authors']} ({article['year']})\n"
                f"📚 {article['venue']}\n"
                f"🔗 {article['url']}\n"
                f"🧠 Seviye: {level_guess}\n"
                f"📝 {article['abstract'][:200]}...\n"
            )
        if not results:
            return jsonify({"reply": "Makale bulunamadı."})
        return jsonify({"reply": "\n\n".join(results)})

    else:
        return jsonify({"reply": "Şu anda yalnızca kitap ve makale önerisi yapılabilmektedir."})

if __name__ == "__main__":
    app.run(debug=True)
