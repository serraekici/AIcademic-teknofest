import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_user_message(message: str) -> dict:
    try:
        system_prompt = (
            "Kullanıcının mesajını analiz et ve şu bilgileri JSON olarak çıkar:\n"
            "- sınava_girdi: true ya da false (örn: 'girdim', 'evet' → true, 'girmedim', 'hayır' → false)\n"
            "- puan_turu: 'SAY', 'EA', 'SÖZ', 'DİL' ya da null\n"
            "- ilgi_alani: string ya da null\n"
            "- siralama: sayı ya da null\n"
            "- sehirler: string listesi ya da null (örn: ['İstanbul', 'Ankara'])\n"
            "Sadece geçerli bir JSON string döndür. Açıklama yapma. Eksik olanları null yap."
        )

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            temperature=0.2
        )

        raw = response.choices[0].message.content.strip()
        return json.loads(raw)

    except Exception as e:
        return {"hata": str(e)}
