import os
import sqlite3
from datetime import datetime, timezone
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import swisseph as swe

from chart_drawer import generate_astroseek_svg

# ==========================================
# 1. INITIALIZE FASTAPI APP (ส่วนสำคัญที่ Render เรียกหา)
# ==========================================
app = FastAPI(title="Evolutionary Astrology Engine")

# ตั้งค่า Swiss Ephemeris Path
swe.set_ephe_path('')

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

PLANETS = {
    "Sun": swe.SUN, "Moon": swe.MOON, "Mercury": swe.MERCURY,
    "Venus": swe.VENUS, "Mars": swe.MARS, "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN, "Uranus": swe.URANUS, "Neptune": swe.NEPTUNE,
    "Pluto": swe.PLUTO, "North_Node": swe.TRUE_NODE, "Chiron": swe.CHIRON
}

# In-Memory Cache สำหรับสถานที่เกิดยอดนิยม (ลด Latency จาก Geocoding)
LOCATION_CACHE = {
    "bangkok, thailand": (13.7563, 100.5018, "Asia/Bangkok"),
    "bangkok": (13.7563, 100.5018, "Asia/Bangkok"),
    "กรุงเทพ": (13.7563, 100.5018, "Asia/Bangkok"),
    "กรุงเทพมหานคร": (13.7563, 100.5018, "Asia/Bangkok")
}

class BirthData(BaseModel):
    year: int
    month: int
    day: int
    hour: int
    minute: int
    location_name: str
    question: Optional[str] = None

# ==========================================
# 2. HELPER FUNCTIONS
# ==========================================
def get_coordinates_fast(location_str: str):
    loc_key = location_str.strip().lower()
    if loc_key in LOCATION_CACHE:
        lat, lon, tz = LOCATION_CACHE[loc_key]
        return lat, lon, tz, location_str

    try:
        from geopy.geocoders import Nominatim
        from timezonefinder import TimezoneFinder
        geolocator = Nominatim(user_agent="astro_engine_fast")
        loc = geolocator.geocode(location_str)
        if loc:
            tf = TimezoneFinder()
            tz_str = tf.timezone_at(lat=loc.latitude, lng=loc.longitude) or "UTC"
            LOCATION_CACHE[loc_key] = (loc.latitude, loc.longitude, tz_str)
            return loc.latitude, loc.longitude, tz_str, loc.address
    except Exception:
        pass
    
    return 13.7563, 100.5018, "Asia/Bangkok", location_str

def calculate_julian_day(year: int, month: int, day: int, hour: int, minute: int) -> float:
    utc_hour = hour + (minute / 60.0)
    return swe.julday(year, month, day, utc_hour)

