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

app = FastAPI(title="Evolutionary Astrology Engine API")

# เปิดใช้งาน CORS รองรับการเรียกใช้จากต่าง Domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------
# 1. CONFIG & SWISS EPHEMERIS SETUP
# ------------------------------------------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

EPHE_DIR = "/tmp/ephe"
CHIRON_FILE = os.path.join(EPHE_DIR, "seas_18.se1")
CHIRON_URL = "https://raw.githubusercontent.com/aloistr/swisseph/master/ephe/seas_18.se1"

def ensure_ephe():
    """ตรวจสอบและดาวน์โหลดไฟล์ตำแหน่งดาว Chiron หากไม่มีในระบบ"""
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

geolocator = Nominatim(user_agent="evolutionary_astro_engine")
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

# ------------------------------------------------------------------
# 2. HELPER CALCULATIONS & FORMATTING
# ------------------------------------------------------------------
def _get_degree_info(degree: float) -> dict:
    """แปลงเลขทศนิยมเป็น องศา และ ลิปดา (DD°MM')"""
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
    """คำนวณตำแหน่งองศาดาวด้วย Swiss Ephemeris"""
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

def _calculate_chart_data(dt_utc: datetime, lat: float, lon: float):
    """คำนวณตำแหน่งองศาดาว จุดแกน และเรือนชะตา (Placidus)"""
    dec_hour = dt_utc.hour + (dt_utc.minute / 60.0) + (dt_utc.second / 3600.0)
    julday = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, dec_hour)

    planets = {}
    for name, p_id in PLANETS.items():
        planets[name] = _get_degree_info(_calc_planet_degree(julday, p_id))

    # South Node ตรงข้าม North Node 180°
    planets['South_Node'] = _get_degree_info((planets['North_Node']['absolute_degree'] + 180) % 360)

    # คำนวณ Houses ระบบ Placidus
    houses, ascmc = swe.houses(julday, lat, lon, b'P')
    planets['ASC'] = _get_degree_info(ascmc[0])
    planets['MC'] = _get_degree_info(ascmc[1])

    # ระบุ House placement ของดาวแต่ละดวง
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
# 3. MODULAR LOCAL DB INTERPRETER ENGINE
# ------------------------------------------------------------------
def query_local_natal_module(category: str, lookup_key: str, db_path: str = "astro_rules.db") -> str | None:
    """ค้นหาบทพยากรณ์จาก Local DB แยกตาม Category และ Key"""
    if not os.path.exists(db_path):
        return None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT content FROM natal_interpretations WHERE category = ? AND lookup_key = ?",
            (category, lookup_key)
        )
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None
    except Exception:
        return None

def execute_7_modules_analysis(planets: dict, houses: dict) -> dict:
    """ประมวลผลแยก 7 หมวดหมู่จาก Local Database"""
    modules = {
        "1_personality": [
            ("personality", f"ASC_{planets['ASC']['sign']}"),
            ("personality", f"Sun_{planets['Sun']['sign']}_H{planets['Sun']['house']}"),
            ("personality", f"Moon_{planets['Moon']['sign']}_H{planets['Moon']['house']}")
        ],
        "2_finance": [
            ("finance", f"H2_{houses['House_2']['sign']}"),
            ("finance", f"H8_{houses['House_8']['sign']}"),
            ("finance", f"Venus_{planets['Venus']['sign']}_H{planets['Venus']['house']}")
        ],
        "3_career": [
            ("career", f"MC_{planets['MC']['sign']}"),
            ("career", f"Sun_{planets['Sun']['sign']}_H{planets['Sun']['house']}"),
            ("career", f"Saturn_H{planets['Saturn']['house']}")
        ],
        "4_love": [
            ("love", f"H7_{houses['House_7']['sign']}"),
            ("love", f"H5_{houses['House_5']['sign']}"),
            ("love", f"Venus_{planets['Venus']['sign']}"),
            ("love", f"Mars_{planets['Mars']['sign']}")
        ],
        "5_strengths_weaknesses": [
            ("strength_weakness", f"Chiron_{planets['Chiron']['sign']}_H{planets['Chiron']['house']}"),
            ("strength_weakness", "general_remedy")
        ],
        "6_potentials": [
            ("potential", f"NorthNode_{planets['North_Node']['sign']}"),
            ("potential", f"SouthNode_{planets['South_Node']['sign']}"),
            ("potential", f"Jupiter_{planets['Jupiter']['sign']}_H{planets['Jupiter']['house']}")
        ],
        "7_growth": [
            ("growth", f"Saturn_{planets['Saturn']['sign']}_H{planets['Saturn']['house']}"),
            ("growth", f"H12_{houses['House_12']['sign']}")
        ]
    }

    report = {}
    is_complete = True

    for mod_key, rules in modules.items():
        mod_results = []
        for cat, key in rules:
            text = query_local_natal_module(cat, key)
            if text:
                mod_results.append(text)
            else:
                is_complete = False
                mod_results.append(f"[{key}] รอการเพิ่มข้อมูลลงในฐานข้อมูล")
        report[mod_key] = mod_results

    return {"is_complete": is_complete, "report": report}

