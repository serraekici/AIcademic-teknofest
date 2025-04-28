import os
import requests
import json
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# API anahtarını oku
API_KEY = os.getenv("YOUTUBE_API_KEY")
PLAYLIST_ID = "PLwD6iReEI9cfT57KIkynKlQORGFOExfvW"
url = "https://www.googleapis.com/youtube/v3/playlistItems"

params = {
    "part": "snippet",
    "playlistId": PLAYLIST_ID,
    "maxResults": 50,
    "key": API_KEY
}

videos = {}
while True:
    response = requests.get(url, params=params)
    data = response.json()

    for item in data["items"]:
        title = item["snippet"]["title"].strip().upper()
        video_id = item["snippet"]["resourceId"]["videoId"]
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        videos[title] = video_url

    if "nextPageToken" in data:
        params["pageToken"] = data["nextPageToken"]
    else:
        break

with open("uni_video_links.json", "w", encoding="utf-8") as f:
    json.dump(videos, f, indent=2, ensure_ascii=False)

print(f"🎉 {len(videos)} video başarıyla kaydedildi.")
