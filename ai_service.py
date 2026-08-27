# ai_service.py - Robust OpenAI Integration with Timeout Handler

import os
import json
import re
from openai import OpenAI, APITimeoutError, APIError
from prompts import (
    SYSTEM_PROMPT_NATAL_7,
    SYSTEM_PROMPT_TRANSIT_QA,
    SYSTEM_PROMPT_DEEP_REPORT
)

# 1. ขยาย Timeout เป็น 60 วินาที และเปิด Auto Retry 2 ครั้ง
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    timeout=60.0,
    max_retries=2
)

CLIENT_MODE_DIRECTIVE = """
[MODE: CLIENT VERSION]
- ภาษาจิตวิทยาอ่านง่าย ไม่ใส่ชื่อดาว/องศาในเนื้อหาหลัก สรุปไว้ใน "ที่มา:" ท้ายย่อหน้า
"""

ASTROLOGER_MODE_DIRECTIVE = """
[MODE: ASTROLOGER VERSION]
- ภาษาเทคนิคโหราศาสตร์ ระบุชื่อดาว, ราศี, เรือนชะตา, องศา DMS, และ House Ruler Chain ชัดเจน
"""

def get_mode_prompt(mode):
    return ASTROLOGER_MODE_DIRECTIVE if mode == 'astrologer' else CLIENT_MODE_DIRECTIVE

# ฟังก์ชันดึง completions พร้อมระบบป้องกัน Timeout
def call_openai_safe(messages, temperature=0.4, max_tokens=2500):
    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return res.choices[0].message.content.strip()
    except APITimeoutError:
        raise RuntimeError("OpenAI API ตอบสนองช้าเกินกำหนด (Timeout 60s) กรุณากดลองแมตช์อีกครั้ง")
    except APIError as e:
        raise RuntimeError(f"OpenAI API Error: {str(e)}")

def analyze_natal_7_categories(user_name, chart_data, mode='client'):
    directive = get_mode_prompt(mode)
    prompt = f"{SYSTEM_PROMPT_NATAL_7}\n\n{directive}\n\nผู้รับคำทำนาย: {user_name}\nข้อมูลดวงชะตา: {json.dumps(chart_data, ensure_ascii=False)}"
    return call_openai_safe([{"role": "system", "content": prompt}], temperature=0.4)

def analyze_transit_qa(user_name, question, chart_data, mode='client'):
    directive = get_mode_prompt(mode)
    prompt = f"{SYSTEM_PROMPT_TRANSIT_QA}\n\n{directive}\n\nผู้รับคำทำนาย: {user_name}\nคำถาม: {question}\nข้อมูลดวงชะตา: {json.dumps(chart_data, ensure_ascii=False)}"
    return call_openai_safe([{"role": "system", "content": prompt}], temperature=0.4)

def analyze_deep_report(user_name, chart_data, mode='client'):
    directive = get_mode_prompt(mode)
    prompt = f"{SYSTEM_PROMPT_DEEP_REPORT}\n\n{directive}\n\nผู้รับคำทำนาย: {user_name}\nข้อมูลดวงชะตา: {json.dumps(chart_data, ensure_ascii=False)}"
    full_text = call_openai_safe([{"role": "system", "content": prompt}], temperature=0.5, max_tokens=3000)
    
    # สกัด JSON วาดกราฟ
    radar_data, clean_text = extract_and_clean_json(full_text, "RADAR_DATA")
    bar_data, clean_text = extract_and_clean_json(clean_text, "POTENTIAL_BAR_DATA")
    
    return {"report": clean_text, "radar_data": radar_data, "bar_data": bar_data}

def extract_and_clean_json(text, key_name):
    pattern = rf"{key_name}:\s*(\[.*?\])"
    match = re.search(pattern, text, re.DOTALL)
    data = []
    if match:
        try:
            data = json.loads(match.group(1))
            text = text.replace(match.group(0), "").strip()
        except Exception:
            data = []
    return data, text
