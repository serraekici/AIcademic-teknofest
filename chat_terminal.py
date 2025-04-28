from app.openai_chat import analyze_user_message
from app.yok import filtrele_json_programlar
import json
import re
import unicodedata

# Hafıza
session = {}

# 🎥 Tanıtım videolarını yükle
with open("uni_video_links.json", "r", encoding="utf-8") as f:
    uni_video_links = json.load(f)

# 🌐 Üniversite verilerini yükle
with open("universities.json", "r", encoding="utf-8") as f:
    universities_data = json.load(f)

# 🔧 Fonksiyonlar
def normalize(text):
    text = unicodedata.normalize("NFKD", text).encode("ASCII", "ignore").decode("ASCII").upper()
    text = text.replace("-", " ")
    text = re.sub(r"ÜNİVERSİTESİ", "", text)
    text = re.sub(r"UNIVERSITESI", "", text)
    text = re.sub(r"ÜNİVERSITE", "", text)
    text = re.sub(r"UNIVERSITE", "", text)
    text = re.sub(r"[^A-ZÇĞİÖŞÜ ]+", "", text)
    return text.strip()

def find_university_details(university_name):
    hedef_kelimeler = normalize(university_name).split()
    en_iyi_eslesen = None
    en_yuksek_skor = 0

    for uni in universities_data:
        aday_kelimeler = normalize(uni.get("name", "")).split()
        skor = sum(1 for kelime in hedef_kelimeler if kelime in aday_kelimeler)

        if skor > en_yuksek_skor:
            en_yuksek_skor = skor
            en_iyi_eslesen = uni

    if en_yuksek_skor == 0:
        return None
    return en_iyi_eslesen

def find_university_website(university_name):
    hedef = normalize(university_name)
    for uni in universities_data:
        aday = normalize(uni.get("name", ""))
        if hedef in aday or aday in hedef:
            return uni.get("web", "Resmi web sitesi bulunamadı")
    return "Resmi web sitesi bulunamadı"

def make_clickable(link):
    if link.startswith("http"):
        return link
    else:
        return "http://" + link

def print_university_details(uni):
    print("\n📚 Üniversite Detayları:")
    print(f"🏫 Adı: {uni.get('name', 'Bilinmiyor')}")
    print(f"📍 Adres: {uni.get('address', 'Bilinmiyor')}")
    print(f"📞 Telefon: {uni.get('phone', 'Bilinmiyor')}")
    print(f"📠 Fax: {uni.get('fax', 'Bilinmiyor')}")
    print(f"✉️ E-posta: {uni.get('email', 'Bilinmiyor')}")
    print(f"🌐 Web: {make_clickable(uni.get('web', ''))}")
    print(f"👨‍🎓 Rektör: {uni.get('warden', 'Bilinmiyor')}\n")

# Başlangıç
print("🎓 Üniversite Tercih Asistanına Hoş Geldin!")
print("🤖 Sohbete başlayabilirsin. (Çıkmak için: q / Sıfırlamak için: reset)\n")

