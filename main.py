# main.py
import os
import logging
logging.basicConfig(level=logging.INFO)
from database import get_cached_chart, save_chart_cache, generate_chart_hash, get_cached_ai_report, save_cached_ai_report
from datetime import datetime, timezone, timedelta
from flask import Flask, request, jsonify

from astro_calc import get_coordinates, calculate_chart, calculate_current_transits
from ai_service import (
    analyze_natal_7_categories,
    analyze_transit_qa,
    analyze_deep_report_json
)

logging.basicConfig(level=logging.INFO)
app = Flask(__name__, static_folder='.', static_url_path='')

@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error(f"Server Error: {str(e)}")
    return jsonify({
        "status": "error",
        "message": f"Python Exception: {str(e)}"
    }), 500

@app.errorhandler(404)
def handle_404(e):
    return jsonify({"status": "error", "message": "Endpoint Not Found (404)"}), 404

@app.errorhandler(405)
def handle_405(e):
    return jsonify({"status": "error", "message": "Method Not Allowed (405)"}), 405

@app.errorhandler(500)
def handle_500(e):
    return jsonify({"status": "error", "message": "Internal Server Error (500)"}), 500

@app.errorhandler(Exception)
def handle_all(e):
    return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/transit', methods=['GET'])
def get_transit():
    transits = calculate_current_transits()
    return jsonify({"status": "success", "transits": transits})

# จังหวะที่ 1: คำนวณองศาดาว + SVG Wheel
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

    lat, lon, _ = get_coordinates(location_name)
    tz_th = timezone(timedelta(hours=7))
    birth_dt_local = datetime(year_ad, month, day, hour, minute, tzinfo=tz_th)
    birth_dt_utc = birth_dt_local.astimezone(timezone.utc)

    chart_data = calculate_chart(birth_dt_utc, lat, lon)
    return jsonify({"status": "success", **chart_data})

# จังหวะที่ 2: วิเคราะห์บทพยากรณ์ AI (7 หมวดหมู่ หรือ Transit Q&A)
@app.route('/analyze_ai', methods=['POST'])
def analyze_ai_endpoint():
    data = request.get_json() or {}
    user_name = data.get('user_name') or 'คุณ'
    report_type = data.get('report_type') or 'natal_7'
    chart_data = data.get('chart_data')
    question = data.get('question')

    if not chart_data:
        return jsonify({"status": "error", "message": "Missing chart data"}), 400

    # 1. สร้าง Cache Key จากโครงสร้างดวง
    chart_hash = generate_chart_hash(chart_data)
    
    # 2. จัดการ Cache Key ตามประเภทการวิเคราะห์
    if report_type == 'transit_qa':
        # Transit เปลี่ยนทุกวัน และคำถามต่างกัน ต้องเอา วันที่ + คำถาม มาผสมใน Key
        today_str = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        cache_key = f"{chart_hash}_{today_str}_{question}"
    else:
        # พื้นดวง (Natal / Deep Report) ดวงเดิมคำแปลเดิมเสมอ
        cache_key = f"{chart_hash}_{report_type}"

    # 3. เช็ก Database ว่าเคยแปล AI ดวงนี้หรือยัง
    cached_response = get_cached_ai_report(cache_key, report_type)
    if cached_response:
        return jsonify(cached_response)

    # 4. ถ้ายังไม่เคยแปล ค่อยส่งเรียก OpenAI (AI Service)
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

    # 5. บันทึกคำแปล AI ลง Database เพื่อใช้ครั้งต่อไป
    save_cached_ai_report(cache_key, report_type, response_data)

    return jsonify(response_data)


@app.route('/deep_report', methods=['POST'])
def deep_report_endpoint():
    data = request.get_json() or {}
    user_name = data.get('user_name') or 'คุณ'
    chart_data = data.get('chart_data')

    if not chart_data:
        return jsonify({"status": "error", "message": "Missing chart data"}), 400

    deep_report_res = analyze_deep_report_json(user_name, chart_data)
    return jsonify({"status": "success", "type": "deep_report", "report": deep_report_res})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
