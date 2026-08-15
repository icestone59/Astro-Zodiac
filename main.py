import os
import sqlite3
import ssl
import urllib.request
from datetime import datetime
import pytz
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
import swisseph as swe
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import openai

# นำเข้าโมดูลวาดรูป Birth Chart
from chart_drawer import generate_astroseek_svg

app = FastAPI(title="Evolutionary Astrology Engine API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------
# 1. CONFIG & SWISS EPHEMERIS SETUP (Crash-Proof)
# ------------------------------------------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

EPHE_DIR = "/tmp/ephe"
CHIRON_FILE = os.path.join(EPHE_DIR, "seas_18.se1")

def ensure_ephe() -> bool:
    """ดาวน์โหลดไฟล์ Chiron (seas_18.se1) ป้องกันระบบค้างหากไม่มีไฟล์"""
    os.makedirs(EPHE_DIR, exist_ok=True)
    if os.path.exists(CHIRON_FILE) and os.path.getsize(CHIRON_FILE) > 200000:
        swe.set_ephe_path(EPHE_DIR)
        return True

    urls = [
        "https://raw.githubusercontent.com/aloistr/swisseph/master/ephe/seas_18.se1",
        "https://github.com/aloistr/swisseph/raw/master/ephe/seas_18.se1"
    ]

    for url in urls:
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
                data = response.read()
                if len(data) > 200000:
                    with open(CHIRON_FILE, 'wb') as out:
                        out.write(data)
                    swe.set_ephe_path(EPHE_DIR)
                    return True
        except Exception:
            pass

    swe.set_ephe_path(EPHE_DIR)
    return os.path.exists(CHIRON_FILE) and os.path.getsize(CHIRON_FILE) > 200000

geolocator = Nominatim(user_agent="evolutionary_astro_engine")
tf = TimezoneFinder()

LOCATION_CACHE = {
    "bangkok, thailand": (13.7563, 100.5018, "Asia/Bangkok"),
    "bangkok": (13.7563, 100.5018, "Asia/Bangkok"),
    "กรุงเทพ": (13.7563, 100.5018, "Asia/Bangkok")
}

PLANETS = {
    'Sun': swe.SUN, 'Moon': swe.MOON, 'Mercury': swe.MERCURY,
    'Venus': swe.VENUS, 'Mars': swe.MARS, 'Jupiter': swe.JUPITER,
    'Saturn': swe.SATURN, 'Uranus': swe.URANUS, 'Neptune': swe.NEPTUNE,
    'Pluto': swe.PLUTO, 'North_Node': swe.MEAN_NODE, 'Chiron': swe.CHIRON
}

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# ------------------------------------------------------------------
# 2. HELPER CALCULATIONS & FORMATTING
# ------------------------------------------------------------------
def get_coordinates_fast(loc_str: str):
    loc_key = loc_str.strip().lower()
    if loc_key in LOCATION_CACHE:
        return LOCATION_CACHE[loc_key][0], LOCATION_CACHE[loc_key][1], LOCATION_CACHE[loc_key][2], loc_str
    try:
        loc = geolocator.geocode(loc_str, timeout=10)
        if loc:
            tz_str = tf.timezone_at(lng=loc.longitude, lat=loc.latitude) or "UTC"
            LOCATION_CACHE[loc_key] = (loc.latitude, loc.longitude, tz_str)
            return loc.latitude, loc.longitude, tz_str, loc.address
    except Exception:
        pass
    raise HTTPException(status_code=400, detail="ไม่พบพิกัดสถานที่เกิดที่ระบุ")

def _get_degree_info(degree: float) -> dict:
    degree = degree % 360
    sign_idx = int(degree // 30)
    deg_in_sign = degree % 30
    d, m = int(deg_in_sign), int((deg_in_sign - int(deg_in_sign)) * 60)
    return {
        "sign": ZODIAC_SIGNS[sign_idx],
        "degree": d, "minute": m,
        "formatted": f"{d}°{m:02d}'",
        "absolute_degree": round(degree, 4)
    }

def _calc_planet_degree(julday: float, p_id: int) -> float:
    ephe_ready = ensure_ephe()
    if p_id == swe.CHIRON:
        if ephe_ready:
            try:
                res, _ = swe.calc_ut(julday, p_id, swe.FLG_SWIEPH)
                return res[0]
            except Exception:
                pass
        return 0.0 # Fallback 
    try:
        res, _ = swe.calc_ut(julday, p_id, swe.FLG_MOSEPH)
        return res[0]
    except Exception:
        return 0.0

def _calculate_chart_data(dt_utc: datetime, lat: float, lon: float):
    dec_hour = dt_utc.hour + (dt_utc.minute / 60.0) + (dt_utc.second / 3600.0)
    julday = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, dec_hour)

    planets = {name: _get_degree_info(_calc_planet_degree(julday, p_id)) for name, p_id in PLANETS.items()}
    planets['South_Node'] = _get_degree_info((planets['North_Node']['absolute_degree'] + 180) % 360)

    houses, ascmc = swe.houses(julday, lat, lon, b'P')
    planets['ASC'] = _get_degree_info(ascmc[0])
    planets['MC'] = _get_degree_info(ascmc[1])

    house_cusps = [houses[i] for i in range(12)]
    for p_name, p_data in planets.items():
        p_abs = p_data['absolute_degree']
        for h_idx in range(12):
            h_start, h_end = house_cusps[h_idx], house_cusps[(h_idx + 1) % 12]
            if (h_start < h_end and h_start <= p_abs < h_end) or (h_start >= h_end and (p_abs >= h_start or p_abs < h_end)):
                planets[p_name]['house'] = h_idx + 1
                break

    formatted_houses = {f"House_{i+1}": _get_degree_info(houses[i]) for i in range(12)}
    return planets, formatted_houses

# ------------------------------------------------------------------
# 3. REQUEST SCHEMAS
# ------------------------------------------------------------------
class AnalysisRequest(BaseModel):
    year: int
    month: int
    day: int
    hour: int
    minute: int
    location_name: str
    question: str | None = None

# ------------------------------------------------------------------
# 4. FASTAPI ENDPOINTS
# ------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return HTMLResponse("<h1>Evolutionary Astrology API Running</h1>")

@app.get("/transit")
def get_realtime_transit():
    """1. Transit ของดาวทุกดวงแบบ Real time"""
    try:
        now_utc = datetime.now(pytz.utc)
        dec_hour = now_utc.hour + (now_utc.minute / 60.0) + (now_utc.second / 3600.0)
        julday = swe.julday(now_utc.year, now_utc.month, now_utc.day, dec_hour)
        transits = {name: _get_degree_info(_calc_planet_degree(julday, p_id)) for name, p_id in PLANETS.items()}
        transits['South_Node'] = _get_degree_info((transits['North_Node']['absolute_degree'] + 180) % 360)
        return {"timestamp_utc": now_utc.isoformat(), "transits": transits}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transit Error: {str(e)}")

@app.post("/analyze")
def analyze_chart(req: AnalysisRequest):
    """2. & 3. คำนวณองศาดาวครบถ้วน (Birth Chart) + วิเคราะห์พื้นดวง/ตอบคำถาม (Transit)"""
    try:
        lat, lon, tz_str, address = get_coordinates_fast(req.location_name)
        
        local_tz = pytz.timezone(tz_str)
        local_dt = local_tz.localize(datetime(req.year, req.month, req.day, req.hour, req.minute))
        utc_dt = local_dt.astimezone(pytz.utc)

        natal_planets, natal_houses = _calculate_chart_data(utc_dt, lat, lon)
        
        now_utc = datetime.now(pytz.utc)
        transit_planets, _ = _calculate_chart_data(now_utc, lat, lon)

        # วาดรูป SVG
        target_planets = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto', 'North_Node', 'Chiron']
        simple_planets = {p: natal_planets[p]['absolute_degree'] for p in target_planets}
        simple_houses = [natal_houses[f'House_{i+1}']['absolute_degree'] for i in range(12)]
        chart_svg = generate_astroseek_svg(simple_planets, simple_houses, natal_planets['ASC']['absolute_degree'])

        if not client:
            raise HTTPException(status_code=500, detail="OPENAI_API_KEY is not configured.")

        # CASE 1: พยากรณ์พื้นดวง 7 หมวดหมู่
        if not req.question:
            system_prompt = """
คุณคือนักโหราศาสตร์สากลเชิงพัฒนาศักยภาพ (Psychological & Evolutionary Astrologer)
โทนเสียง: ผู้เชี่ยวชาญ มีหลักการ ตรงประเด็น ไม่พูดเยอะ ห้ามใช้คำทักทายหรือเกริ่นนำเด็ดขาด

ให้วิเคราะห์พื้นดวงชะตา (Birth Chart) โดยแบ่งเป็น 7 หัวข้อดังนี้เท่านั้น:
1. นิสัย บุคลิกภาพ
2. การเงิน
3. การงาน อาชีพ ที่ตรงกับดวง
4. ความรัก
5. จุดเด่น จุดด้อย และการแก้จุดด้อย
6. ศักยภาพที่มี และวิธีการพัฒนา
7. ปัญหาที่ต้องปรับปรุง เพื่อความก้าวหน้า
"""
            user_content = f"พิกัดดาวกำเนิด:\n{natal_planets}\nพิกัดเรือนชะตา:\n{natal_houses}"
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_content}],
                temperature=0.2
            )
            return {
                "location_info": {"address": address, "timezone": tz_str},
                "birth_chart_degrees": natal_planets,
                "report": response.choices[0].message.content,
                "chart_svg": chart_svg
            }

        # CASE 2: พยากรณ์ตามคำถามโดยใช้ Transit + Birth Chart
        else:
            qa_system_prompt = """
คุณคือนักโหราศาสตร์สากลเชิงพัฒนาศักยภาพ
โทนเสียง: ผู้เชี่ยวชาญ มีหลักการ ตรงประเด็น ไม่พูดเยอะ ห้ามใช้คำทักทาย

หน้าที่: วิเคราะห์คำถามของผู้ใช้ โดยเทียบมุมสัมพันธ์ระหว่างดาวจรปัจจุบัน (Transit) และ ดาวกำเนิด (Birth Chart)
- หาคำตอบที่ชัดเจน เช่น จะได้งานช่วงไหน ปัญหาแก้ด้วยพฤติกรรมใด
- ให้อธิบายตามหลักอิทธิพลดาวที่มากระทบอย่างเป็นเหตุเป็นผล
"""
            qa_user_content = f"คำถาม: \"{req.question}\"\n\n[Birth Chart]\n{natal_planets}\n\n[Real-time Transit]\n{transit_planets}"
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": qa_system_prompt}, {"role": "user", "content": qa_user_content}],
                temperature=0.2
            )
            return {
                "question": req.question,
                "answer": response.choices[0].message.content,
                "chart_svg": chart_svg
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis Error: {str(e)}")

@app.get("/db-view", response_class=HTMLResponse)
def view_database_contents():
    return "<h1>Local DB is disabled. Engine is running fully via System Prompts & High-precision Ephemeris.</h1>"
