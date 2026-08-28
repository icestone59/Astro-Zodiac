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

# ai_service.py - Strict Dual-Mode Directives

CLIENT_MODE_DIRECTIVE = """
[MODE: CLIENT VERSION - ภาษาจิตวิทยา 100%]
1. เขียนด้วยภาษาจิตวิทยาพัฒนาตนเองที่สละสลวย อ่านง่าย นำไปปฏิบัติได้จริง
2. ห้ามใช้คำว่า "ดาว", "ราศี", "เรือนชะตา", "ลัคนา", "มุม" หรือชื่อดาวภาษาอังกฤษ/ไทย (เช่น Sun, Moon, ราศีสิงห์, เรือนที่ 1) ในเนื้อหาบรรยายเด็ดขาด
3. อธิบายเฉพาะ "พฤติกรรม สภาวะ อารมณ์ และทางออก" ของผู้รับคำทำนายเท่านั้น
4. ตัดบรรทัด "ที่มา:" ท้ายย่อหน้าทิ้งทั้งหมด
"""

ASTROLOGER_MODE_DIRECTIVE = """
[MODE: ASTROLOGER TECHNICAL VERSION - โหราศาสตร์วิชาการ]
1. เขียนด้วยภาษาโหราศาสตร์สากลวิชาการ สำหรับนักโหราศาสตร์วิเคราะห์ดวงชะตา
2. ต้องระบุตำแหน่งดาวกำเนิด, ราศี, เรือนชะตา, องศา DMS, มุมสัมพันธ์ (เช่น Conjunction, Opposition, Square) และ House Ruler Chain ในเนื้อหาอย่างละเอียด
3. ต้องระบุบรรทัด "ที่มา:" ท้ายทุกหัวข้อ โดยแสดงข้อมูลองศาและเรือนชะตาเต็มรูปแบบ
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
