import json
import os
import logging
import traceback
from datetime import datetime, timezone, timedelta
from flask import Flask, request, jsonify

from astro_calc import get_coordinates, calculate_chart, calculate_current_transits
from ai_service import (
    analyze_natal_7_categories,
    analyze_transit_qa,
    analyze_deep_report_json
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AstroBackend")

app = Flask(__name__, static_folder='.', static_url_path='')

RULES_FILE = 'school_rules.json'

def load_school_rules():
    if os.path.exists(RULES_FILE):
        try:
            with open(RULES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Error loading rules: {e}")
    return {"school_name": "สำนักโหราศาสตร์วิวัฒนาการ", "natal_categories": {}}

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"status": "error", "message": "Endpoint Not Found (404)"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"status": "error", "message": "Internal Server Error (500)"}), 500

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/transit', methods=['GET'])
def get_transit():
    try:
        transits = calculate_current_transits()
        return jsonify({
            "status": "success",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "transits": transits
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# 📌 Endpoint จังหวะที่ 1: คำนวณองศาดาว + วาด SVG Wheel ส่งกลับทันที (<100ms)
@app.route('/calculate_chart', methods=['POST'])
def calculate_chart_endpoint():
    try:
        data = request.get_json() or {}
        day = int(data.get('day', 1))
        month = int(data.get('month', 1))
        year_be = int(data.get('year', 2538))
        year_ad = year_be - 543 if year_be > 2400 else year_be
        hour = int(data.get('hour', 0))
        minute = int(data.get('minute', 0))
        location_name = data.get('location_name') or 'กรุงเทพมหานคร'

        lat, lon, _ = get_coordinates(location_name)
        tz_thailand = timezone(timedelta(hours=7))
        birth_dt_local = datetime(year_ad, month, day, hour, minute, tzinfo=tz_thailand)
        birth_dt_utc = birth_dt_local.astimezone(timezone.utc)

        chart_data = calculate_chart(birth_dt_utc, lat, lon)
        return jsonify({
            "status": "success",
            "birth_chart_degrees": chart_data["birth_chart_degrees"],
            "transit_degrees": chart_data["transit_degrees"],
            "ruler_mapping": chart_data["ruler_mapping"],
            "chart_svg": chart_data["chart_svg"]
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# 📌 Endpoint จังหวะที่ 2: วิเคราะห์บทแปล AI (7 หมวดหมู่ หรือ Transit Q&A)
@app.route('/analyze_ai', methods=['POST'])
def analyze_ai_endpoint():
    try:
        data = request.get_json() or {}
        user_name = data.get('user_name') or 'คุณ'
        question = data.get('question')
        chart_data = data.get('chart_data')

        if not chart_data:
            return jsonify({"status": "error", "message": "Missing chart data"}), 400

        school_rules = load_school_rules()

        if question and str(question).strip():
            qa_answer = analyze_transit_qa(user_name, str(question).strip(), chart_data)
            return jsonify({
                "status": "success",
                "type": "transit_qa",
                "question": question,
                "answer": qa_answer
            })

        report_text = analyze_natal_7_categories(user_name, chart_data, school_rules)
        return jsonify({
            "status": "success",
            "type": "natal_7_categories",
            "report": report_text
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# 📌 Endpoint สำหรับเจาะลึก 12 เรือนชะตา
@app.route('/deep_report', methods=['POST'])
def deep_report_endpoint():
    try:
        data = request.get_json() or {}
        user_name = data.get('user_name') or 'คุณ'
        chart_data = data.get('chart_data')

        if not chart_data:
            return jsonify({"status": "error", "message": "Missing chart data"}), 400

        school_rules = load_school_rules()
        deep_report_res = analyze_deep_report_json(user_name, chart_data, school_rules)
        return jsonify({
            "status": "success",
            "type": "deep_report",
            "report": deep_report_res
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
