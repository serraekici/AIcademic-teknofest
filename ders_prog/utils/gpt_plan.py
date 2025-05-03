from openai import OpenAI
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_smart_plan(exam_schedule, start_date="1 Mayıs"):
    system_prompt = """
Sen bir yapay zeka eğitim planlayıcısısın. Kullanıcı sana bir sınav programı verdiğinde aşağıdaki kurallara göre çalışma planı oluşturacaksın:

1. Yakın sınavlara daha çok çalıştır.
2. Aynı gün birden fazla sınav varsa önceki günlerde eşit dağıt.
3. Saat, yemek gibi şeyler yazma. Sade olsun.
4. Format: `1 Mayıs → Fizik`
"""

    user_prompt = f"""
Sınav Programım:
{exam_schedule}

Çalışmalara {start_date} itibarıyla başlıyorum. Planı oluştur.
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    return response.choices[0].message.content

def what_to_study_today(plan_text):
    # Windows için gün formatı: %d (0'sız kullanamaz)
    today = datetime.today().strftime("%d %B %Y")
    prompt = f"Bugün {today}. Aşağıdaki plana göre bugün hangi derse çalışmalıyım?\n\n{plan_text}"
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

