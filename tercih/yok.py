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

# ✅ Bölüm filtreleme fonksiyonu (otomatik sıralama genişlemeli)
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
    puan_turleri = ["say", "ea", "söz", "dil"] if puan_turu is None else [puan_turu.lower()]

    # Özel eşleşme listesi
    ozel_eslesmeler = {
        "YAZILIM": ["YAZILIM", "BILGISAYAR", "YAZILIM MUHENDISLIGI", "BILGISAYAR MUHENDISLIGI"],
        "BILGISAYAR": ["BILGISAYAR", "YAZILIM", "BILGISAYAR MUHENDISLIGI", "YAZILIM MUHENDISLIGI"],
        "DIS": ["DIS", "DIS HEKIMLIGI", "DISHEKIMLIGI", "DISH"]  # yeni eklenen
    }

    # 🔁 Sıralama aralığını otomatik artır
    if sinava_girdi and siralama_kullanici:
        alt = siralama_kullanici * 0.9
        ust_baslangic = siralama_kullanici * 2
        ust_max = siralama_kullanici * 3
        ust_artim = siralama_kullanici * 0.25
        deneme_ust = ust_baslangic
        filtrelenmis = []

        while deneme_ust <= ust_max:
            filtrelenmis.clear()
            for uni in data.values():
                if sehirler:
                    uni_sehir_norm = normalize(uni["sehir"])
                    if not any(sehir in uni_sehir_norm for sehir in sehirler):
                        continue

                for tur in puan_turleri:
                    bolumler = uni.get(tur, [])
                    for bolum in bolumler:
                        bolum_adi = normalize(bolum.get("bolumAdi", ""))
                        
                        eşleşti = False
                        for ilgi in ilgi_kelimeler:
                            if ilgi == "OGRETMENLIK" and "OGRETMEN" in bolum_adi:
                                eşleşti = True
                                break
                            elif ilgi == "MUHENDISLIK" and "MUHENDIS" in bolum_adi:
                                eşleşti = True
                                break
                            elif ilgi == "DIS":
                                if "DIS" in bolum_adi and "HEKIM" in bolum_adi:
                                    eşleşti = True
                                    break
                            elif ilgi in ozel_eslesmeler:
                                if any(k in bolum_adi for k in ozel_eslesmeler[ilgi]):
                                    eşleşti = True
                                    break
                            elif ilgi in bolum_adi:
                                eşleşti = True
                                break
                        if not eşleşti:
                            continue

                        try:
                            siralama = float(bolum["siralama"].replace(".", "").replace(",", "."))
                        except:
                            continue

                        if siralama < alt or siralama > deneme_ust:
                            continue

                        filtrelenmis.append({
                            "üniversite": uni["uniAdi"],
                            "bölüm": bolum["bolumAdi"],
                            "puan": bolum["puan"],
                            "sıralama": bolum["siralama"],
                            "siralama_float": siralama,
                            "burs": bolum["burs"],
                            "şehir": uni["sehir"]
                        })

            if len(filtrelenmis) >= 24:
                break
            deneme_ust += ust_artim

        filtrelenmis.sort(key=lambda x: x["siralama_float"] if x["siralama_float"] is not None else float("inf"))
        return filtrelenmis[:24]

    # 🟡 Sınava girmediyse veya sıralama yoksa: sıralamasız filtreleme
    uygunlar = []

    for uni in data.values():
        if sehirler:
            uni_sehir_norm = normalize(uni["sehir"])
            if not any(sehir in uni_sehir_norm for sehir in sehirler):
                continue

        for tur in puan_turleri:
            bolumler = uni.get(tur, [])
            for bolum in bolumler:
                bolum_adi = normalize(bolum.get("bolumAdi", ""))

                eşleşti = False
                for ilgi in ilgi_kelimeler:
                    if ilgi == "OGRETMENLIK" and "OGRETMEN" in bolum_adi:
                        eşleşti = True
                        break
                    elif ilgi == "MUHENDISLIK" and "MUHENDIS" in bolum_adi:
                        eşleşti = True
                        break
                    elif ilgi in ozel_eslesmeler:
                        if any(k in bolum_adi for k in ozel_eslesmeler[ilgi]):
                            eşleşti = True
                            break
                    elif ilgi in bolum_adi:
                        eşleşti = True
                        break

                if not eşleşti:
                    continue

                try:
                    siralama = float(bolum["siralama"].replace(".", "").replace(",", "."))
                except:
                    continue

                if sinava_girdi == False and siralama > 100000:
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

    uygunlar.sort(key=lambda x: x["siralama_float"] if x["siralama_float"] is not None else float("inf"))
    return uygunlar[:24]
