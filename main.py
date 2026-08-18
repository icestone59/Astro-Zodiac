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

# 📌 บังคับให้ Flask คืนค่าเป็น JSON เสมอเมื่อเกิด Error ทุกกรณี (แก้ Unexpected token '<')
# บังคับดักจับ Error ทุกชนิดแล้วส่ง Stack Trace กลับเป็น JSON
@app.errorhandler(Exception)
def handle_all_errors(e):
    code = getattr(e, 'code', 500)
    error_trace = traceback.format_exc()
    print(f"❌ SERVER ERROR: {error_trace}") # พิมพ์ลง Render Log
    return jsonify({
        "status": "error",
        "message": str(e),
        "traceback": error_trace,
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

def save_school_rules(data):
    with open(RULES_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/admin')
def admin():
    return app.send_static_file('admin.html')

@app.route('/api/rules', methods=['GET', 'POST'], strict_slashes=False)
def handle_rules():
    if request.method == 'POST':
        data = request.get_json() or {}
        save_school_rules(data)
        return jsonify({"status": "success", "message": "บันทึก Master Rules เรียบร้อย"})
    return jsonify(load_school_rules())

@app.route('/api/calculate', methods=['POST'], strict_slashes=False)
def calculate():
    try:
        data = request.get_json() or {}
        user_name = data.get('user_name') or 'ลูกดวง'
        
        # ป้องกัน ValueError จากค่าว่าง หรือ String ที่แปลงเป็น intไม่ได้
        day = int(data.get('day') or 1)
        month = int(data.get('month') or 1)
        year_be = int(data.get('year') or 2538)
        hour = int(data.get('hour') or 0)
        minute = int(data.get('minute') or 0)
        
        year_ad = year_be - 543 if year_be > 2400 else year_be
        user_location = data.get('location') or 'กรุงเทพมหานคร'

        # ค้นหาพิกัด
        lat, lon, city, country = get_coordinates(user_location)
        birth_dt_utc = datetime(year_ad, month, day, hour, minute, tzinfo=timezone.utc)

        # คำนวณ Chart Data
        school_rules = load_school_rules()
        chart_data = calculate_chart(birth_dt_utc, lat, lon)

        # AI แปลความหมาย 8 หมวดหมู่
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
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"ประมวลผลล้มเหลว: {str(e)}"
        }), 400

@app.route('/api/transit-qa', methods=['POST'], strict_slashes=False)
def transit_qa():
    """วิเคราะห์ Transit Real-time ร่วมกับ Birth Chart ตอบคำถามเจาะจง"""
    data = request.get_json() or {}
    user_name = data.get('user_name', 'ลูกดวง')
    question = data.get('question', '')
    
    day = int(data.get('day', 1))
    month = int(data.get('month', 1))
    year_be = int(data.get('year', 2538))
    year_ad = year_be - 543 if year_be > 2400 else year_be
    hour = int(data.get('hour', 0))
    minute = int(data.get('minute', 0))
    user_location = data.get('location', 'กรุงเทพมหานคร')

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
