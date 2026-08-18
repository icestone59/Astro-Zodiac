import os
import json
from datetime import datetime
import pytz
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel

from config_manager import load_school_rules, save_school_rules
from astro_calc import get_coordinates, calculate_chart
from ai_service import analyze_natal_7_categories, analyze_transit_qa, analyze_deep_report_json, client

app = FastAPI(title="Evolutionary Astrology Engine API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalysisRequest(BaseModel):
    user_name: str | None = "คุณ"
    year: int
    month: int
    day: int
    hour: int
    minute: int
    location_name: str
    question: str | None = None

@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    if os.path.exists("index.html"): return FileResponse("index.html")
    return HTMLResponse("<h1>API Active</h1>")

@app.get("/admin", response_class=HTMLResponse)
def serve_admin():
    if os.path.exists("admin.html"): return FileResponse("admin.html")
    return HTMLResponse("<h1>Admin Dashboard</h1>")

@app.get("/transit")
def get_realtime_transit():
    try:
        now_utc = datetime.now(pytz.utc)
        transit_planets, _, _ = calculate_chart(now_utc, 13.7563, 100.5018)
        return {"timestamp_utc": now_utc.isoformat(), "transits": transit_planets}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/rules")
def get_rules():
    return load_school_rules()

@app.post("/api/rules")
def save_rules(data: dict):
    save_school_rules(data)
    return {"status": "success"}

@app.post("/analyze")
def analyze_chart_endpoint(req: AnalysisRequest):
    try:
        year_ad = req.year - 543 if req.year > 2400 else req.year
        lat, lon, tz_str, address = get_coordinates(req.location_name)
        local_tz = pytz.timezone(tz_str)
        local_dt = local_tz.localize(datetime(year_ad, req.month, req.day, req.hour, req.minute))
        utc_dt = local_dt.astimezone(pytz.utc)

        natal_planets, natal_houses, natal_aspects = calculate_chart(utc_dt, lat, lon)
        
        now_utc = datetime.now(pytz.utc)
        transit_planets, _, _ = calculate_chart(now_utc, lat, lon)

        if not client: raise HTTPException(status_code=500, detail="OPENAI_API_KEY is not configured")

        rules = load_school_rules()
        if not req.question:
            report = analyze_natal_7_categories(req.user_name, natal_planets, natal_houses, natal_aspects, rules)
        else:
            report = analyze_transit_qa(req.user_name, req.question, natal_planets, transit_planets, natal_aspects)

        return {
            "birth_chart_degrees": natal_planets,
            "natal_aspects": natal_aspects,
            "transit_degrees": transit_planets,
            "report": report
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-report", response_class=HTMLResponse)
def generate_deep_report_endpoint(req: AnalysisRequest):
    try:
        year_ad = req.year - 543 if req.year > 2400 else req.year
        lat, lon, tz_str, _ = get_coordinates(req.location_name)
        local_tz = pytz.timezone(tz_str)
        local_dt = local_tz.localize(datetime(year_ad, req.month, req.day, req.hour, req.minute))
        utc_dt = local_dt.astimezone(pytz.utc)

        natal_planets, natal_houses, natal_aspects = calculate_chart(utc_dt, lat, lon)

        if not client: raise HTTPException(status_code=500, detail="OPENAI_API_KEY is not configured")

    # โหลดสูตรจาก DB
        school_rules = load_school_rules()
        deep_rules = school_rules.get("deep_report_rules", "")

        # ส่ง deep_rules เข้าไปใน AI Service
        json_result = analyze_deep_report_json(req.user_name, natal_planets, natal_houses, natal_aspects, deep_rules)

        template_path = "report_template.html"
        if not os.path.exists(template_path):
            raise HTTPException(status_code=500, detail="ไม่พบไฟล์ report_template.html")

        with open(template_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        def to_li(items):
            if isinstance(items, list): return "".join([f"<li>{item}</li>" for item in items])
            return f"<li>{items}</li>"

        replacements = {
            "{{ USER_NAME }}": req.user_name,
            "{{ SUN_SIGN }}": f"{natal_planets.get('Sun', {}).get('sign', '')} ({natal_planets.get('Sun', {}).get('formatted', '')})",
            "{{ MOON_SIGN }}": f"{natal_planets.get('Moon', {}).get('sign', '')} ({natal_planets.get('Moon', {}).get('formatted', '')})",
            "{{ ASC_SIGN }}": f"{natal_planets.get('ASC', {}).get('sign', '')} ({natal_planets.get('ASC', {}).get('formatted', '')})",
            "{{ MC_SIGN }}": f"{natal_planets.get('MC', {}).get('sign', '')} ({natal_planets.get('MC', {}).get('formatted', '')})",
            "{{ EXECUTIVE_SUMMARY }}": data.get("executive_summary", ""),
            "{{ IDENTITY_LIST }}": to_li(data.get("identity_list", [])),
            "{{ IDENTITY_DEV }}": data.get("identity_dev", ""),
            "{{ SHADOW_LIST }}": to_li(data.get("shadow_list", [])),
            "{{ SHADOW_DEV }}": data.get("shadow_dev", ""),
            "{{ WOUND_LIST }}": to_li(data.get("wound_list", [])),
            "{{ WOUND_DEV }}": data.get("wound_dev", ""),
            "{{ SABOTAGE_LIST }}": to_li(data.get("sabotage_list", [])),
            "{{ SABOTAGE_MECHANISM }}": data.get("sabotage_mechanism", ""),
            "{{ CAREER_SUMMARY }}": data.get("career_summary", ""),
            "{{ CAREER_MATCH_LIST }}": to_li(data.get("career_match_list", [])),
            "{{ CAREER_AVOID_LIST }}": to_li(data.get("career_avoid_list", [])),
            "{{ CAREER_DEV }}": data.get("career_dev", ""),
            "{{ MONEY_LIST }}": to_li(data.get("money_list", [])),
            "{{ EDU_LIST }}": to_li(data.get("edu_list", [])),
            "{{ REL_LIST }}": to_li(data.get("rel_list", [])),
            "{{ HEALTH_LIST }}": to_li(data.get("health_list", [])),
            "{{ LIFE_STRATEGY }}": data.get("life_strategy", ""),
            "{{ DIAGNOSIS }}": data.get("diagnosis", ""),
            "{{ FATHER_DESC }}": data.get("father_desc", "").replace("\n", "<br>"),
            "{{ MOTHER_DESC }}": data.get("mother_desc", "").replace("\n", "<br>"),
            "{{ FAMILY_ATMOSPHERE }}": data.get("family_atmosphere", "").replace("\n", "<br>"),
            "{{ FAMILY_DEV }}": data.get("family_dev", "")
        }

        for key, val in replacements.items():
            html_content = html_content.replace(key, str(val))

        return HTMLResponse(content=html_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
