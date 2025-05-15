import os
from dotenv import load_dotenv
from openai import OpenAI

# .env dosyasından API anahtarını al
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# Dersler ve sınav tarihleri (örnek veri)
dersler = [
    {"ders": "Matematik", "tarih": "2025-05-20"},
    {"ders": "Fizik", "tarih": "2025-05-24"},
    {"ders": "Kimya", "tarih": "2025-05-27"},
]

# Kullanıcıdan tercih edilen çalışma yöntemini al
def kullanicidan_yontem_al():
    print("📌 Çalışma Yöntemleri:")
    print("1 - Pomodoro (25 dk çalışma + 5 dk mola)")
    print("2 - Blok (Uzun süreli, odaklanmış seanslar)")
    print("3 - Klasik (Derse göre gün ayırma)")
    print("4 - Yoğun Tekrar (Sınava yakın sık tekrar)")
    
    secenek = input("\nHangi çalışma yöntemini kullanmak istersin? (pomodoro / blok / klasik / yoğun tekrar): ").strip().lower()
    gecerli_yontemler = ["pomodoro", "blok", "klasik", "yoğun tekrar"]

    while secenek not in gecerli_yontemler:
        print("❗ Geçersiz seçim. Lütfen geçerli bir yöntem gir.")
        secenek = input("Yöntem (pomodoro / blok / klasik / yoğun tekrar): ").strip().lower()

    return secenek

# GPT prompt üretici
def plan_prompt_olustur(dersler, yontem):
    ders_bilgisi = "\n".join([f"- {d['ders']}: {d['tarih']}" for d in dersler])
    prompt = f"""
Sen bir yapay zeka destekli eğitim danışmanısın.
Öğrencinin sınav tarihleri ve tercih ettiği çalışma yöntemi aşağıda verilmiştir.

🧠 Çalışma Yöntemi: {yontem.upper()}
📆 Sınav Takvimi:
{ders_bilgisi}

Kurallar:
- Plan, {yontem} yöntemine uygun hazırlanmalı.
- Günlük plan sade, uygulanabilir ve öğrenci dostu olsun.
- Eğer Pomodoro ise: 25 dakika çalışma + 5 dakika mola, 4 setten sonra uzun mola.
- Eğer Blok ise: 60-90 dakikalık odaklanmış seanslar öner.
- Eğer Klasik ise: her ders için belirli gün ve saat öner.
- Eğer Yoğun Tekrar ise: sınava yakın dönemde tekrar odaklı plan yap.
- Planı haftalık ya da günlük olarak listele.

Şimdi bu bilgilere göre detaylı bir çalışma planı oluştur.
"""
    return prompt

# GPT-4 ile plan oluşturucu
def plan_olustur(dersler, calisma_yontemi):
    prompt = plan_prompt_olustur(dersler, calisma_yontemi)

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Sen kişiye özel çalışma planı hazırlayan bir eğitim danışmanısın."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content

# Ana çalıştırma
if __name__ == "__main__":
    print("👋 Merhaba! Sana özel bir çalışma planı oluşturacağım.")
    yontem = kullanicidan_yontem_al()
    print("\n📘 Kişiselleştirilmiş Çalışma Planın:\n")
    sonuc = plan_olustur(dersler, yontem)
    print(sonuc)
