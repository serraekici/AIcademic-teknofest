import os
import requests
import json
from dotenv import load_dotenv
from datetime import datetime, timedelta
from datetime import timezone

# .env dosyasından API Key çekiyoruz
load_dotenv()
API_KEY = os.getenv("TICKETMASTER_API_KEY")

if not API_KEY:
    print("❌ .env dosyasında TICKETMASTER_API_KEY bulunamadı.")
    exit()

base_url = "https://app.ticketmaster.com/discovery/v2/events.json"

# Bugünden itibaren 1 gün sonrası
start_date = (datetime.now(timezone.utc) + timedelta(days=1)).strftime("%Y-%m-%dT00:00:00Z")


# 5 kategori
categories = {
    "Konser": "music",
    "Festival": "festival",
    "Tiyatro": "theatre",
    "Sergi": "arts & culture",
    "Workshop": "education"
}

results = []

def check_image(url):
    try:
        res = requests.head(url, timeout=3)
        return res.status_code == 200
    except:
        return False

def convert_event(e, tag):
    image_url = None
    if e.get("images"):
        try:
            image_url = sorted(e["images"], key=lambda x: x["width"], reverse=True)[0]["url"]
        except:
            image_url = None

    # image_url None ise, yedek ver
    if not image_url:
        image_url = "https://via.placeholder.com/300x200?text=Gorsel+Yok"

    venue = e.get("_embedded", {}).get("venues", [{}])[0]
    city = venue.get("city", {}).get("name", "Bilinmiyor")

    return {
        "category": tag,
        "title": e["name"],
        "url": e["url"],
        "start": e["dates"]["start"]["localDate"],
        "city": city,
        "image": image_url
    }


def get_events(classification, tag):
    params = {
        "countryCode": "TR",
        "classificationName": classification,
        "startDateTime": start_date,
        "sort": "date,asc",
        "size": 10,
        "apikey": API_KEY
    }

    response = requests.get(base_url, params=params)

    if not response.ok:
        print(f"❌ {tag} için API hatası:", response.status_code)
        return None

    events = response.json().get("_embedded", {}).get("events", [])

    for e in events:
        return convert_event(e, tag)

    return None

# Kategorileri tek tek çek
for tag, classification in categories.items():
    event = get_events(classification, tag)
    if event:
        results.append(event)

# Eksikleri doldur
if len(results) < 5:
    params = {
        "countryCode": "TR",
        "sort": "date,asc",
        "startDateTime": start_date,
        "size": 20,
        "apikey": API_KEY
    }

    response = requests.get(base_url, params=params)

    if response.ok:
        fallback_events = response.json().get("_embedded", {}).get("events", [])
        for e in fallback_events:
            event = convert_event(e, "Genel")
            if not any(ev["title"] == event["title"] for ev in results):
                results.append(event)
            if len(results) >= 5:
                break

# JSON'a kaydet
with open("ticketmaster_data.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"✅ Toplam {len(results)} etkinlik başarıyla kaydedildi.")