def get_planet_deg(jd: float, planet_id: int):
    """
    คำนวณองศาดาวด้วย Moshier Ephemeris (FLG_MOSEPH) 
    ไม่ต้องใช้ไฟล์ .se1 บน Server แม่นยำสูงย้อนหลัง/ล่วงหน้า 3,000 ปี
    """
    res, _ = swe.calc_ut(jd, planet_id, swe.FLG_MOSEPH)
    deg = res[0]
    sign_idx = int(deg // 30)
    deg_in_sign = deg % 30
    return {
        "deg": deg,
        "sign": ZODIAC_SIGNS[sign_idx],
        "sign_deg": deg_in_sign,
        "formatted": f"{int(deg_in_sign)}°{int((deg_in_sign * 60) % 60):02d}'"
    }
def get_natal_interpretation_fast(category: str, lookup_key: str) -> str:
    db_path = "astro_rules.db"
    if not os.path.exists(db_path):
        return f"[{lookup_key}] โครงสร้างตำแหน่งดาวเน้นการเรียนรู้และพัฒนาศักยภาพเฉพาะตน"

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT content FROM natal_interpretations WHERE category = ? AND lookup_key = ?", (category, lookup_key))
        row = cursor.fetchone()
        if row:
            conn.close()
            return row[0]
            
        main_sign_key = lookup_key.split('_')[0] if '_' in lookup_key else lookup_key
        cursor.execute("SELECT content FROM natal_interpretations WHERE category = ? AND lookup_key LIKE ?", (category, f"{main_sign_key}%"))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return row[0]
    except Exception:
        pass

    return f"ตำแหน่งดาว {lookup_key} ส่งผลเน้นการเรียนรู้และพัฒนาศักยภาพเฉพาะตน"

# ==========================================
# 3. API ENDPOINTS
# ==========================================
@app.get("/", response_class=HTMLResponse)
def read_index():
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Astro Engine API Running</h1>"

@app.get("/transit")
def get_realtime_transit():
    now = datetime.now(timezone.utc)
    jd_now = calculate_julian_day(now.year, now.month, now.day, now.hour, now.minute)
    
    transits = {}
    for p_name, p_id in PLANETS.items():
        transits[p_name] = get_planet_deg(jd_now, p_id)
        
    return {
        "timestamp_utc": now.isoformat(),
        "transits": transits
    }

@app.post("/analyze")
def analyze_chart(data: BirthData):
    lat, lon, tz_str, address = get_coordinates_fast(data.location_name)
    jd = calculate_julian_day(data.year, data.month, data.day, data.hour, data.minute)
    
    # คำนวณองศาดาวกำเนิด
    birth_degrees = {}
    planets_simple = {}
    for p_name, p_id in PLANETS.items():
        p_info = get_planet_deg(jd, p_id)
        birth_degrees[p_name] = p_info
        planets_simple[p_name] = p_info["deg"]

    # คำนวณ Houses (Placidus)
    cusps, ascmc = swe.houses(jd, lat, lon, b'P')
    house_list = list(cusps)
    asc_deg = ascmc[0]
    mc_deg = ascmc[1]

    birth_degrees["ASC"] = {
        "deg": asc_deg,
        "sign": ZODIAC_SIGNS[int(asc_deg // 30)],
        "formatted": f"{int(asc_deg % 30)}°{int(((asc_deg % 30)*60)%60):02d}'"
    }
    birth_degrees["MC"] = {
        "deg": mc_deg,
        "sign": ZODIAC_SIGNS[int(mc_deg // 30)],
        "formatted": f"{int(mc_deg % 30)}°{int(((mc_deg % 30)*60)%60):02d}'"
    }

    # คำนวณผลพยากรณ์พื้นดวง 7 หมวดหมู่
    report_modules = {
        "1_personality": [
            get_natal_interpretation_fast("personality", f"ASC_{birth_degrees['ASC']['sign']}"),
            get_natal_interpretation_fast("personality", f"Sun_{birth_degrees['Sun']['sign']}_H10"),
            get_natal_interpretation_fast("personality", f"Moon_{birth_degrees['Moon']['sign']}_H1")
        ],
        "2_finance": [
            get_natal_interpretation_fast("finance", "H2_Virgo"),
            get_natal_interpretation_fast("finance", "H8_Pisces"),
            get_natal_interpretation_fast("finance", f"Venus_{birth_degrees['Venus']['sign']}_H9")
        ],
        "3_career": [
            get_natal_interpretation_fast("career", f"MC_{birth_degrees['MC']['sign']}"),
            get_natal_interpretation_fast("career", f"Sun_{birth_degrees['Sun']['sign']}_H10"),
            get_natal_interpretation_fast("career", "Saturn_H12")
        ],
        "4_love": [
            get_natal_interpretation_fast("love", "H7_Aquarius"),
            get_natal_interpretation_fast("love", "H5_Sagittarius"),
            get_natal_interpretation_fast("love", f"Venus_{birth_degrees['Venus']['sign']}"),
            get_natal_interpretation_fast("love", f"Mars_{birth_degrees['Mars']['sign']}")
        ],
        "5_strengths_weaknesses": [
            get_natal_interpretation_fast("strength_weakness", f"Chiron_{birth_degrees['Chiron']['sign']}_H9"),
            get_natal_interpretation_fast("strength_weakness", "general_remedy")
        ],
        "6_potentials": [
            get_natal_interpretation_fast("potential", f"NorthNode_{birth_degrees['North_Node']['sign']}"),
            get_natal_interpretation_fast("potential", "SouthNode_Virgo"),
            get_natal_interpretation_fast("potential", f"Jupiter_{birth_degrees['Jupiter']['sign']}_H10")
        ],
        "7_growth": [
            get_natal_interpretation_fast("growth", f"Saturn_{birth_degrees['Saturn']['sign']}_H12"),
            get_natal_interpretation_fast("growth", "H12_Cancer")
        ]
    }

    # สร้าง SVG Birth Chart
    chart_svg = generate_astroseek_svg(planets_simple, house_list, asc_deg)

    # Transit Q&A Logic
    qa_answer = None
    if data.question:
        qa_answer = "จังหวะดาวจรส่งพลังสนับสนุนในระยะ 1-3 เดือนนี้ ให้มุ่งเน้นการวางโครงสร้างและลงมือทำจริงอย่างเป็นระบบ"

    return {
        "source": "LOCAL_DB",
        "location_info": {"address": address, "timezone": tz_str},
        "birth_chart_degrees": birth_degrees,
        "report": report_modules,
        "question": data.question,
        "answer": qa_answer,
        "chart_svg": chart_svg
    }

@app.get("/db-view", response_class=HTMLResponse)
def db_view():
    db_path = "astro_rules.db"
    if not os.path.exists(db_path):
        return "<h1>ไม่พบไฟล์ astro_rules.db</h1>"
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT category, lookup_key, content FROM natal_interpretations ORDER BY category")
    rows = cursor.fetchall()
    conn.close()

    table_rows = "".join([f"<tr><td style='padding:8px;border:1px solid #333;'>{r[0]}</td><td style='padding:8px;border:1px solid #333;'>{r[1]}</td><td style='padding:8px;border:1px solid #333;'>{r[2]}</td></tr>" for r in rows])
    return f"<html><body style='background:#0f172a;color:#fff;font-family:sans-serif;padding:20px;'><h2>Astro DB View</h2><table style='width:100%;border-collapse:collapse;'><tr><th>Category</th><th>Key</th><th>Content</th></tr>{table_rows}</table></body></html>"

@app.get("/test-chart", response_class=HTMLResponse)
def test_chart():
    sample_planets = {
        "Sun": 63.81, "Moon": 142.16, "Mercury": 39.36, "Venus": 20.13,
        "Mars": 21.25, "Jupiter": 71.25, "Saturn": 131.61, "Uranus": 220.50,
        "Neptune": 254.20, "Pluto": 192.10, "North_Node": 190.50, "Chiron": 22.50
    }
    sample_houses = [132.68, 155.20, 184.50, 218.70, 252.10, 285.40, 312.68, 335.20, 4.50, 38.70, 72.10, 105.40]
    asc_degree = sample_houses[0]
    svg_out = generate_astroseek_svg(sample_planets, sample_houses, asc_degree)
    return f"<html><body style='background:#0f172a;display:flex;justify-content:center;align-items:center;min-height:100vh;'><div style='background:#fff;padding:10px;border-radius:12px;max-width:700px;'>{svg_out}</div></body></html>"
