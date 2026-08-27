# ai_service.py
import os
import re
import json
from openai import OpenAI
from prompts import (
    SYSTEM_PROMPT_NATAL_7,
    SYSTEM_PROMPT_TRANSIT_QA,
    SYSTEM_PROMPT_DEEP_REPORT
)
from evidence_engine import build_evidence_matrix, format_evidence_for_prompt

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# กำหนด Timeout สูงสุด 20 วินาทีสำหรับ OpenAI API Call
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    timeout=20.0,
    max_retries=1
)

# ai_service.py (ส่วนปรับการส่ง Prompt)

CLIENT_MODE_DIRECTIVE = """
[MODE: CLIENT VERSION]
- เขียนด้วยภาษาจิตวิทยาพัฒนาตนเองที่สละสลวย อ่านง่าย ให้กำลังใจ และนำไปปฏิบัติได้ทันที
- ห้ามใส่ชื่อดาว องศา DMS หรือศัพท์เทคนิคโหราศาสตร์ไว้ในเนื้อหาบรรยายหลักเด็ดขาด
- ให้สรุปตำแหน่งดาวที่ใช้คำนวณไว้สั้นๆ ในบรรทัด "ที่มา:" ท้ายย่อหน้าเท่านั้น
"""

ASTROLOGER_MODE_DIRECTIVE = """
[MODE: ASTROLOGER TECHNICAL VERSION]
- เขียนด้วยภาษาโหราศาสตร์วิชาการเชิงลึก สำหรับนักโหราศาสตร์และผู้ทดสอบระบบ
- ระบุชื่อดาว, ราศี, เรือนชะตา, องศา DMS, มุมสัมพันธ์ (Aspect Orbs), และ House Ruler Chain แทรกในเนื้อหาบรรยายอย่างละเอียด
"""

def get_mode_prompt(mode):
    return ASTROLOGER_MODE_DIRECTIVE if mode == 'astrologer' else CLIENT_MODE_DIRECTIVE

def extract_and_clean_json(text, marker):
    pattern = rf"{marker}\s*:\s*(\[.*?\])"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    
    if match:
        json_str = match.group(1)
        try:
            parsed_data = json.loads(json_str)
            clean_text = text.replace(match.group(0), "")
            return parsed_data, clean_text
        except json.JSONDecodeError:
            return None, text
            
    return None, text

# ai_service.py

def analyze_deep_report(user_name, chart_data):
    evidence_matrix = build_evidence_matrix(chart_data)
    evidence_text = format_evidence_for_prompt(evidence_matrix)

    res = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT_DEEP_REPORT},
            {"role": "user", "content": f"ผู้รับคำทำนาย: {user_name}\n\n{evidence_text}"}
        ],
        temperature=0.55,  # ปรับเพิ่มจาก 0.1 เป็น 0.55 เพื่อให้เขียนภาษานุ่มนวล ลึกซึ้ง และไม่ย่อสั้น
        max_tokens=3500     # ขยายพื้นที่ Token เพื่อให้เขียนครบทั้ง 12 หัวข้อ
    )
    
    full_text = res.choices[0].message.content
    
    # สกัดข้อมูล JSON สำหรับวาดกราฟ
    radar_data, full_text = extract_and_clean_json(full_text, "RADAR_DATA")
    bar_data, full_text = extract_and_clean_json(full_text, "POTENTIAL_BAR_DATA")
    
    return {
        "report": full_text.strip(),
        "radar_data": radar_data,
        "bar_data": bar_data
    }

def analyze_natal_7_categories(user_name, chart_data):
    evidence_matrix = build_evidence_matrix(chart_data)
    evidence_text = format_evidence_for_prompt(evidence_matrix)

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT_NATAL_7},
            {"role": "user", "content": f"ผู้รับคำทำนาย: {user_name}\n\n{evidence_text}"}
        ],
        temperature=0.0
    )
    return res.choices[0].message.content

def analyze_transit_qa(user_name, question, chart_data):
    evidence_matrix = build_evidence_matrix(chart_data)
    evidence_text = format_evidence_for_prompt(
        evidence_matrix, 
        ["personality", "career", "finance", "love", "shadow_wound", "transits"]
    )

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT_TRANSIT_QA},
            {"role": "user", "content": f"ผู้ถาม: {user_name}\nคำถาม: {question}\n\n{evidence_text}"}
        ],
        temperature=0.1
    )
    return res.choices[0].message.content

def analyze_deep_report(user_name, chart_data):
    evidence_matrix = build_evidence_matrix(chart_data)
    evidence_text = format_evidence_for_prompt(evidence_matrix)

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT_DEEP_REPORT},
            {"role": "user", "content": f"ผู้รับคำทำนาย: {user_name}\n\n{evidence_text}"}
        ],
        temperature=0.1
    )
    
    full_text = res.choices[0].message.content
    
    radar_data, full_text = extract_and_clean_json(full_text, "RADAR_DATA")
    bar_data, full_text = extract_and_clean_json(full_text, "POTENTIAL_BAR_DATA")
    _, full_text = extract_and_clean_json(full_text, "POTENTIAL")
    
    full_text = re.sub(r'={3,}.*?5\. DARK URANIAN POTENTIAL MAP.*?={3,}', '', full_text, flags=re.DOTALL | re.IGNORECASE)
    full_text = re.sub(r'={3,}.*?6\. GRAPH DATA.*?={3,}', '', full_text, flags=re.DOTALL | re.IGNORECASE)
    full_text = re.sub(r'A\. POTENTIAL RADAR\n*', '', full_text, flags=re.IGNORECASE)
    full_text = re.sub(r'B\. POTENTIAL vs ACTIVATION vs BLOCK\n*', '', full_text, flags=re.IGNORECASE)
    full_text = re.sub(r'GRAPH DATA\n*', '', full_text, flags=re.IGNORECASE)
    
    return {
        "report": full_text.strip(),
        "radar_data": radar_data,
        "bar_data": bar_data
    }
