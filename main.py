import os
import sqlite3
import ssl
import urllib.request
from datetime import datetime
import pytz
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import swisseph as swe
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import openai

app = FastAPI(title="Evolutionary Astrology Engine API")

# ------------------------------------------------------------------
# CONFIG & SETUP
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

geolocator = Nominatim(user_agent="astro_zodiac_app")
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

# ==================================================================
# [ขั้นตอนที่ 3.1]: ฟังก์ชันเชื่อมต่ออ่านไฟล์ astro_rules.db
# ==================================================================
def query_local_db(lookup_keys: list) -> dict:
    """เปิดไฟล์ DB ท้องถิ่น ดึงคำพยากรณ์ด้วย Keys แล้วปิด DB ทันที"""
    db_path = "astro_rules.db"
    if not os.path.exists(db_path):
        return {}
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    results = {}
    for key in lookup_keys:
        cursor.execute("SELECT category, content FROM natal_rules WHERE lookup_key = ?", (key,))
        row = cursor.fetchone()
        if row:
            category, content = row
            results[category] = content
            
    conn.close()
    return results

class AnalysisRequest(BaseModel):
    year: int
    month: int
    day: int
    hour: int
    minute: int
    location_name: str
    question: str | None = None

# ------------------------------------------------------------------
# ENDPOINTS
# ------------------------------------------------------------------

@app.get("/transit")
def get_realtime_transit():
    """1. คำนวณ Real-time Transit ของดาวทุกดวง"""
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
def analyze_chart(req: AnalysisRequest):
    """2. ประมวลผล Birth Chart + Transit + ดึงคำพยากรณ์"""
    try:
        # Step A: แปลงสถานที่และเวลาเป็น UTC
        loc = geolocator.geocode(req.location_name, timeout=10)
        if not loc:
            raise HTTPException(status_code=400, detail="Location not found")
        
        lat, lon = loc.latitude, loc.longitude
        tz_str = tf.timezone_at(lng=lon, lat=lat) or "UTC"
        local_tz = pytz.timezone(tz_str)
        local_dt = local_tz.localize(datetime(req.year, req.month, req.day, req.hour, req.minute))
        utc_dt = local_dt.astimezone(pytz.utc)

        dec_hour = utc_dt.hour + (utc_dt.minute / 60.0) + (utc_dt.second / 3600.0)
        julday = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, dec_hour)

        # Step B: คำนวณ Birth Chart
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

        # Step C: สร้าง Lookup Keys สำหรับค้นหาใน DB
        search_keys = [
            f"ASC_{planets['ASC']['sign']}",
            f"Sun_{planets['Sun']['sign']}_H{planets['Sun']['house']}",
            f"Moon_{planets['Moon']['sign']}_H{planets['Moon']['house']}",
            f"Mercury_{planets['Mercury']['sign']}_H{planets['Mercury']['house']}",
            f"Venus_{planets['Venus']['sign']}_H{planets['Venus']['house']}",
            f"Mars_{planets['Mars']['sign']}_H{planets['Mars']['house']}",
            f"Saturn_{planets['Saturn']['sign']}_H{planets['Saturn']['house']}",
            f"Chiron_{planets['Chiron']['sign']}",
            f"NorthNode_{planets['North_Node']['sign']}"
        ]

        # ==================================================================
        # [ขั้นตอนที่ 3.2]: เรียกใช้ Local DB อ่านข้อมูล (ไม่เสียค่า API)
        # ==================================================================
        db_results = query_local_db(search_keys)

        # หากพบข้อมูลใน DB ครบตาม Keys ให้ส่งผลลัพธ์กลับทันที
        if db_results and len(db_results) > 0:
            return {
                "source": "local_db",
                "cost_baht": 0.0,
                "natal_chart_summary": {
                    "location": loc.address,
                    "utc_time": utc_dt.isoformat()
                },
                "prediction": db_results
            }

        # ==================================================================
        # Step D: Fallback กรณีใน DB ไม่มีข้อมูล จึงวิ่งไปหา OpenAI API
        # ==================================================================
        if not client:
            raise HTTPException(status_code=500, detail="Local DB miss and OPENAI_API_KEY is not configured")

        now_utc = datetime.now(pytz.utc)
        now_dec_hour = now_utc.hour + (now_utc.minute / 60.0) + (now_utc.second / 3600.0)
        now_julday = swe.julday(now_utc.year, now_utc.month, now_utc.day, now_dec_hour)

        transits = {}
        for name, p_id in PLANETS.items():
            transits[name] = _get_degree_info(_calc_planet_degree(now_julday, p_id))

        system_prompt = """คุณคือนักโหราศาสตร์สากลเชิงพัฒนาศักยภาพ
โทนเสียง: ผู้เชี่ยวชาญ มีหลักการ ตรงประเด็น ไม่อ้อมค้อม ไม่เพ้อเจ้อ
วิเคราะห์พื้นดวง 7 หัวข้อ หรือตอบคำถามเฉพาะเจาะจงจาก Transit + Birth Chart (Orb <= 4°)
"""
        user_content = f"[Natal]\n{planets}\n\n[Transit]\n{transits}\n\n[Question]\n{req.question}"

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            temperature=0.1
        )

        return {
            "source": "openai_api_fallback",
            "prediction": response.choices[0].message.content
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis Error: {str(e)}")
