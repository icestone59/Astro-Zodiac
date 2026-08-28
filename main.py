# main.py - Evolutionary & Uranian Astrology Engine Server
import os
import logging
import traceback
from datetime import datetime, timezone, timedelta
from flask import Flask, request, jsonify, send_from_directory

from astro_calc import (
    get_coordinates, 
    calculate_chart, 
    calculate_current_transits
)
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
    analyze_deep_report
)

logging.basicConfig(level=logging.INFO)

# กำหนด Root Directory สำหรับ Static Files ให้รัดกุม
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=BASE_DIR, static_url_path='')

# main.py - Handling Cache Bypass for Dev Testing
bypass_cache = data.get('bypass_cache', False)

if bypass_cache:
    cached_response = None  # บังคับยิง OpenAI API ใหม่เพื่อตรวจ Prompt
else:
    cached_response = get_cached_ai_report(cache_key, report_type)[cite: 1]
# ------------------------------------------------------------------
# Page & Static Routes (ป้องกัน 404 Not Found)
# ------------------------------------------------------------------
@app.route('/')
def index():
    return send_from_directory(BASE_DIR, 'index.html')

@app.route('/deepreport')
def deep_report_page():
    return send_from_directory(BASE_DIR, 'deepreport.html')

# ------------------------------------------------------------------
# Global Error Handler & Terminal Debug Logger
# ------------------------------------------------------------------
@app.errorhandler(Exception)
def handle_all_exceptions(e):
    tb_str = traceback.format_exc()
    app.logger.error(f"[SYSTEM EXCEPTION]:\n{tb_str}")
    
    # ส่งรายละเอียด Error ออกเป็น JSON เพื่อให้ Frontend แสดง Terminal Debug Log
    return jsonify({
        "status": "error",
        "error_type": type(e).__name__,
        "message": str(e),
        "traceback": tb_str
    }), 500

# ------------------------------------------------------------------
# API Endpoints
# ------------------------------------------------------------------

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
    mode = data.get('mode') or 'client'

    if not chart_data:
        return jsonify({"status": "error", "message": "ไม่พบข้อมูลดวงชะตา (Missing chart_data)"}), 400

    # สร้าง Cache Key จากองศาดวงกำเนิดหลัก
    birth_degrees = chart_data.get("birth_chart_degrees", {})
    birth_key_raw = f"{birth_degrees.get('ASC', {}).get('degree_raw')}_{birth_degrees.get('Sun', {}).get('degree_raw')}"
    chart_hash = generate_chart_hash({"birth": birth_key_raw})

    if report_type == 'transit_qa':
        today_str = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        cache_key = f"{chart_hash}_{today_str}_{str(question).strip()}_{mode}"
    else:
        cache_key = f"{chart_hash}_{report_type}_{mode}"

    cached_response = get_cached_ai_report(cache_key, report_type)
    if cached_response:
        app.logger.info(f"[DB CACHE HIT]: {cache_key}")
        return jsonify(cached_response)

    app.logger.info(f"[DB CACHE MISS]: Calling OpenAI API for {cache_key}")

    if report_type == 'transit_qa':
        answer = analyze_transit_qa(user_name, str(question).strip(), chart_data, mode=mode)
        response_data = {"status": "success", "type": "transit_qa", "question": question, "answer": answer}
    elif report_type == 'deep_report':
        result = analyze_deep_report(user_name, chart_data, mode=mode)
        response_data = {
            "status": "success", 
            "type": "deep_report", 
            "report": result["report"],
            "radar_data": result["radar_data"],
            "bar_data": result["bar_data"]
        }
    else:
        report_text = analyze_natal_7_categories(user_name, chart_data, mode=mode)
        response_data = {"status": "success", "type": "natal_7", "report": report_text}

    save_cached_ai_report(cache_key, report_type, response_data)
    return jsonify(response_data)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
