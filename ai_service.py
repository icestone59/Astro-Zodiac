# ai_service.py
import os
import re
import json
from openai import OpenAI
from prompts import SYSTEM_PROMPT_DEEP_REPORT
from evidence_engine import build_evidence_matrix, format_evidence_for_prompt

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_json_block(text, marker):
    """สกัดก้อน JSON Array ที่ถูกครอบด้วยชื่อ Marker ที่ระบุใน Prompt"""
    pattern = f"{marker}:\s*(\[.*?\])"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except Exception as e:
            print(f"JSON Parse Error for {marker}: {e}")
    return None

def analyze_deep_report(user_name, chart_data):
    evidence_matrix = build_evidence_matrix(chart_data)
    # ส่ง Evidence 12 เรือนแบบเต็ม (คุณต้องปรับ evidence_engine.py ให้ครอบคลุมทุกหมวดด้วย)
    evidence_text = format_evidence_for_prompt(evidence_matrix)

    res = client.chat.completions.create(
        model="gpt-4o-mini", # ใช้ mini ไปก่อนตามที่คุณระบุ
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT_DEEP_REPORT},
            {"role": "user", "content": f"ผู้รับคำทำนาย: {user_name}\n\n{evidence_text}"}
        ],
        temperature=0.1
    )
    
    full_text = res.choices[0].message.content
    
    # 1. สกัดข้อมูลกราฟออกมาเป็น JSON Object
    radar_data = extract_json_block(full_text, "RADAR_DATA")
    bar_data = extract_json_block(full_text, "POTENTIAL_BAR_DATA")
    
    # 2. ลบก้อน JSON ดิบออกจาก Text เพื่อไม่ให้หน้าเว็บแสดงโค้ดรกๆ
    clean_text = re.sub(r'RADAR_DATA:\s*\[.*?\]', '', full_text, flags=re.DOTALL)
    clean_text = re.sub(r'POTENTIAL_BAR_DATA:\s*\[.*?\]', '', clean_text, flags=re.DOTALL)
    clean_text = re.sub(r'POTENTIAL:\s*\[.*?\]', '', clean_text, flags=re.DOTALL) # ซ่อน JSON ก้อนนี้ด้วยถ้ามี
    
    return {
        "report": clean_text.strip(),
        "radar_data": radar_data,
        "bar_data": bar_data
    }