# ------------------------------------------------------------------
# 4. REQUEST SCHEMAS
# ------------------------------------------------------------------
class NatalRequest(BaseModel):
    year: int
    month: int
    day: int
    hour: int
    minute: int
    location_name: str

class AnalysisRequest(BaseModel):
    year: int
    month: int
    day: int
    hour: int
    minute: int
    location_name: str
    question: str | None = None

# ------------------------------------------------------------------
# 5. FASTAPI ENDPOINTS
# ------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    """ให้บริการหน้าเว็บ Frontend UI (index.html)"""
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return HTMLResponse("<h1>Evolutionary Astrology API Running</h1><p>index.html not found in root directory.</p>")

@app.get("/transit")
def get_realtime_transit():
    """1. คำนวณ Real-time Transit ของดาวทุกดวง (UTC)"""
    try:
        now_utc = datetime.now(pytz.utc)
        dec_hour = now_utc.hour + (now_utc.minute / 60.0) + (now_utc.second / 3600.0)
        julday = swe.julday(now_utc.year, now_utc.month, now_utc.day, dec_hour)

        transits = {}
        for name, p_id in PLANETS.items():
            transits[name] = _get_degree_info(_calc_planet_degree(julday, p_id))

        transits['South_Node'] = _get_degree_info((transits['North_Node']['absolute_degree'] + 180) % 360)
        return {
            "timestamp_utc": now_utc.isoformat(),
            "transits": transits
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transit Calculation Error: {str(e)}")

@app.post("/natal")
def get_birth_chart(req: NatalRequest):
    """2. คำนวณข้อมูลองศาดาวแท้จริง แกนลัคนา และเรือนชะตา จากวันและสถานที่เกิด"""
    try:
        loc = geolocator.geocode(req.location_name, timeout=10)
        if not loc:
            raise HTTPException(status_code=400, detail="ไม่พบพิกัดสถานที่เกิดที่ระบุ")
        
        lat, lon = loc.latitude, loc.longitude
        tz_str = tf.timezone_at(lng=lon, lat=lat) or "UTC"

        local_tz = pytz.timezone(tz_str)
        local_dt = local_tz.localize(datetime(req.year, req.month, req.day, req.hour, req.minute))
        utc_dt = local_dt.astimezone(pytz.utc)

        planets, houses = _calculate_chart_data(utc_dt, lat, lon)

        return {
            "resolved_location": loc.address,
            "coordinates": {"lat": lat, "lon": lon, "timezone": tz_str},
            "utc_time": utc_dt.isoformat(),
            "planets": planets,
            "houses": houses
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Natal Error: {str(e)}")

@app.post("/analyze")
def analyze_chart(req: AnalysisRequest):
    """
    3. Endpoint ประมวลผลหลัก:
       - คำนวณ Birth Chart + Real-time Transit
       - หากไม่มีคำถาม: คืนค่าผลพยากรณ์พื้นดวง 7 หมวดหมู่ (Local DB -> Fallback AI)
       - หากมีคำถาม: ประมวลผล Transit vs Natal ตอบคำถามเจาะจง
    """
    try:
        # Step A: พิกัดและเวลาเกิด
        loc = geolocator.geocode(req.location_name, timeout=10)
        if not loc:
            raise HTTPException(status_code=400, detail="ไม่พบพิกัดสถานที่เกิดที่ระบุ")
        
        lat, lon = loc.latitude, loc.longitude
        tz_str = tf.timezone_at(lng=lon, lat=lat) or "UTC"
        local_tz = pytz.timezone(tz_str)
        local_dt = local_tz.localize(datetime(req.year, req.month, req.day, req.hour, req.minute))
        utc_dt = local_dt.astimezone(pytz.utc)

        # Step B: คำนวณ Birth Chart และ Real-time Transit
        natal_planets, natal_houses = _calculate_chart_data(utc_dt, lat, lon)
        now_utc = datetime.now(pytz.utc)
        transit_planets, _ = _calculate_chart_data(now_utc, lat, lon)

        # --------------------------------------------------------------
        # CASE 1: พยากรณ์พื้นดวง 7 หมวดหมู่ (ไม่มีคำถาม)
        # --------------------------------------------------------------
        if not req.question:
            local_db_res = execute_7_modules_analysis(natal_planets, natal_houses)

            # หากข้อมูลใน Local DB สมบูรณ์ ส่งกลับทันที (0 บาท)
            if local_db_res["is_complete"]:
                return {
                    "source": "local_db",
                    "cost_baht": 0.0,
                    "location_info": {"address": loc.address, "timezone": tz_str},
                    "birth_chart_degrees": natal_planets,
                    "report": local_db_res["report"]
                }

            # Fallback ไปที่ OpenAI API หาก Local DB ข้อมูลยังไม่ครบ 100%
            if not client:
                return {
                    "source": "local_db_partial",
                    "location_info": {"address": loc.address, "timezone": tz_str},
                    "birth_chart_degrees": natal_planets,
                    "report": local_db_res["report"]
                }

            system_prompt = """
คุณคือนักโหราศาสตร์สากลเชิงพัฒนาศักยภาพ (Psychological & Evolutionary Astrologer)
หน้าที่: วิเคราะห์พื้นดวงชะตาเพื่อแนะนำการพัฒนาตนเอง ทลายข้อจำกัดทางจิตวิทยา และปลดล็อกศักยภาพ

ข้อกำหนดเรื่องโทนเสียงและรูปแบบอย่างเคร่งครัด:
1. โทนเสียง: ผู้เชี่ยวชาญ มีหลักการ ตรงประเด็น กระชับ ไม่อ้อมค้อม ไม่เพ้อเจ้อ
2. ห้ามใช้คำทักทาย อารัมภบท หรือคำอวยพรเด็ดขาด
3. แบ่งเนื้อหาออกเป็น 7 หัวข้อหลักอย่างชัดเจน:
   1. นิสัย บุคลิกภาพ
   2. การเงิน
   3. การงาน อาชีพ ที่ตรงกับดวง
   4. ความรัก
   5. จุดเด่น จุดด้อย และการแก้จุดด้อย
   6. ศักยภาพที่มี และวิธีการพัฒนา
   7. ปัญหาที่ต้องปรับปรุง เพื่อความก้าวหน้า
"""
            user_content = f"[Birth Chart Data]\n{natal_planets}"

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.2
            )

            return {
                "source": "openai_api_fallback",
                "location_info": {"address": loc.address, "timezone": tz_str},
                "birth_chart_degrees": natal_planets,
                "report": response.choices[0].message.content
            }

        # --------------------------------------------------------------
        # CASE 2: พยากรณ์ตามคำถามเจาะจง (Transit + Birth Chart)
        # --------------------------------------------------------------
        else:
            # ตรวจสอบคำตอบจาก Local Transit DB ก่อน
            conn = sqlite3.connect("astro_rules.db") if os.path.exists("astro_rules.db") else None
            db_answer = None
            if conn:
                cursor = conn.cursor()
                if "งาน" in req.question:
                    cursor.execute("SELECT solution_text FROM transit_interpretations WHERE question_type = 'career_timing'")
                elif "ปัญหา" in req.question:
                    cursor.execute("SELECT solution_text FROM transit_interpretations WHERE question_type = 'problem_solving'")
                row = cursor.fetchone()
                if row:
                    db_answer = row[0]
                conn.close()

            if db_answer:
                return {
                    "source": "local_db",
                    "cost_baht": 0.0,
                    "question": req.question,
                    "answer": db_answer
                }

            # Fallback ไปที่ OpenAI API ประมวลผลมุมสัมพันธ์ Transit vs Natal (Orb <= 4°)
            if not client:
                raise HTTPException(status_code=500, detail="OPENAI_API_KEY is not configured on server")

            qa_system_prompt = """
คุณคือนักโหราศาสตร์สากลเชิงพัฒนาศักยภาพ
หน้าที่: คำนวณระยะมุมสัมพันธ์ (Orb <= 4°) ระหว่าง Transit (T) และ Birth Chart (N) เพื่อตอบคำถามผู้ใช้

ข้อกำหนดการตอบ:
1. โทนเสียง: ผู้เชี่ยวชาญ มีหลักการ ตรงประเด็น กระชับ ไม่อ้อมค้อม ตัดคำทักทายออกทั้งหมด
2. ระบุช่วงเวลา/เดือนที่องศาดาวจรทำมุมส่งผลชัดเจน
3. ชี้สาเหตุปัญหาทางจิตวิทยา/พฤติกรรม และกำหนดทางออกเชิงพฤติกรรม (Actionable Steps) ทันที
"""
            qa_user_content = f"คำถาม: \"{req.question}\"\n\n[Birth Chart]\n{natal_planets}\n\n[Real-time Transit]\n{transit_planets}"

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": qa_system_prompt},
                    {"role": "user", "content": qa_user_content}
                ],
                temperature=0.2
            )

            return {
                "source": "openai_api_qa",
                "question": req.question,
                "answer": response.choices[0].message.content
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis Error: {str(e)}")
