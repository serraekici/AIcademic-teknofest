from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv() 
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_smart_plan(ocr_text, start_date, end_date):
    prompt = f"""
OCR çıktısından elde edilen sınav programı aşağıdadır. Bu metinden hangi derslerin olduğunu sen çıkar ve {start_date} - {end_date} tarihleri arasında ders çalışma planı hazırla.

📝 OCR Metni:
{ocr_text}

🎯 Kurallar:
- Ders isimlerini sen belirle.
- Zor dersleri erkene koy.
- Her gün 2-3 konu yaz.
- Plan sade metin olsun.
- Girişte motivasyon verici bir cümle olabilir.

Plan:
"""
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content
