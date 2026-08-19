import json
import os
import traceback
from datetime import datetime, timezone, timedelta
from flask import Flask, request, jsonify

from astro_calc import get_coordinates, calculate_chart, calculate_current_transits
from ai_service import (
    analyze_natal_7_categories,
    analyze_transit_qa,
    analyze_deep_report_json
)

app = Flask(__name__, static_folder='.', static_url_path='')

RULES_FILE = 'school_rules.json'

def load_school_rules():
    if os.path.exists(RULES_FILE):
        try:
            with open(RULES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {"school_name": "สำนักโหราศาสตร์วิวัฒนาการ", "natal_categories": {}}

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/admin')
def admin():
    return app.send_static_file('admin.html')

@app.route('/transit', methods=['GET'])
def get_transit():
    """ดึงข้อมูลดาวจร Real-time ล่าสุด"""
    try:
        transits = calculate_current_transits()
        return jsonify({"status": "success", "transits": transits})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json() or {}
        user_name = data.get('user_name') or 'คุณ'
        day = int(data.get('day', 1))
        month = int(data.get('month', 1))
        year_ad = int(data.get('year', 1995))
        hour = int(data.get('hour', 0))
        minute = int(data.get('minute', 0))
        location_name = data.get('location_name') or 'กรุงเทพมหานคร'
        question = data.get('question')

        lat, lon, _ = get_coordinates(location_name)

        # 📌 แก้ไขจุดนี้: กำหนดเป็นเวลาไทย (UTC+7) แล้วแปลงเป็น UTC อัตโนมัติ
        tz_thailand = timezone(timedelta(hours=7))
        birth_dt_local = datetime(year_ad, month, day, hour, minute, tzinfo=tz_thailand)
        birth_dt_utc = birth_dt_local.astimezone(timezone.utc) # จะถูกปรับเป็น 03:51 UTC อัตโนมัติ

        chart_data = calculate_chart(birth_dt_utc, lat, lon)
        school_rules = load_school_rules()

        if question and str(question).strip():
            qa_answer = analyze_transit_qa(user_name, question, chart_data)
            return jsonify({
                "status": "success",
                "question": question,
                "answer": qa_answer,
                "birth_chart_degrees": chart_data["birth_chart_degrees"],
                "transit_degrees": chart_data["transit_degrees"],
                "chart_svg": chart_data["chart_svg"]
            })

        report_text = analyze_natal_7_categories(user_name, chart_data, school_rules)
        return jsonify({
            "status": "success",
            "report": report_text,
            "birth_chart_degrees": chart_data["birth_chart_degrees"],
            "transit_degrees": chart_data["transit_degrees"],
            "chart_svg": chart_data["chart_svg"]
        })

    except Exception as e:
        tb = traceback.format_exc()
        print(f"❌ ANALYZE ERROR:\n{tb}")
        return jsonify({"detail": str(e)}), 500

@app.route('/generate-report', methods=['POST'])
def generate_report():
    """สร้างรายงาน Deep Report เจาะลึก 12 มิติ ใน Tab ใหม่"""
    try:
        data = request.get_json() or {}
        user_name = data.get('user_name') or 'คุณไอซ์'
        day = int(data.get('day', 1))
        month = int(data.get('month', 1))
        year_ad = int(data.get('year', 1995))
        hour = int(data.get('hour', 0))
        minute = int(data.get('minute', 0))
        location_name = data.get('location_name') or 'กรุงเทพมหานคร'

        lat, lon, _ = get_coordinates(location_name)
        birth_dt_utc = datetime(year_ad, month, day, hour, minute, tzinfo=timezone.utc)
        chart_data = calculate_chart(birth_dt_utc, lat, lon)
        school_rules = load_school_rules()

        deep_report = analyze_deep_report_json(user_name, chart_data, school_rules)

        html_response = f"""
        <!DOCTYPE html>
        <html lang="th">
        <head>
            <meta charset="UTF-8">
            <title>รายงานเจาะลึกปมชีวิต 12 มิติ - {user_name}</title>
            <style>
                body {{ font-family: sans-serif; background: #0f172a; color: #f8fafc; padding: 40px; line-height: 1.8; }}
                .container {{ max-width: 900px; margin: 0 auto; background: #1e293b; padding: 30px; border-radius: 16px; border: 1px solid #475569; }}
                h1 {{ color: #c084fc; border-bottom: 2px solid #7c3aed; padding-bottom: 10px; }}
                .content {{ white-space: pre-wrap; margin-top: 20px; font-size: 1rem; color: #e2e8f0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🔮 รายงานเจาะลึกปมชีวิตพัฒนาศักยภาพ: {user_name}</h1>
                <div class="content">{deep_report}</div>
            </div>
        </body>
        </html>
        """
        return html_response
    except Exception as e:
        return f"<h2>เกิดข้อผิดพลาดในการสร้างรายงาน: {str(e)}</h2>", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
