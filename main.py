import os
import sqlite3
import ssl
import urllib.request
from datetime import datetime
import pytz
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import swisseph as swe
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import openai

# อิมพอร์ตโมดูลแปลความหมายทั้ง 7 หมวด
from interpreters import (
    PersonalityInterpreter,
    FinanceInterpreter,
    CareerInterpreter,
    LoveInterpreter,
    StrengthWeaknessInterpreter,
    PotentialInterpreter,
    GrowthInterpreter
)

app = FastAPI(title="Evolutionary Astrology Engine API")

# ------------------------------------------------------------------
# CONFIG & INITIALIZATION
# ------------------------------------------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

EPHE_DIR = "/tmp/ephe"
CHIRON_FILE = os.path.join(EPHE_DIR, "seas_18.se1")
CHIRON_URL = "https://raw.githubusercontent.com/aloistr/swisseph/master/ephe/seas_18.se1"

def ensure_ephe():
    os.makedirs(EPHE_DIR, exist_ok=True)
    if not os.path.exists(CHIRON_FILE) or os.path.getsize(CHIRON_FILE) < 200000:
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            req = urllib.request.Request(CHIRON_URL, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, context=ctx) as response, open(CHIRON_FILE, 'wb') as out:
                out.write(response.read())
        except Exception as e:
            print(f"[Ephemeris Warning] {e}")
    swe.set_ephe_path(EPHE_DIR)

geolocator = Nominatim(user_agent="astro_zodiac_engine")
tf = TimezoneFinder()

PLANETS = {
    'Sun': swe.SUN, 'Moon': swe.MOON, 'Mercury': swe.MERCURY,
    'Venus': swe.VENUS, 'Mars': swe.MARS, 'Jupiter': swe.JUPITER,
    'Saturn': swe.SATURN, 'Uranus': swe.URANUS, 'Neptune': swe.NEPTUNE,
    'Pluto': swe.PLUTO, 'Chiron': swe.CHIRON, 'North_Node': swe.MEAN_NODE
}

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# เรียกใช้งานโมดูลคำนวณทั้ง 7
personality_engine = PersonalityInterpreter()
finance_engine = FinanceInterpreter()
career_engine = CareerInterpreter()
love_engine = LoveInterpreter()
strength_engine = StrengthWeaknessInterpreter()
potential_engine = PotentialInterpreter()
growth_engine = GrowthInterpreter()

# ------------------------------------------------------------------
# HELPER FUNCTIONS
# ------------------------------------------------------------------
def _get_degree_info(degree: float) -> dict:
    degree = degree % 360
    sign_idx = int(degree // 30)
    deg_in_sign = degree % 30
    d = int(deg_in_sign)
    m = int((deg_in_sign - d) * 60)
    return {
        "sign": ZODIAC_SIGNS[sign_idx],
        "degree": d,
        "minute": m,
        "formatted": f"{d}°{m:02d}'",
        "absolute_degree": round(degree, 4)
    }

def _calc_planet_degree(julday: float, p_id: int) -> float:
    ensure_ephe()
    try:
        if p_id == swe.CHIRON:
            res, _ = swe.calc_ut(julday, p_id, swe.FLG_SWIEPH)
        else:
            res, _ = swe.calc_ut(julday, p_id, swe.FLG_MOSEPH)
        return res[0]
    except Exception:
        res, _ = swe.calc_ut(julday, p_id, swe.FLG_MOSEPH)
        return res[0]

def _calculate_chart(dt_utc: datetime, lat: float, lon: float):
    dec_hour = dt_utc.hour + (dt_utc.minute / 60.0) + (dt_utc.second / 3600.0)
    julday = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, dec_hour)

    planets = {}
    for name, p_id in PLANETS.items():
        planets[name] = _get_degree_info(_calc_planet_degree(julday, p_id))

    planets['South_Node'] = _get_degree_info((planets['North_Node']['absolute_degree'] + 180) % 360)

    houses, ascmc = swe.houses(julday, lat, lon, b'P')
    planets['ASC'] = _get_degree_info(ascmc[0])
    planets['MC'] = _get_degree_info(ascmc[1])

    house_cusps = [houses[i] for i in range(12)]
    for p_name, p_data in planets.items():
        p_abs = p_data['absolute_degree']
        for h_idx in range(12):
            h_start, h_end = house_cusps[h_idx], house_cusps[(h_idx + 1) % 12]
            if h_start < h_end:
                if h_start <= p_abs < h_end:
                    planets[p_name]['house'] = h_idx + 1
                    break
            else:
                if p_abs >= h_start or p_abs < h_end:
                    planets[p_name]['house'] = h_idx + 1
                    break

    formatted_houses = {f"House_{i+1}": _get_degree_info(houses[i]) for i in range(12)}
    return planets, formatted_houses

