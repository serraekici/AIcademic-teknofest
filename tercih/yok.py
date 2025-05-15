import os
import json
import unicodedata
import re

# ✅ Türkçe karakter temizleyici
def normalize(text):
    text = unicodedata.normalize("NFKD", text).encode("ASCII", "ignore").decode()
    text = text.replace("ı", "i")
    text = text.upper()
    text = re.sub(r"[^A-ZÇGIOSU ]+", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

# ✅ Bölüm filtreleme fonksiyonu
def filtrele_json_programlar(puan_turu: str = None, ilgi_alani: str = "", siralama_kullanici: float = None, sehirler: list = None, sinava_girdi: bool = True):
    data_path = os.path.join(os.path.dirname(__file__), 'data', 'data.json')

    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not ilgi_alani:
        return []

    # Çoklu ilgi alanı ayırma (ve, and, virgül ile)
    ilgi_raw = ilgi_alani.lower().replace(" ve ", ",").replace(" and ", ",")
    ilgi_kelimeler = [normalize(k.strip()) for k in ilgi_raw.split(",") if k.strip()]
    
    # Şehirler normalize ediliyor
    sehirler = [normalize(s) for s in sehirler] if sehirler else None
    uygunlar = []
    puan_turleri = ["say", "ea", "söz", "dil"] if puan_turu is None else [puan_turu.lower()]

    # Özel eşleşme listesi – yazılım gibi kelimeler daha geniş aranır
    ozel_eslesmeler = {
        "YAZILIM": ["YAZILIM", "BILGISAYAR", "YAZILIM MUHENDISLIGI", "BILGISAYAR MUHENDISLIGI"],
        "BILGISAYAR": ["BILGISAYAR", "YAZILIM", "BILGISAYAR MUHENDISLIGI", "YAZILIM MUHENDISLIGI"]
    }

    for uni in data.values():
        # ✅ Şehir filtresi daha esnek: İSTANBUL (ÜSKÜDAR) gibi varyasyonlar eşleşir
        if sehirler:
            uni_sehir_norm = normalize(uni["sehir"])
            if not any(sehir in uni_sehir_norm for sehir in sehirler):
                continue

        for tur in puan_turleri:
            bolumler = uni.get(tur, [])
            for bolum in bolumler:
                bolum_adi = normalize(bolum.get("bolumAdi", ""))
                
                # 🔍 İlgi alanı eşleşmesi
                eşleşti = any(
                    (
                        "OGRETMEN" in bolum_adi if ilgi == "OGRETMENLIK" else
                        any(kelime in bolum_adi for kelime in ozel_eslesmeler.get(ilgi, [ilgi]))
                    )
                    for ilgi in ilgi_kelimeler if ilgi
                )

                if not eşleşti:
                    continue

                # 🔍 Başarı sırası ve filtre
                try:
                    siralama = float(bolum["siralama"].replace(".", "").replace(",", "."))
                except:
                    siralama = None

                if siralama is None:
                    continue

                uygun = True

                if sinava_girdi and siralama_kullanici:
                    alt = siralama_kullanici * 0.8
                    ust = siralama_kullanici * 1.2
                    if not (alt <= siralama <= ust):
                        uygun = False
                elif not sinava_girdi and siralama > 100000:
                    uygun = False

                if uygun:
                    uygunlar.append({
                        "üniversite": uni["uniAdi"],
                        "bölüm": bolum["bolumAdi"],
                        "puan": bolum["puan"],
                        "sıralama": bolum["siralama"],
                        "siralama_float": siralama,
                        "burs": bolum["burs"],
                        "şehir": uni["sehir"]
                    })

    # ✅ En iyi sıralamaya göre sırala ve ilk 24 bölümü döndür
    uygunlar.sort(key=lambda x: x["siralama_float"] if x["siralama_float"] is not None else float("inf"))
    return uygunlar[:24]
