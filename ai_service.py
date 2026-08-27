# ai_service.py - AI Integration Service with Dual-Mode Support

import os
import json
import re
from openai import OpenAI
from prompts import (
    SYSTEM_PROMPT_NATAL_7,
    SYSTEM_PROMPT_TRANSIT_QA,
    SYSTEM_PROMPT_DEEP_REPORT
)

# Initialize OpenAI Client
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    timeout=25.0,
    max_retries=1
)

# Directives สำหรับแยกโหมดการแปลผล
CLIENT_MODE_DIRECTIVE = """
[MODE: CLIENT VERSION - อ่านง่าย เน้นพฤติกรรมศาสตร์]
1. เขียนด้วยภาษาจิตวิทยาพัฒนาตนเองที่สละสลวย อ่านง่าย ให้กำลังใจ เข้าใจง่าย และนำไปปฏิบัติได้จริง
2. ห้ามแทรกชื่อดาว องศา DMS หรือศัพท์เทคนิคโหราศาสตร์ไว้ในเนื้อหาบรรยายหลัก
3. สรุปตำแหน่งดาวที่ใช้อ้างอิงไว้สั้นๆ ในบรรทัด "ที่มา:" ท้ายย่อหน้าเท่านั้น
"""

ASTROLOGER_MODE_DIRECTIVE = """
[MODE: ASTROLOGER TECHNICAL VERSION - วิชาการโหราศาสตร์เชิงลึก]
1. เขียนด้วยภาษาโหราศาสตร์วิชาการเชิงลึก สำหรับนักโหราศาสตร์และผู้ทดสอบระบบ
2. ระบุชื่อดาว, ราศี, เรือนชะตา, องศา DMS, มุมสัมพันธ์ (Aspect Orbs), และ House Ruler Chain แทรกในเนื้อหาอย่างละเอียด
"""

def get_mode_prompt(mode):
    return ASTROLOGER_MODE_DIRECTIVE if mode == 'astrologer' else CLIENT_MODE_DIRECTIVE

# Helper สำหรับดึงข้อมูล JSON ท้ายข้อความ Deep Report
def extract_and_clean_json(text, key_name):
    pattern = rf"{key_name}:\s*(\[.*?\])"
    match = re.search(pattern, text, re.DOTALL)
    data = []
    if match:
        raw_json = match.group(1)
        try:
            data = json.loads(raw_json)
            text = text.replace(match.group(0), "").strip()
        except Exception:
            data = []
    return data, text


# 1. ฟังก์ชันวิเคราะห์พื้นดวง 7 หมวดหมู่ (รองรับ mode)
def analyze_natal_7_categories(user_name, chart_data, mode='client'):
    mode_directive = get_mode_prompt(mode)
    prompt_content = f"{SYSTEM_PROMPT_NATAL_7}\n\n{mode_directive}\n\nผู้รับคำทำนาย: {user_name}\nข้อมูลดวงชะตา: {json.dumps(chart_data, ensure_ascii=False)}"

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt_content}
        ],
        temperature=0.4
    )
    return res.choices[0].message.content.strip()


# 2. ฟังก์ชันตอบคำถามดาวจร Transit Q&A (รองรับ mode)
def analyze_transit_qa(user_name, question, chart_data, mode='client'):
    mode_directive = get_mode_prompt(mode)
    prompt_content = f"{SYSTEM_PROMPT_TRANSIT_QA}\n\n{mode_directive}\n\nผู้รับคำทำนาย: {user_name}\nคำถามเจาะจง: {question}\nข้อมูลดวงชะตาและดาวจร: {json.dumps(chart_data, ensure_ascii=False)}"

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt_content}
        ],
        temperature=0.4
    )
    return res.choices[0].message.content.strip()


# 3. ฟังก์ชันวิเคราะห์ Clinical Deep Report 12 หัวข้อ (รองรับ mode)
def analyze_deep_report(user_name, chart_data, mode='client'):
    mode_directive = get_mode_prompt(mode)
    prompt_content = f"{SYSTEM_PROMPT_DEEP_REPORT}\n\n{mode_directive}\n\nผู้รับคำทำนาย: {user_name}\nข้อมูลดวงชะตา: {json.dumps(chart_data, ensure_ascii=False)}"

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt_content}
        ],
        temperature=0.5,
        max_tokens=3500
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
