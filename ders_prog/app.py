from flask import Flask, render_template, request, redirect
import os, json
from utils.ocr import extract_text_from_image
from utils.filename_cleaner import normalize_filename
from utils.gpt_plan import generate_smart_plan
from dotenv import load_dotenv
from utils.text_cleaner import clean_exam_text


load_dotenv()

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
SESSION_FILE = 'session_data.json'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def save_session(data):
    with open(SESSION_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_session():
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['image']
        filename = normalize_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        ocr_text = extract_text_from_image(filepath)
        print("OCR ÇIKTISI:\n", ocr_text)
        exam_text = clean_exam_text(ocr_text)

        smart_plan = generate_smart_plan(exam_text, start_date="18 Mart")
        save_session({
            "ocr_text": ocr_text,
            "exam_text": exam_text,
            "plan_text": smart_plan
        })

        return redirect('/plan')

    return render_template("index.html")

@app.route('/plan')
def plan():
    data = load_session()
    plan_text = data.get("plan_text", "Plan oluşturulamadı.")
    return render_template("plan.html", plan=plan_text)

@app.route('/today')
def today():
    from utils.gpt_plan import what_to_study_today
    data = load_session()
    plan_text = data.get("plan_text", "")
    suggestion = what_to_study_today(plan_text)
    return f"<h2>📅 Bugünlük Öneri:</h2><pre>{suggestion}</pre><br><a href='/plan'>🔙 Plana Dön</a>"

if __name__ == '__main__':
    app.run(debug=True)
