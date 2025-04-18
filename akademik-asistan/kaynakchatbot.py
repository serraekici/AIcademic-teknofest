import os
import re
import requests
import time
import random
from dotenv import load_dotenv
from openai import OpenAI

# 🔐 API Anahtarlarını yükle
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# 🔢 Kullanıcının kaç kaynak istediğini çıkar
def extract_limit_from_message(message, default=3):
    numbers = re.findall(r"\d+", message)
    if numbers:
        return int(numbers[0])
    return default

# 🧠 GPT ile tür, konu, seviye analizi
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
            {"role": "system", "content": "Sen bir akademik asistan analiz aracısısın."},
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

# 📚 GPT'den kitap başlıkları al
def get_book_titles_from_gpt(topic, level, limit=3):
    level_part = f"{level} seviyesinde" if level != "otomatik" else "Seviye belirtilmemiş. Uygun seviyede kitap öner."
    prompt = f"""
Kullanıcı senden '{topic}' konusunda {level_part} akademik kitaplar istiyor.
Sadece {limit} kitap öner. Her biri şu formatta olsun:
1. Kitap Adı – Yazar
2. ...
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

# 📖 Google Books API'den kitap bilgisi al
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

# 📊 Açıklamaya göre seviye tahmini
def guess_level_with_gpt(description):
    prompt = f"Aşağıdaki kitap açıklamasına göre bu kitabın akademik seviyesini belirt:\nSeçenekler: Başlangıç, Orta, İleri.\nSadece bir kelimeyle cevap ver.\n\nAçıklama:\n{description}"
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Sen bir akademik seviye sınıflandırıcısısın."},
            {"role": "user", "content": prompt}
        ],
        temperature=0,
        max_tokens=10
    )
    return response.choices[0].message.content.strip()

# 📄 Semantic Scholar'dan makale bilgisi al
def get_articles_from_semantic_scholar(topic, limit=3, retries=3):
    base_url = "https://api.semanticscholar.org/graph/v1/paper/search"
    fields = "title,authors,year,url,abstract,venue"
    params = {"query": topic, "limit": limit, "fields": fields}

    for attempt in range(retries):
        response = requests.get(base_url, params=params)
        if response.status_code == 429:
            print("⏳ Çok fazla istek. Bekleniyor ve tekrar deneniyor...")
            time.sleep(2 * (attempt + 1))
            continue
        if response.status_code != 200:
            print(f"❌ Semantic Scholar API hatası: {response.status_code}")
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

# 🎬 Ana Chatbot Döngüsü
print("🎓 GPT Akademik Asistan: Merhaba! Hangi konuda kitap veya makale arıyorsun?\n")

while True:
    user_input = input("👤 Sen: ")
    if user_input.lower() in ["exit", "quit", "çık", "görüşürüz"]:
        print("📘 Görüşmek üzere! Yardımcı olabileceğim başka bir şey olursa yine gel. 😊")
        break

    analysis = analyze_user_message(user_input)
    item_type = analysis["type"]
    topic = analysis["topic"]
    level = analysis["level"]
    limit = extract_limit_from_message(user_input, default=3)

    # Seviye boşsa "başlangıç" olarak ayarla
    if not level or level.lower() not in ["başlangıç", "orta", "ileri"]:
        level = "başlangıç"

    # Kullanıcı seviye belirtmiş mi kontrolü (filtreleme için)
    user_level_provided = any(x in user_input.lower() for x in ["başlangıç", "orta", "ileri"])

    print(f"🔎 GPT Analizi → Tür: {item_type}, Konu: {topic}, Seviye: {level}\n")

    if item_type == "kitap":
        print("📚 Kitaplar getiriliyor...\n")
        titles = get_book_titles_from_gpt(topic, level, limit=limit)
        if not titles:
            print("❌ Kitap önerileri alınamadı.")
            continue
        count = 1
        for title, author in titles:
            info = fetch_google_books_info(title, author)
            if not info:
                continue
            level_guess = guess_level_with_gpt(info["description"])
            if user_level_provided and level_guess.lower() != level.lower():
                continue
            print(f"{count}. 📘 {info['title']} – {info['authors']}")
            print(f"   📝 {info['description'][:200]}...")
            print(f"   🎯 GPT'ye Göre Seviye: {level_guess}")
            print(f"   🏛 Yayıncı: {info['publisher']} | 📅 Yıl: {info['publishedDate']}\n")
            count += 1

    elif item_type == "makale":
        print("📄 Makaleler getiriliyor...\n")
        articles = get_articles_from_semantic_scholar(topic, limit=limit)
        if not articles:
            print("❌ Makale bulunamadı.")
            continue
        for i, article in enumerate(articles, 1):
            abstract = article["abstract"]
            level_guess = guess_level_with_gpt(abstract)
            print(f"{i}. 📄 {article['title']} – {article['authors']}")
            print(f"   📰 {article['venue']} | 📅 {article['year']}")
            print(f"   📌 {abstract[:200]}...")
            print(f"   🎯 GPT'ye Göre Seviye: {level_guess}\n")

    else:
        print("❌ GPT, kaynak türünü anlayamadı. Lütfen 'kitap' ya da 'makale' istediğini belirterek tekrar yazar mısın?\n")
