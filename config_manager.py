import os
import json

RULES_FILE = "school_rules.json"
DEFAULT_RULES = {
    "school_name": "สำนักโหราศาสตร์วิวัฒนาการ",
    "natal_categories": {
        "1_personality": "", "2_finance": "", "3_career": "",
        "4_love": "", "5_strengths_weaknesses": "", "6_potentials": "", "7_growth": ""
    },
    "love_advanced_rules": {
        "personal_attraction_indicators": "", "complex_relationship_indicators": "",
        "sun_moon_midpoint_rules": "", "house_7_and_ruler_rules": "", "planets_in_7th_house": ""
    },
    # เพิ่มฐานข้อมูลส่วนนี้ สำหรับเก็บสูตร Deep Report โดยเฉพาะ
    "deep_report_rules": "" 
}

def load_school_rules() -> dict:
    if os.path.exists(RULES_FILE):
        try:
            with open(RULES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                # เช็กและเพิ่ม Key หากเป็นไฟล์เวอร์ชันเก่า
                if "deep_report_rules" not in data:
                    data["deep_report_rules"] = ""
                return data
        except Exception:
            pass
    try:
        with open(RULES_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_RULES, f, ensure_ascii=False, indent=2)
    except Exception:
        pass
    return DEFAULT_RULES

def save_school_rules(data: dict):
    with open(RULES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