while True:
    mesaj = input("👤 Sen: ").strip().lower()

    if mesaj in ["q", "quit", "exit"]:
        print("👋 Görüşmek üzere!")
        break

    if mesaj in ["reset", "sıfırla", "baştan başla"]:
        session = {}
        print("🔄 Hafıza sıfırlandı. Baştan başlayalım!")
        continue

    analiz = analyze_user_message(mesaj)

    if "hata" in analiz:
        print(f"⚠️ GPT Hatası: {analiz['hata']}")
        continue

    for k in ["sınava_girdi", "puan_turu", "ilgi_alani", "siralama", "sehirler"]:
        if k == "sehirler":
            val = analiz.get("sehirler")
            temiz = []

            if isinstance(val, list):
                temiz = [v.lower().strip() for v in val]
            elif isinstance(val, str):
                temiz = [val.lower().strip()]
            elif val is None and mesaj in ["hayır", "yok", "istemiyorum", "farketmez", "önemli değil"]:
                temiz = [mesaj]

            sehir_red_kelimeleri = [
                "hayır", "yok", "boş", "önemli değil", "farketmez",
                "istemiyorum", "istemem", "hiçbiri", "şehir seçmek istemiyorum"
            ]

            if any(v in sehir_red_kelimeleri for v in temiz):
                session["sehirler"] = "yok"
            elif temiz:
                session["sehirler"] = temiz
        elif analiz.get(k) is not None:
            session[k] = analiz[k]

    eksik = []

    if "sınava_girdi" not in session:
        eksik.append("sınava_girdi")
    elif session.get("sınava_girdi") == True:
        for key in ["puan_turu", "siralama", "ilgi_alani"]:
            if key not in session:
                eksik.append(key)
    elif session.get("sınava_girdi") == False:
        if "ilgi_alani" not in session:
            eksik.append("ilgi_alani")

    if (
        "sehirler" not in session or
        (session.get("sehirler") not in ["yok"] and not session.get("sehirler"))
    ):
        eksik.append("sehirler")

    if eksik:
        sorular = {
            "sınava_girdi": "🎯 Üniversite sınavına girdin mi?",
            "puan_turu": "📊 Puan türün nedir? (SAY, EA, SÖZ, DİL)",
            "siralama": "📈 Başarı sıranı belirtir misin?",
            "ilgi_alani": "🧠 Hangi bölümlere ilgin var? (örnek: hukuk, bilgisayar)",
            "sehirler": "📍 Tercih etmek istediğin şehirler var mı? (örnek: İstanbul, Ankara — boş bırakabilirsin)"
        }
        print(f"🤖 {sorular[eksik[0]]}")
        continue

    siralama_kullanici = (
        float(session["siralama"]) if isinstance(session.get("siralama"), (int, float)) else None
    )
    sehir_filtresi = None if session.get("sehirler") == "yok" else session.get("sehirler")

    tercihler = filtrele_json_programlar(
        puan_turu=session.get("puan_turu"),
        ilgi_alani=session.get("ilgi_alani"),
        siralama_kullanici=siralama_kullanici,
        sehirler=sehir_filtresi
    )

    if tercihler:
        print("\n🎓 Sana uygun bazı bölümler (sıralamaya göre):")
        for i, t in enumerate(tercihler, 1):
            uni_adi_norm = normalize(t['üniversite'])
            video_link = next(
                (
                    url for title, url in uni_video_links.items()
                    if uni_adi_norm in normalize(title)
                ),
                "Tanıtım videosu bulunamadı"
            )
            web_link = find_university_website(t['üniversite'])
            web_link = make_clickable(web_link)

            print(f"{i}. {t['üniversite']} – {t['bölüm']} ({t['şehir']})")
            print(f"   🎯 Sıralama: {t['sıralama']} | 📊 Puan: {t['puan']} | 🎓 Burs: {t['burs']}")
            print(f"   🎥 Tanıtım Videosu: {video_link}")
            print(f"   🌐 Resmi Web Sitesi: {web_link}\n")

        detay_iste = input("💬 Detaylı bilgi almak istediğiniz bir üniversite var mı? (Yoksa boş bırakın): ").strip()
        if detay_iste:
            detay_bilgi = find_university_details(detay_iste)
            if detay_bilgi:
                print_university_details(detay_bilgi)
            else:
                print("❗ İstediğiniz üniversite bulunamadı. İsim doğru mu kontrol eder misiniz?")

    else:
        print("🤔 Hmm... Şu an için uygun bir bölüm bulamadım. İstersen farklı bir ilgi alanı veya şehir söyleyebilirsin.")

    print("\n💬 Yeni bir şey yazabilir veya 'reset' ile yeniden başlayabilirsin. 'q' ile çıkabilirsin.\n")
