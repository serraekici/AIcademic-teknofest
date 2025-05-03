from datetime import datetime

def clean_exam_text(ocr_text):
    lines = ocr_text.splitlines()
    dersler = []
    tarihler = []

    for line in lines:
        line = line.strip()
        if line and not any(anahtar in line for anahtar in ["DERS", "TARİH", "SAAT", "KAMP", ":"]):
            if "-" in line and ":" in line:
                # Örn: 22.03.2025 - 09:00 - 10:50 → sadece tarihi al
                date_part = line.split("-")[0].strip()
                tarihler.append(date_part)
            elif line:
                dersler.append(line)

    # Eşleştir
    exam_pairs = []
    for i in range(min(len(dersler), len(tarihler))):
        try:
            date = datetime.strptime(tarihler[i], "%d.%m.%Y")
            formatted = date.strftime("%d %B %Y")  # Windows kullanıyorsan: "%d %B %Y"
        except:
            formatted = tarihler[i]

        exam_pairs.append(f"{formatted} – {dersler[i]}")

    return "\n".join(exam_pairs)
