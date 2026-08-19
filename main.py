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

# ตั้งค่า Logging ละเอียดระดับ DEBUG ลงระบบ Console ของ Render
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s'
)
logger = logging.getLogger("AstroApp")

app = Flask(__name__, static_folder='.', static_url_path='')

RULES_FILE = 'school_rules.json'

def load_school_rules():
    if os.path.exists(RULES_FILE):
        try:
            with open(RULES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load school_rules.json: {e}")
    return {"school_name": "สำนักโหราศาสตร์วิวัฒนาการ", "natal_categories": {}}

# ==========================================
# JSON Error Handlers (ป้องกันเซิร์ฟเวอร์คายหน้า HTML)
# ==========================================
@app.errorhandler(404)
def not_found_error(error):
    logger.error(f"404 Error: Path '{request.path}' not found.")
    return jsonify({
        "status": "error",
        "message": f"Endpoint '{request.path}' ไม่พบในระบบ (404 Not Found)"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"500 Internal Error: {error}")
    return jsonify({
        "status": "error",
        "message": "เกิดข้อผิดพลาดภายในเซิร์ฟเวอร์ (500 Internal Error)"
    }), 500

@app.errorhandler(Exception)
def handle_unexpected_error(error):
    tb = traceback.format_exc()
    logger.error(f"❌ UNHANDLED EXCEPTION:\n{tb}")
    return jsonify({
        "status": "error",
        "error_type": type(error).__name__,
        "detail": str(error),
        "traceback": tb
    }), 500


# ==========================================
# Routes & Endpoints
# ==========================================
@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.route('/transit', methods=['GET'])
def get_transit():
    try:
        logger.info("Fetching real-time transit data...")
        transits = calculate_current_transits()
        return jsonify({
            "status": "success",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "transits": transits
        })
    except Exception as e:
        logger.error(f"Transit endpoint failed: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json() or {}
        logger.debug(f"Received /analyze Payload: {data}")

        user_name = data.get('user_name') or 'คุณ'
        day = int(data.get('day', 1))
        month = int(data.get('month', 1))
        
        year_input = int(data.get('year', 2538))
        year_ad = year_input - 543 if year_input > 2400 else year_input
        
        hour = int(data.get('hour', 0))
        minute = int(data.get('minute', 0))
        location_name = data.get('location_name') or 'กรุงเทพมหานคร'
        question = data.get('question')

        lat, lon, clean_loc = get_coordinates(location_name)
        logger.info(f"Geocoded location: {clean_loc} -> Lat: {lat}, Lon: {lon}")

        tz_thailand = timezone(timedelta(hours=7))
        birth_dt_local = datetime(year_ad, month, day, hour, minute, tzinfo=tz_thailand)
        birth_dt_utc = birth_dt_local.astimezone(timezone.utc)
        logger.info(f"Local Birth Time: {birth_dt_local} | Converted UTC: {birth_dt_utc}")

        chart_data = calculate_chart(birth_dt_utc, lat, lon)
        school_rules = load_school_rules()

        if question and str(question).strip():
            logger.info(f"Processing Transit QA for Question: {question}")
            qa_answer = analyze_transit_qa(user_name, str(question).strip(), chart_data)
            return jsonify({
                "status": "success",
                "type": "transit_qa",
                "question": question,
                "answer": qa_answer,
                "birth_chart_degrees": chart_data["birth_chart_degrees"],
                "transit_degrees": chart_data["transit_degrees"],
                "ruler_mapping": chart_data["ruler_mapping"],
                "chart_svg": chart_data["chart_svg"]
            })

        logger.info("Processing Natal 7 Categories Analysis")
        report_text = analyze_natal_7_categories(user_name, chart_data, school_rules)
        return jsonify({
            "status": "success",
            "type": "natal_7_categories",
            "report": report_text,
            "birth_chart_degrees": chart_data["birth_chart_degrees"],
            "transit_degrees": chart_data["transit_degrees"],
            "ruler_mapping": chart_data["ruler_mapping"],
            "chart_svg": chart_data["chart_svg"]
        })

    except Exception as e:
        tb = traceback.format_exc()
        logger.error(f"❌ /analyze Execution Error:\n{tb}")
        return jsonify({
            "status": "error",
            "error_type": type(e).__name__,
            "detail": str(e),
            "traceback": tb
        }), 500


@app.route('/deep_report', methods=['POST'])
def deep_report():
    try:
        data = request.get_json() or {}
        logger.debug(f"Received /deep_report Payload: {data}")

        user_name = data.get('user_name') or 'คุณ'
        day = int(data.get('day', 1))
        month = int(data.get('month', 1))
        
        year_input = int(data.get('year', 2538))
        year_ad = year_input - 543 if year_input > 2400 else year_input
        
        hour = int(data.get('hour', 0))
        minute = int(data.get('minute', 0))
        location_name = data.get('location_name') or 'กรุงเทพมหานคร'

        lat, lon, _ = get_coordinates(location_name)

        tz_thailand = timezone(timedelta(hours=7))
        birth_dt_local = datetime(year_ad, month, day, hour, minute, tzinfo=tz_thailand)
        birth_dt_utc = birth_dt_local.astimezone(timezone.utc)

        chart_data = calculate_chart(birth_dt_utc, lat, lon)
        school_rules = load_school_rules()

        logger.info("Generating Deep Report Analysis...")
        deep_report_res = analyze_deep_report_json(user_name, chart_data, school_rules)
        return jsonify({
            "status": "success",
            "type": "deep_report",
            "report": deep_report_res,
            "birth_chart_degrees": chart_data["birth_chart_degrees"],
            "transit_degrees": chart_data["transit_degrees"],
            "ruler_mapping": chart_data["ruler_mapping"],
            "chart_svg": chart_data["chart_svg"]
        })

    except Exception as e:
        tb = traceback.format_exc()
        logger.error(f"❌ /deep_report Execution Error:\n{tb}")
        return jsonify({
            "status": "error",
            "error_type": type(e).__name__,
            "detail": str(e),
            "traceback": tb
        }), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
