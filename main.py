import requests

def search_academic_articles(topic):
    url = f"https://api.openalex.org/works?search={topic}&per-page=3"
    response = requests.get(url)
    data = response.json()
    
    if "results" not in data:
        return "Üzgünüm, bu konuda veri bulamadım."

    reply = f"🔎 İşte '{topic}' hakkında bazı akademik makaleler:\n\n"
    for i, result in enumerate(data["results"], start=1):
        title = result["title"]
        year = result.get("publication_year", "Yıl bilinmiyor")
        doi = result.get("doi", "DOI bulunamadı")
        reply += f"{i}. {title} ({year})\n📄 DOI: {doi}\n\n"
    
    return reply


# Basit chatbot simülasyonu
while True:
    user_input = input("Konu girin (çıkmak için 'exit'): ")
    if user_input.lower() == "exit":
        break
    print(search_academic_articles(user_input))

