import json
import os
import traceback
from datetime import datetime, timezone
from flask import Flask, request, jsonify

from astro_calc import get_coordinates, calculate_chart
from ai_service import (
    analyze_natal_7_categories,
    analyze_transit_qa,
    analyze_deep_report_json
)

app = Flask(__name__, static_folder='.', static_url_path='')

RULES_FILE = 'school_rules.json'

# ดักจับ Error ทุกประเภท และคืนค่าเป็น JSON พร้อม Traceback เสมอ (ป้องกัน Unexpected token '<')
@app.errorhandler(Exception)
def handle_all_errors(e):
    code = getattr(e, 'code', 500)
    tb = traceback.format_exc()
    print(f"❌ SERVER ERROR TRACEBACK:\n{tb}")
    return jsonify({
        "status": "error",
        "message": str(e),
        "traceback": tb,
        "status_code": code
    }), code

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

@app.route('/api/calculate', methods=['POST'], strict_slashes=False)
def calculate():
    """คำนวณ Birth Chart + Real-time Transit สังเคราะห์ 8 หมวดหมู่พัฒนาศักยภาพ"""
    data = request.get_json() or {}
    user_name = data.get('user_name') or 'ลูกดวง'
    
    day = int(data.get('day') or 1)
    month = int(data.get('month') or 1)
    year_be = int(data.get('year') or 2538)
    year_ad = year_be - 543 if year_be > 2400 else year_be
    hour = int(data.get('hour') or 0)
    minute = int(data.get('minute') or 0)
    user_location = data.get('location') or 'กรุงเทพมหานคร'

    # 1. แปลงพิกัดภูมิศาสตร์
    lat, lon, city, country = get_coordinates(user_location)
    birth_dt_utc = datetime(year_ad, month, day, hour, minute, tzinfo=timezone.utc)

    # 2. คำนวณองศาดาวเกิด + ดาวจร Real-time + Rulers
    school_rules = load_school_rules()
    chart_data = calculate_chart(birth_dt_utc, lat, lon)

    # 3. AI สังเคราะห์พยากรณ์ภาษาคนเชิงจิตวิทยา
    analysis_result = analyze_natal_7_categories(user_name, chart_data, school_rules)

    return jsonify({
        "status": "success",
        "user_info": {
            "name": user_name,
            "location": f"{city}, {country}",
            "latitude": lat,
            "longitude": lon,
            "birth_utc": birth_dt_utc.strftime("%Y-%m-%d %H:%M UTC")
        },
        "chart_data": chart_data,
        "analysis": analysis_result
    })

@app.route('/api/transit-qa', methods=['POST'], strict_slashes=False)
def transit_qa():
    """คำนวณ Transit Real-time vs Natal Chart ตอบคำถามเจาะจง"""
    data = request.get_json() or {}
    user_name = data.get('user_name') or 'ลูกดวง'
    question = data.get('question') or 'ภาพรวมจังหวะชีวิตและกลยุทธ์ทางออก'
    
    day = int(data.get('day') or 1)
    month = int(data.get('month') or 1)
    year_be = int(data.get('year') or 2538)
    year_ad = year_be - 543 if year_be > 2400 else year_be
    hour = int(data.get('hour') or 0)
    minute = int(data.get('minute') or 0)
    user_location = data.get('location') or 'กรุงเทพมหานคร'

    lat, lon, city, country = get_coordinates(user_location)
    birth_dt_utc = datetime(year_ad, month, day, hour, minute, tzinfo=timezone.utc)
    chart_data = calculate_chart(birth_dt_utc, lat, lon)

    qa_result = analyze_transit_qa(user_name, question, chart_data)

    return jsonify({
        "status": "success",
        "question": question,
        "transit_timestamp": chart_data.get("transit_timestamp_utc"),
        "answer": qa_result
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
