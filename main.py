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
        year_be = int(data.get('year', 2538))
        year_ad = year_be - 543 if year_be > 2400 else year_be
        
        hour = int(data.get('hour', 0))
        minute = int(data.get('minute', 0))
        location_name = data.get('location_name') or 'กรุงเทพมหานคร'
        question = data.get('question')

        lat, lon, _ = get_coordinates(location_name)

        # แปลงเวลาท้องถิ่นไทย (UTC+7) ให้เป็น UTC ก่อนส่งคำนวณ
        tz_thailand = timezone(timedelta(hours=7))
        birth_dt_local = datetime(year_ad, month, day, hour, minute, tzinfo=tz_thailand)
        birth_dt_utc = birth_dt_local.astimezone(timezone.utc)

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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
