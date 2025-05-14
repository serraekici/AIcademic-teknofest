import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("TICKETMASTER_API_KEY")

if not API_KEY:
    print("❌ .env dosyasında TICKETMASTER_API_KEY bulunamadı!")
    exit()

base_url = "https://app.ticketmaster.com/discovery/v2/events.json"

# Hedef kategoriler
categories = {
    "Konser": "music",
    "Festival": "festival",
    "Tiyatro": "theatre",
    "Sergi": "arts & culture",
    "Workshop": "education"
}

results = []

def get_events(classification, tag):
    params = {
        "countryCode": "TR",
        "classificationName": classification,
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

def convert_event(e, tag):
    image_url = sorted(e["images"], key=lambda x: x["width"], reverse=True)[0]["url"]
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


# Her kategoriden bir tane almaya çalış
for tag, classification in categories.items():
    event = get_events(classification, tag)
    if event:
        results.append(event)

# Eksikse → kalanları karışık şekilde tamamla
if len(results) < 5:
    params = {
        "countryCode": "TR",
        "sort": "date,asc",
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

# JSON olarak kaydet
with open("ticketmaster_data.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"✅ Toplam {len(results)} etkinlik kaydedildi.")