# ------------------------------------------------------------------
# SCHEMAS
# ------------------------------------------------------------------
class AnalysisRequest(BaseModel):
    year: int
    month: int
    day: int
    hour: int
    minute: int
    location_name: str
    question: str | None = None  # ถ้าเป็น None จะทำพยากรณ์พื้นดวง 7 หัวข้อ

# ------------------------------------------------------------------
# ENDPOINTS
# ------------------------------------------------------------------
@app.get("/transit")
def get_realtime_transit():
    """1. หาตำแหน่งดาวจร Real-time ทุกดวง (UTC)"""
    try:
        now_utc = datetime.now(pytz.utc)
        dec_hour = now_utc.hour + (now_utc.minute / 60.0) + (now_utc.second / 3600.0)
        julday = swe.julday(now_utc.year, now_utc.month, now_utc.day, dec_hour)

        transits = {}
        for name, p_id in PLANETS.items():
            transits[name] = _get_degree_info(_calc_planet_degree(julday, p_id))

        transits['South_Node'] = _get_degree_info((transits['North_Node']['absolute_degree'] + 180) % 360)
        return {"timestamp_utc": now_utc.isoformat(), "transits": transits}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transit Error: {str(e)}")

@app.post("/analyze")
def analyze(req: AnalysisRequest):
    """
    Endpoint หลัก:
    1. รับวัน/เวลา/สถานที่เกิด -> คำนวณองศาดาว Birth Chart
    2. ดึงดาวจร Real-time Transit
    3. หากไม่มีคำถาม -> พยากรณ์พื้นดวง 7 หมวดหมู่
    4. หากมีคำถาม -> สแกนมุมสัมพันธ์ Transit vs Natal เพื่อตอบคำถาม
    """
    try:
        # Step 1: แปลงสถานที่เกิดเป็น Lat/Lon/Timezone
        loc = geolocator.geocode(req.location_name, timeout=10)
        if not loc:
            raise HTTPException(status_code=400, detail="Location not found")
        
        lat, lon = loc.latitude, loc.longitude
        tz_str = tf.timezone_at(lng=lon, lat=lat) or "UTC"
        local_tz = pytz.timezone(tz_str)
        local_dt = local_tz.localize(datetime(req.year, req.month, req.day, req.hour, req.minute))
        utc_dt = local_dt.astimezone(pytz.utc)

        # Step 2: คำนวณ Birth Chart
        natal_planets, natal_houses = _calculate_chart(utc_dt, lat, lon)

        # Step 3: คำนวณ Real-time Transit
        now_utc = datetime.now(pytz.utc)
        transit_planets, _ = _calculate_chart(now_utc, lat, lon)

        # --------------------------------------------------------------
        # CASE 1: พยากรณ์พื้นดวง 7 หัวข้อ (ไม่มีคำถามเฉพาะเจาะจง)
        # --------------------------------------------------------------
        if not req.question:
            # รันการดึงข้อมูลจาก 7 โมดูลย่อย (Local DB)
            modular_report = {
                "1_personality": personality_engine.analyze(natal_planets),
                "2_finance": finance_engine.analyze(natal_planets, natal_houses),
                "3_career": career_engine.analyze(natal_planets),
                "4_love": love_engine.analyze(natal_planets, natal_houses),
                "5_strengths_weaknesses": strength_engine.analyze(natal_planets),
                "6_potentials": potential_engine.analyze(natal_planets),
                "7_growth": growth_engine.analyze(natal_planets, natal_houses)
            }

            # ตรวจสอบว่าใน Local DB มีข้อมูลครบถ้วนหรือไม่
            # หากมี key ที่ส่งข้อความ "รอการเพิ่มบทวิเคราะห์" และตั้งค่า OPENAI_API_KEY ไว้ จะ Fallback ไป AI
            has_missing = any(
                "รอการเพิ่มบทวิเคราะห์" in str(val) 
                for module in modular_report.values() 
                for val in module.values()
            )

            if not has_missing:
                return {
                    "source": "local_db",
                    "cost_baht": 0.0,
                    "location_info": {"address": loc.address, "timezone": tz_str},
                    "birth_chart_degrees": natal_planets,
                    "report": modular_report
                }

            # Fallback AI (ถ้า Local DB ข้อมูลยังไม่สมบูรณ์)
            if client:
                prompt = f"""
วิเคราะห์พื้นดวงชะตาเชิงพัฒนาศักยภาพแบ่งตาม 7 หัวข้อนี้อย่างเคร่งครัด:
1. นิสัย บุคลิกภาพ
2. การเงิน
3. การงาน อาชีพ ที่ตรงกับดวง
4. ความรัก
5. จุดเด่น จุดด้อย และการแก้จุดด้อย
6. ศักยภาพที่มี และวิธีการพัฒนา
7. ปัญหาที่ต้องปรับปรุง เพื่อความก้าวหน้า

[ข้อมูลดวงชะตา]
{natal_planets}
"""
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "คุณคือนักโหราศาสตร์สากลเชิงพัฒนาศักยภาพ โทนเสียง: ผู้เชี่ยวชาญ มีหลักการ ตรงประเด็น กระชับ ไม่อ้อมค้อม ตัดคำทักทายออกทั้งหมด"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2
                )
                return {
                    "source": "openai_api_fallback",
                    "location_info": {"address": loc.address, "timezone": tz_str},
                    "birth_chart_degrees": natal_planets,
                    "report": response.choices[0].message.content
                }

            return {
                "source": "local_db_partial",
                "location_info": {"address": loc.address, "timezone": tz_str},
                "birth_chart_degrees": natal_planets,
                "report": modular_report
            }

        # --------------------------------------------------------------
        # CASE 2: พยากรณ์ตามคำถามเฉพาะเจาะจง (Transit + Birth Chart)
        # --------------------------------------------------------------
        else:
            # ค้นหาคำตอบจาก Local Transit DB
            conn = sqlite3.connect("astro_rules.db")
            cursor = conn.cursor()
            
            # ตัวอย่างคิวรีคำตอบจาก DB ตามประเภทคำถาม
            answer = None
            if "งาน" in req.question:
                cursor.execute("SELECT solution_text FROM transit_interpretations WHERE question_type = 'career_timing'")
                row = cursor.fetchone()
                if row:
                    answer = row[0]
            elif "ปัญหา" in req.question:
                cursor.execute("SELECT solution_text FROM transit_interpretations WHERE question_type = 'problem_solving'")
                row = cursor.fetchone()
                if row:
                    answer = row[0]
            
            conn.close()

            if answer:
                return {
                    "source": "local_db",
                    "cost_baht": 0.0,
                    "question": req.question,
                    "answer": answer
                }

            # Fallback AI ประมวลผลมุมสัมพันธ์ Transit vs Natal
            if not client:
                raise HTTPException(status_code=500, detail="OPENAI_API_KEY is not configured for Q&A fallback")

            qa_prompt = f"""
คำนวณระยะมุมสัมพันธ์ (Orb <= 4°) ระหว่าง Transit (T) และ Birth Chart (N) เพื่อตอบคำถามผู้ใช้
คำถาม: "{req.question}"

[ข้อมูล Birth Chart]
{natal_planets}

[ข้อมูล Real-time Transit]
{transit_planets}

ข้อกำหนดการตอบ:
- ระบุช่วงเวลา/เดือนที่องศาดาวส่งผล
- ชี้สาเหตุปัญหา และกำหนดทางออกเชิงพฤติกรรมทันที
"""
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "คุณคือนักโหราศาสตร์สากลเชิงพัฒนาศักยภาพ โทนเสียง: ผู้เชี่ยวชาญ มีหลักการ ตรงประเด็น กระชับ ไม่อ้อมค้อม"},
                    {"role": "user", "content": qa_prompt}
                ],
                temperature=0.2
            )

            return {
                "source": "openai_api_qa",
                "question": req.question,
                "answer": response.choices[0].message.content
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analyze Error: {str(e)}")
