import os
import json
from openai import OpenAI
from prompts import SYSTEM_PROMPT_DEEP_REPORT
from evidence_engine import build_evidence_matrix, format_evidence_for_prompt

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_json_block(text, marker):
    """สกัด JSON Array ด้วยการนับวงเล็บ (Bracket Matching) ป้องกัน JSON ขาดแหว่ง"""
    marker_str = f"{marker}:"
    start_idx = text.find(marker_str)
    if start_idx == -1:
        return None, text
        
    array_start = text.find("[", start_idx)
    if array_start == -1:
        return None, text
        
    bracket_count = 0
    array_end = -1
    for i in range(array_start, len(text)):
        if text[i] == '[':
            bracket_count += 1
        elif text[i] == ']':
            bracket_count -= 1
            
        if bracket_count == 0:
            array_end = i + 1
            break
            
    if array_end != -1:
        json_str = text[array_start:array_end]
        try:
            parsed_json = json.loads(json_str)
            # ตัดก้อนข้อความดิบออกไป เพื่อไม่ให้ไปโผล่ในหน้าเว็บ
            text_to_remove = text[start_idx:array_end]
            clean_text = text.replace(text_to_remove, "")
            return parsed_json, clean_text
        except Exception as e:
            print(f"JSON Parse Error for {marker}: {e}\nRaw String: {json_str}")
            
    return None, text

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
    
    # 1. สกัดข้อมูลกราฟออกมาอย่างแม่นยำด้วยการนับวงเล็บ
    radar_data, full_text = extract_json_block(full_text, "RADAR_DATA")
    bar_data, full_text = extract_json_block(full_text, "POTENTIAL_BAR_DATA")
    potential_data, full_text = extract_json_block(full_text, "POTENTIAL")
    
    # 2. คลีนข้อความส่วนหัวข้อตกค้าง (เช่น "GRAPH DATA", "A. POTENTIAL RADAR") ออกให้เรียบร้อย
    import re
    full_text = re.sub(r'6\. GRAPH DATA\n+', '', full_text, flags=re.IGNORECASE)
    full_text = re.sub(r'A\. POTENTIAL RADAR\n+', '', full_text, flags=re.IGNORECASE)
    full_text = re.sub(r'B\. POTENTIAL vs ACTIVATION vs BLOCK\n+', '', full_text, flags=re.IGNORECASE)
    
    return {
        "report": full_text.strip(),
        "radar_data": radar_data,
        "bar_data": bar_data
    }
