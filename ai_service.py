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

def extract_and_clean_json(text, marker):
    """สกัด JSON Array และลบก้อนข้อมูลนั้นออกจาก Text หลัก"""
    # ใช้ Regex ค้นหา marker ตามด้วยอะไรก็ได้ จนกว่าจะเจอวงเล็บ [ ... ]
    pattern = rf"{marker}.*?(\[.*?\])"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    
    if match:
        json_str = match.group(1)
        try:
            parsed_data = json.loads(json_str)
            # ลบก้อนที่หาเจอออกจากข้อความหลัก เพื่อไม่ให้ไปโผล่ในหน้าเว็บ
            clean_text = text.replace(match.group(0), "")
            return parsed_data, clean_text
        except json.JSONDecodeError as e:
            print(f"JSON Parse Error for {marker}: {e}\nString: {json_str}")
            return None, text
            
    return None, text

def analyze_natal_7_categories(user_name, chart_data):
    """1. วิเคราะห์พื้นดวง 7 หมวดหมู่หลัก (Natal Baseline)"""
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
    """2. วิเคราะห์คำถามเฉพาะเจาะจง ด้วย Transit Real-time + Birth Chart"""
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
    """วิเคราะห์ Deep Report และแยก Data Graph ออกมา"""
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
    
    # 1. สกัด Data Graph ออกมา
    radar_data, full_text = extract_and_clean_json(full_text, "RADAR_DATA")
    bar_data, full_text = extract_and_clean_json(full_text, "POTENTIAL_BAR_DATA")
    _, full_text = extract_and_clean_json(full_text, "POTENTIAL") # ลบก้อน POTENTIAL ทิ้ง
    
    # 2. คลีนหัวข้อที่ AI ชอบแถมมาทิ้งไปให้หมด
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
