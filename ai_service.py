# ai_service.py - รองรับ Quick Analysis และ Deep Report ตาม Architecture ใหม่

import os
from openai import OpenAI
from prompts import (
    SYSTEM_PROMPT_NATAL_7,
    SYSTEM_PROMPT_TRANSIT_QA,
    SYSTEM_PROMPT_DEEP_REPORT
)
from evidence_engine import build_evidence_matrix, format_evidence_for_prompt

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ⚡ ระดับ 1 — Quick / Standard Natal 7 Categories Analysis
def analyze_natal_7_categories(user_name, chart_data):
    evidence_matrix = build_evidence_matrix(chart_data)
    evidence_text = format_evidence_for_prompt(evidence_matrix)

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT_NATAL_7},
            {"role": "user", "content": f"ผู้รับคำทำนาย: {user_name}\n\n{evidence_text}"}
        ],
        temperature=0.1
    )
    return res.choices[0].message.content

# ⚡ ระดับ 1 — Transit Q&A (ส่งเฉพาะ Evidence คำถาม + ดาวจร)
def analyze_transit_qa(user_name, question, chart_data):
    evidence_matrix = build_evidence_matrix(chart_data)
    # ดึงเฉพาะ Evidence ความรัก/การงาน/การเงิน + Transits ตามบริบท
    evidence_text = format_evidence_for_prompt(evidence_matrix, ["personality", "career", "finance", "love", "transits"])

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT_TRANSIT_QA},
            {"role": "user", "content": f"ผู้ถาม: {user_name}\nคำถาม: {question}\n\n{evidence_text}"}
        ],
        temperature=0.1
    )
    return res.choices[0].message.content

# 🧠 ระดับ 2 — Deep Life Report (Dark Uranian Full Analysis)
def analyze_deep_report_json(user_name, chart_data):
    evidence_matrix = build_evidence_matrix(chart_data)
    evidence_text = format_evidence_for_prompt(evidence_matrix) # ส่ง Evidence รวมทั้งหมดครั้งเดียว

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT_DEEP_REPORT},
            {"role": "user", "content": f"ผู้รับคำทำนาย: {user_name}\n\n{evidence_text}"}
        ],
        temperature=0.1
    )
    return res.choices[0].message.content
