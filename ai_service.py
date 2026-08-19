# ai_service.py
import os
from openai import OpenAI
from prompts import (
    SYSTEM_PROMPT_NATAL_7,
    SYSTEM_PROMPT_TRANSIT_QA,
    SYSTEM_PROMPT_DEEP_REPORT
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def format_chart_context(chart_data):
    """แปลงข้อมูลดวงชะตาและ House Ruler เป็น Text Matrix ป้องกัน AI ข้ามการอ่านข้อมูล"""
    birth = chart_data.get("birth_chart_degrees", {})
    rulers = chart_data.get("ruler_mapping", {})
    transits = chart_data.get("transit_degrees", {})

    text = "=== 1. ตำแหน่งดาวกำเนิด (BIRTH CHART DEGREES) ===\n"
    for planet, info in birth.items():
        text += f"- {planet}: {info.get('sign')} {info.get('formatted')} (House {info.get('house')})\n"

    text += "\n=== 2. ตารางเจ้าเรือน (HOUSE RULER MAPPING - บังคับต้องนำไปแปลทุกหมวด) ===\n"
    for house, info in rulers.items():
        text += f"- {house} (ราศี {info.get('sign')}): ดาวเจ้าเรือนคือ {info.get('ruler_planet')} -> ไปสถิตที่ {info.get('ruler_pos')}\n"

    if transits:
        text += "\n=== 3. ตำแหน่งดาวจร REAL-TIME (TRANSIT DEGREES) ===\n"
        for planet, info in transits.items():
            text += f"- Transit {planet}: {info.get('sign')} {info.get('formatted')} (สถิตใน Natal House {info.get('house_in_natal')})\n"

    return text

def analyze_natal_7_categories(user_name, chart_data, school_rules):
    chart_text = format_chart_context(chart_data)
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT_NATAL_7},
            {"role": "user", "content": f"ผู้ถาม: {user_name}\n\n{chart_text}"}
        ],
        temperature=0.1
    )
    return res.choices[0].message.content

def analyze_transit_qa(user_name, question, chart_data):
    chart_text = format_chart_context(chart_data)
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT_TRANSIT_QA},
            {"role": "user", "content": f"ผู้ถาม: {user_name}\nคำถาม: {question}\n\n{chart_text}"}
        ],
        temperature=0.1
    )
    return res.choices[0].message.content

# 📌 เพิ่มฟังก์ชันที่ขาดหายไป แก้ปัญหา ImportError บน Render
def analyze_deep_report_json(user_name, chart_data, school_rules):
    chart_text = format_chart_context(chart_data)
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT_DEEP_REPORT},
            {"role": "user", "content": f"ผู้ถาม: {user_name}\n\n{chart_text}"}
        ],
        temperature=0.1
    )
    return res.choices[0].message.content
