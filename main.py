import os
import json
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

try:
    from chart_drawer import generate_astroseek_svg
except ImportError:
    def generate_astroseek_svg(planets, houses, asc_deg):
        return "<svg width='400' height='400'><text x='50%' y='50%' text-anchor='middle'>Chart Generated</text></svg>"

app = FastAPI(title="Evolutionary Astrology Engine API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------
# 1. SWISS EPHEMERIS & SYSTEM CONFIGURATION
# ------------------------------------------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

EPHE_DIR = "/tmp/ephe"
CHIRON_FILE = os.path.join(EPHE_DIR, "seas_18.se1")
RULES_FILE = "school_rules.json"

def ensure_ephe() -> bool:
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
    "กรุงเทพ": (13.7563, 100.5018, "Asia/Bangkok"),
    "กรุงเทพมหานคร": (13.7563, 100.5018, "Asia/Bangkok")
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

def load_school_rules() -> dict:
    if os.path.exists(RULES_FILE):
        try:
            with open(RULES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

# ------------------------------------------------------------------
# 2. HIGH-PRECISION DEGREE & HOUSE CALCULATIONS
# ------------------------------------------------------------------
def get_coordinates_fast(loc_str: str):
    loc_key = loc_str.strip().lower()
    if loc_key in LOCATION_CACHE:
        lat, lon, tz = LOCATION_CACHE[loc_key]
        return lat, lon, tz, loc_str
    try:
        loc = geolocator.geocode(loc_str, timeout=10)
        if loc:
            tz_str = tf.timezone_at(lng=loc.longitude, lat=loc.latitude) or "UTC"
            LOCATION_CACHE[loc_key] = (loc.latitude, loc.longitude, tz_str)
            return loc.latitude, loc.longitude, tz_str, loc.address
    except Exception:
        pass
    raise HTTPException(status_code=400, detail="ไม่พบพิกัดสถานที่เกิดที่ระบุ กรุณาระบุเมืองและประเทศให้ชัดเจน")

def _get_degree_info(degree: float, speed: float = 0.0) -> dict:
    degree = degree % 360
    sign_idx = int(degree // 30)
    deg_in_sign = degree % 30
    d, m = int(deg_in_sign), int((deg_in_sign - int(deg_in_sign)) * 60)
    return {
        "sign": ZODIAC_SIGNS[sign_idx],
        "degree": d, 
        "minute": m,
        "formatted": f"{d}°{m:02d}'",
        "absolute_degree": round(degree, 4),
        "is_retrograde": speed < 0
    }

def _calc_planet_position(julday: float, p_id: int) -> tuple[float, float]:
    ephe_ready = ensure_ephe()
    flag = swe.FLG_SWIEPH if (p_id == swe.CHIRON and ephe_ready) else swe.FLG_MOSEPH
    try:
        res, _ = swe.calc_ut(julday, p_id, flag)
        return res[0], res[3]
    except Exception:
        return 0.0, 0.0

def _calculate_chart_data(dt_utc: datetime, lat: float, lon: float):
    dec_hour = dt_utc.hour + (dt_utc.minute / 60.0) + (dt_utc.second / 3600.0)
    julday = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, dec_hour)

    planets = {}
    for name, p_id in PLANETS.items():
        deg, speed = _calc_planet_position(julday, p_id)
        planets[name] = _get_degree_info(deg, speed)

    sn_deg = (planets['North_Node']['absolute_degree'] + 180) % 360
    planets['South_Node'] = _get_degree_info(sn_deg)

    houses, ascmc = swe.houses(julday, lat, lon, b'P')
    planets['ASC'] = _get_degree_info(ascmc[0])
    planets['MC'] = _get_degree_info(ascmc[1])

    # คำนวณ Sun/Moon Midpoint
    sun_deg = planets['Sun']['absolute_degree']
    moon_deg = planets['Moon']['absolute_degree']
    diff = abs(sun_deg - moon_deg)
    midpoint_deg = ((sun_deg + moon_deg + 360) / 2.0) % 360 if diff > 180 else (sun_deg + moon_deg) / 2.0
    planets['Sun_Moon_Midpoint'] = _get_degree_info(midpoint_deg)

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
# 3. REQUEST SCHEMAS & API ENDPOINTS
# ------------------------------------------------------------------
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
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return HTMLResponse("<h1>Evolutionary Astrology Engine Active</h1>")

@app.get("/transit")
def get_realtime_transit():
    """1. คำนวณ Transit ดาวจร Real-Time ทุกดวง"""
    try:
        now_utc = datetime.now(pytz.utc)
        dec_hour = now_utc.hour + (now_utc.minute / 60.0) + (now_utc.second / 3600.0)
        julday = swe.julday(now_utc.year, now_utc.month, now_utc.day, dec_hour)
        
        transits = {}
        for name, p_id in PLANETS.items():
            deg, speed = _calc_planet_position(julday, p_id)
            transits[name] = _get_degree_info(deg, speed)
        
        sn_deg = (transits['North_Node']['absolute_degree'] + 180) % 360
        transits['South_Node'] = _get_degree_info(sn_deg)

        return {
            "timestamp_utc": now_utc.isoformat(),
            "transits": transits
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transit Error: {str(e)}")

@app.post("/analyze")
def analyze_chart(req: AnalysisRequest):
    """
    2. คำนวณ Birth Chart + Transit + สร้าง SVG + วิเคราะห์ตามโครงสร้างและโทนเสียงเฉพาะ
    """
    try:
        lat, lon, tz_str, address = get_coordinates_fast(req.location_name)
        
        local_tz = pytz.timezone(tz_str)
        local_dt = local_tz.localize(datetime(req.year, req.month, req.day, req.hour, req.minute))
        utc_dt = local_dt.astimezone(pytz.utc)

        natal_planets, natal_houses = _calculate_chart_data(utc_dt, lat, lon)
        now_utc = datetime.now(pytz.utc)
        transit_planets, _ = _calculate_chart_data(now_utc, lat, lon)

        target_planets = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto', 'North_Node', 'Chiron']
        simple_planets = {p: natal_planets[p]['absolute_degree'] for p in target_planets}
        simple_houses = [natal_houses[f'House_{i+1}']['absolute_degree'] for i in range(12)]
        chart_svg = generate_astroseek_svg(simple_planets, simple_houses, natal_planets['ASC']['absolute_degree'])

        if not client:
            raise HTTPException(status_code=500, detail="OPENAI_API_KEY is not configured on server")

        school_rules = load_school_rules()
        current_date_str = now_utc.strftime("%d %B %Y")

        # CASE 1: พยากรณ์พื้นดวง 7 หมวดหมู่ (ไม่มีคำถาม)
        if not req.question:
            system_prompt = f"""
คุณคือนักโหราศาสตร์สากลเชิงพัฒนาศักยภาพผู้เชี่ยวชาญ
โทนเสียง: ผู้เชี่ยวชาญ มีหลักการ อบอุ่น ตรงประเด็น ไม่พูดเยิ่นเย้อ ให้กำลังใจและชี้ทางสว่าง

หลักวิชาประจำสำนัก:
{json.dumps(school_rules, ensure_ascii=False, indent=2)}

หน้าที่: วิเคราะห์พื้นดวงชะตาของผู้ใช้ชื่อ '{req.user_name}' โดยแบ่งออกเป็น 7 หัวข้อหลักอย่างชัดเจน ดังนี้:
1. นิสัย บุคลิกภาพ
2. การเงิน
3. การงาน อาชีพ ที่ตรงกับดวง
4. ความรัก
5. จุดเด่น จุดด้อย และการแก้จุดด้อย
6. ศักยภาพที่มี และวิธีการพัฒนา
7. ปัญหาที่ต้องปรับปรุง เพื่อความก้าวหน้า

ให้อธิบายด้วยภาษามนุษย์ที่สลวย มีพลัง อ่านง่าย และนำไปปฏิบัติได้จริง
"""
            user_content = f"[Natal Planets]\n{json.dumps(natal_planets, ensure_ascii=False, indent=2)}\n\n[Natal Houses]\n{json.dumps(natal_houses, ensure_ascii=False, indent=2)}"
            
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

        # CASE 2: พยากรณ์ตามคำถามเจาะจง (Transit vs Birth Chart) ด้วยโครงสร้างโทนเสียงตามกำหนด
        else:
            qa_system_prompt = f"""
คุณคือนักโหราศาสตร์สากลเชิงพัฒนาศักยภาพ
ชื่อผู้ใช้: {req.user_name}
วันที่ปัจจุบัน: {current_date_str}

หลักวิชาประจำสำนัก:
{json.dumps(school_rules, ensure_ascii=False, indent=2)}

หน้าที่: วิเคราะห์มุมสัมพันธ์ระหว่างดาวจรปัจจุบัน (Transit) กับดาวเดิม (Birth Chart) เพื่อตอบคำถามผู้ใช้
บังคับใช้โครงสร้างและสไตล์การเขียนดังนี้อย่างเคร่งครัด:

1. คำทักทายเปิดหัวเรื่องเป็นกันเอง อบอุ่น และยืนยันวันที่ปัจจุบัน
2. 🌟 วิเคราะห์พื้นดวงเดิม: "[ตั้งชื่อเปรียบเทียบฉายาดวงชะตา]"
   - อธิบายโครงสร้างดาวเดิมในเรื่องนั้นๆ ชี้จุดแข็งและจุดที่ต้องระวัง
3. 🚀 เจาะลึกดวงจร: "[ตั้งชื่อสภาวะดวงจร]"
   - อธิบายตำแหน่งดาวจรและมุมสัมพันธ์ ระบุช่วงวัน/เดือน/ปี ที่จะเกิดการเปลี่ยนแปลงหรือจังหวะเวลาทองชัดเจน
4. 💎 บทสรุปแห่งโชคชะตาและกลยุทธ์เหนือพรหมลิขิต
   - **ฟันธงบทสรุป:** สรุปคำตอบตรงประเด็น ฟันธงช่วงเวลาที่จะประสบความสำเร็จ
   - **กลยุทธ์ชีวิต (แก้ที่ต้นเหตุ):** 
     - *รหัสวิธีแก้:* ทางออกเชิงพฤติกรรมและการปรับสภาวะจิตวิทยา (Evolutionary Strategy)
     - *การใช้ชีวิต/การพัฒนา:* สิ่งที่ต้องเตรียมพร้อมและทักษะที่ต้องใช้
5. ประโยคคำถามชวนคุยต่อในประเด็นที่เกี่ยวข้องกันในตอนท้าย
"""
            qa_user_content = f"คำถามผู้ใช้: \"{req.question}\"\n\n[Birth Chart Planets & Midpoint]\n{json.dumps(natal_planets, ensure_ascii=False, indent=2)}\n\n[Real-time Transit Planets]\n{json.dumps(transit_planets, ensure_ascii=False, indent=2)}"
            
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
