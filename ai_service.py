import os
import json
from openai import OpenAI
from astro_calc import get_realtime_transits
from prompts import (
    SYSTEM_PROMPT_NATAL_7,
    SYSTEM_PROMPT_TRANSIT_QA,
    SYSTEM_PROMPT_DEEP_REPORT
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_ai_service(payload_data: dict) -> dict:
    user_name = payload_data.get("user_name", "คุณผู้ใช้งาน")
    report_type = payload_data.get("report_type", "natal_7")
    chart_data = payload_data.get("chart_data", {})
    question = payload_data.get("question", "")
    package_level = payload_data.get("package_level", "pkg1")
    mode = payload_data.get("mode", "client")
    
    # 1. ดึงพิกัดดาวจร Real-time ล่าสุด
    transits_data = get_realtime_transits()
    
    user_prompt_content = f"""
    [USER INFORMATION]
    Name: {user_name}
    Package Level: {package_level}
    Mode: {mode}
    Question: {question if question else 'ไม่มีคำถามเฉพาะเจาะจง'}
    
    [NATAL CHART DATA]
    {json.dumps(chart_data, ensure_ascii=False, indent=2)}
    
    [REALTIME TRANSITS DATA]
    {json.dumps(transits_data, ensure_ascii=False, indent=2)}
    """
    
    # 2. ประมวลผลตามประเภทรายงาน
    if report_type == "deep_report":
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT_DEEP_REPORT},
                    {"role": "user", "content": user_prompt_content}
                ],
                response_format={"type": "json_object"},
                temperature=0.7
            )
            
            raw_content = response.choices[0].message.content
            parsed = json.loads(raw_content)
            
            return {
                "status": "success",
                "type": "deep_report",
                "report": parsed.get("report", ""),
                "radar_data": parsed.get("radar_data", []),
                "bar_data": parsed.get("bar_data", [])
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"AI Parsing Error: {str(e)}"
            }

    elif report_type == "transit_qa" or (question and package_level != "pkg1"):
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT_TRANSIT_QA},
                {"role": "user", "content": user_prompt_content}
            ],
            temperature=0.5
        )
        return {
            "status": "success",
            "type": "transit_qa",
            "answer": response.choices[0].message.content
        }

    else:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT_NATAL_7},
                {"role": "user", "content": user_prompt_content}
            ],
            temperature=0.6
        )
        return {
            "status": "success",
            "type": "natal_7",
            "report": response.choices[0].message.content
        }
