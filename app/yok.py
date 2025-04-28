import os
import json
import unicodedata
import re

# ✅ normalize() fonksiyonu – Türkçe harf düzeltmeli
def normalize(text):
    text = unicodedata.normalize("NFKD", text).encode("ASCII", "ignore").decode()
    text = text.replace("ı", "i")
    text = text.upper()
    text = re.sub(r"[^A-ZÇGIOSU ]+", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

# ✅ filtrele_json_programlar() fonksiyonu – çoklu ilgi alanı + başarı sırası + şehir + öğretmenlik kökü + boş sıralama kontrolü
def filtrele_json_programlar(puan_turu: str = None, ilgi_alani: str = "", siralama_kullanici: float = None, sehirler: list = None, sinava_girdi: bool = True):
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data.json')

    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not ilgi_alani:
        return []

    # ✅ ilgi alanı çoklu bölme (ve, and, virgül)
    ilgi_raw = ilgi_alani.lower().replace(" ve ", ",").replace(" and ", ",")
    ilgi_kelimeler = [normalize(k.strip()) for k in ilgi_raw.split(",") if k.strip()]
    
    sehirler = [normalize(s) for s in sehirler] if sehirler else None
    uygunlar = []
    puan_turleri = ["say", "ea", "söz", "dil"] if puan_turu is None else [puan_turu.lower()]

    for uni in data.values():
        if sehirler and normalize(uni["sehir"]) not in sehirler:
            continue

        for tur in puan_turleri:
            bolumler = uni.get(tur, [])
            for bolum in bolumler:
                bolum_adi = normalize(bolum.get("bolumAdi", ""))
                
                eşleşti = False
                for ilgi in ilgi_kelimeler:
                    if ilgi:
                        if ilgi == "OGRETMENLIK":
                            if "OGRETMEN" in bolum_adi:
                                eşleşti = True
                                break
                        else:
                            if (f" {ilgi} " in f" {bolum_adi} " or bolum_adi.startswith(ilgi + " ") or bolum_adi.endswith(" " + ilgi) or bolum_adi == ilgi):
                                eşleşti = True
                                break

                if eşleşti:
                    try:
                        siralama = float(bolum["siralama"].replace(".", "").replace(",", "."))
                    except:
                        siralama = None

                    if siralama is None:
                        continue

                    if sinava_girdi:
                        if siralama_kullanici:
                            alt = siralama_kullanici * 0.8
                            ust = siralama_kullanici * 1.2
                            if not (alt <= siralama <= ust):
                                continue
                    else:
                        if siralama > 100000:
                            continue

                    uygunlar.append({
                        "üniversite": uni["uniAdi"],
                        "bölüm": bolum["bolumAdi"],
                        "puan": bolum["puan"],
                        "sıralama": bolum["siralama"],
                        "siralama_float": siralama,
                        "burs": bolum["burs"],
                        "şehir": uni["sehir"]
                    })


    # 🔥 En iyi bölümler (küçük sıralama) en üstte olacak şekilde sırala
    uygunlar.sort(key=lambda x: x["siralama_float"] if x["siralama_float"] is not None else float("inf"))
    return uygunlar[:24]
