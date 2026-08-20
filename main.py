# main.py
import os
import logging
from datetime import datetime, timezone, timedelta
from flask import Flask, request, jsonify

from astro_calc import get_coordinates, calculate_chart, calculate_current_transits
from database import (
    get_cached_chart, 
    save_chart_cache, 
    generate_chart_hash, 
    get_cached_ai_report, 
    save_cached_ai_report
)
from ai_service import (
    analyze_natal_7_categories,
    analyze_transit_qa,
    analyze_deep_report  # แก้ไขชื่อให้ตรงตาม ai_service.py
)

logging.basicConfig(level=logging.INFO)
app = Flask(__name__, static_folder='.', static_url_path='')

@app.errorhandler(Exception)
def handle_all_exceptions(e):
    app.logger.error(f"Server Error: {str(e)}")
    return jsonify({"status": "error", "message": f"Python Exception: {str(e)}"}), 500

@app.route('/')
def index():
    return app.send_static_file('index.html')

# 1. Real-time Transits Endpoint
@app.route('/transit', methods=['GET'])
def get_transit():
    transits = calculate_current_transits()
    return jsonify({"status": "success", "transits": transits})

# 2. Birth Chart Engine Endpoint
@app.route('/calculate_chart', methods=['POST'])
def calculate_chart_endpoint():
    data = request.get_json() or {}
    day = int(data.get('day', 1))
    month = int(data.get('month', 1))
    year_be = int(data.get('year', 2538))
    year_ad = year_be - 543 if year_be > 2400 else year_be
    hour = int(data.get('hour', 0))
    minute = int(data.get('minute', 0))
    location_name = data.get('location_name') or 'กรุงเทพมหานคร'

    user_key = f"{year_ad}-{month}-{day}_{hour}:{minute}_{location_name}"
    cached = get_cached_chart(user_key)
    
    if cached:
        transits = calculate_current_transits()
        return jsonify({
            "status": "success", 
            "birth_chart_degrees": cached["birth_chart_degrees"], 
            "ruler_mapping": cached["ruler_mapping"], 
            "transit_degrees": transits
        })

    lat, lon, _ = get_coordinates(location_name)
    tz_th = timezone(timedelta(hours=7))
    birth_dt_local = datetime(year_ad, month, day, hour, minute, tzinfo=tz_th)
    birth_dt_utc = birth_dt_local.astimezone(timezone.utc)

    chart_data = calculate_chart(birth_dt_utc, lat, lon)
    save_chart_cache(user_key, chart_data["birth_chart_degrees"], chart_data["ruler_mapping"])
    
    return jsonify({"status": "success", **chart_data})

# 3. AI Analysis & Cache Dispatcher Endpoint
@app.route('/analyze_ai', methods=['POST'])
def analyze_ai_endpoint():
    data = request.get_json() or {}
    user_name = data.get('user_name') or 'คุณ'
    report_type = data.get('report_type') or 'natal_7'
    chart_data = data.get('chart_data')
    question = data.get('question')

    if not chart_data:
        return jsonify({"status": "error", "message": "Missing chart data"}), 400

    # สร้าง Cache Key
    chart_hash = generate_chart_hash(chart_data)
    if report_type == 'transit_qa':
        today_str = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        cache_key = f"{chart_hash}_{today_str}_{question}"
    else:
        cache_key = f"{chart_hash}_{report_type}"

    # ดึงผลวิเคราะห์จาก Cache ถ้ามีอยู่แล้ว
    cached_response = get_cached_ai_report(cache_key, report_type)
    if cached_response:
        return jsonify(cached_response)

    # ประมวลผลผ่าน AI Service หากยังไม่มี Cache
    if report_type == 'transit_qa':
        answer = analyze_transit_qa(user_name, str(question).strip(), chart_data)
        response_data = {"status": "success", "type": "transit_qa", "question": question, "answer": answer}
    
    elif report_type == 'deep_report':
        result = analyze_deep_report(user_name, chart_data)
        response_data = {
            "status": "success", 
            "type": "deep_report", 
            "report": result["report"],
            "radar_data": result["radar_data"],
            "bar_data": result["bar_data"]
        }
    
    else: # natal_7
        report_text = analyze_natal_7_categories(user_name, chart_data)
        response_data = {"status": "success", "type": "natal_7", "report": report_text}

    save_cached_ai_report(cache_key, report_type, response_data)
    return jsonify(response_data)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
