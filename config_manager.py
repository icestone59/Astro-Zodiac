import os
import json

RULES_FILE = "school_rules.json"
DEFAULT_RULES = {
    "school_name": "สำนักโหราศาสตร์วิวัฒนาการ",
    "natal_categories": {
        "1_personality": "", "2_finance": "", "3_career": "",
        "4_love": "", "5_strengths_weaknesses": "", "6_potentials": "", "7_growth": ""
    }
}

def load_school_rules() -> dict:
    if os.path.exists(RULES_FILE):
        try:
            with open(RULES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
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
