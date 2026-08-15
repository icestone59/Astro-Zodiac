import os
from datetime import datetime
import pytz
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel

# Import จากไฟล์ที่เราแยกไว้
from config_manager import load_school_rules, save_school_rules
from astro_calc import get_coordinates, calculate_chart
from ai_service import analyze_natal_7_categories, analyze_transit_qa, client

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
    return HTMLResponse("<h1>Admin</h1>")

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

        # 1. คำนวณ Birth Chart + Aspects (ข้อมูลแม่นยำ 100%)
        natal_planets, natal_houses, natal_aspects = calculate_chart(utc_dt, lat, lon)
        
        # 2. คำนวณดาวจร (Transit) ปัจจุบัน
        now_utc = datetime.now(pytz.utc)
        transit_planets, _, _ = calculate_chart(now_utc, lat, lon)

        if not client:
            raise HTTPException(status_code=500, detail="OPENAI_API_KEY is not configured")

        rules = load_school_rules()

        # 3. เลือกยิง AI ตามเงื่อนไข (มีคำถาม หรือ ไม่มีคำถาม)
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
        raise HTTPException(status_code=500, detail=f"Analysis Error: {str(e)}")
