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
# 1. SWISS EPHEMERIS & SYSTEM CONFIG
# ------------------------------------------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

EPHE_DIR = "/tmp/ephe"
CHIRON_FILE = os.path.join(EPHE_DIR, "seas_18.se1")
RULES_FILE = "school_rules.json"

DEFAULT_RULES = {
    "school_name": "สำนักโหราศาสตร์วิวัฒนาการ",
    "natal_categories": {
        "1_personality": "", "2_finance": "", "3_career": "",
        "4_love": "", "5_strengths_weaknesses": "", "6_potentials": "", "7_growth": ""
    },
    "love_advanced_rules": {
        "personal_attraction_indicators": "", "complex_relationship_indicators": "",
        "sun_moon_midpoint_rules": "", "house_7_and_ruler_rules": "", "planets_in_7th_house": ""
    }
}

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
    "กรุงเทพ": (13.7563, 100.5018, "Asia/Bangkok"),
    "กรุงเทพมหานคร": (13.7563, 100.5018, "Asia/Bangkok"),
    "เชียงใหม่": (18.7883, 98.9853, "Asia/Bangkok"),
    "ภูเก็ต": (7.8804, 98.3923, "Asia/Bangkok"),
    "ขอนแก่น": (16.4322, 102.8236, "Asia/Bangkok"),
    "ชลบุรี": (13.3611, 100.9847, "Asia/Bangkok"),
    "สงขลา": (7.1988, 100.5951, "Asia/Bangkok")
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
    try:
        with open(RULES_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_RULES, f, ensure_ascii=False, indent=2)
    except Exception:
        pass
    return DEFAULT_RULES

def get_coordinates_fast(loc_str: str):
    loc_key = loc_str.strip().lower()
    if loc_key in LOCATION_CACHE:
        lat, lon, tz = LOCATION_CACHE[loc_key]
        return lat, lon, tz, loc_str
    try:
        search_query = f"{loc_str}, Thailand" if "thailand" not in loc_key and "ไทย" not in loc_key else loc_str
        loc = geolocator.geocode(search_query, timeout=10)
        if loc:
            tz_str = tf.timezone_at(lng=loc.longitude, lat=loc.latitude) or "Asia/Bangkok"
            LOCATION_CACHE[loc_key] = (loc.latitude, loc.longitude, tz_str)
            return loc.latitude, loc.longitude, tz_str, loc.address
    except Exception:
        pass
    return 13.7563, 100.5018, "Asia/Bangkok", loc_str

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
# 3. REQUEST SCHEMAS & ENDPOINTS
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
    return HTMLResponse("<h1>Evolutionary Astrology Engine API Active</h1>")

@app.get("/admin", response_class=HTMLResponse)
def serve_admin():
    if os.path.exists("admin.html"):
        return FileResponse("admin.html")
    return HTMLResponse("<h1>Admin Dashboard</h1>")

@app.get("/transit")
def get_realtime_transit():
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

@app.get("/api/rules")
def get_rules():
    return load_school_rules()

@app.post("/api/rules")
def save_rules(data: dict):
    try:
        with open(RULES_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return {"status": "success", "message": "บันทึกหลักการของสำนักเรียบร้อยแล้ว"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Save Error: {str(e)}")

@app.post("/analyze")
def analyze_chart(req: AnalysisRequest):
    try:
        year_ad = req.year - 543 if req.year > 2400 else req.year

        lat, lon, tz_str, address = get_coordinates_fast(req.location_name)
        
        local_tz = pytz.timezone(tz_str)
        local_dt = local_tz.localize(datetime(year_ad, req.month, req.day, req.hour, req.minute))
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

        if not req.question:
            system_prompt = f"""
คุณคือนักโหราศาสตร์สากลเชิงพัฒนาศักยภาพ (Evolutionary Astrologer)
หน้าที่: แปลงตำแหน่งดาวใน Birth Chart เป็นบทวิเคราะห์พฤติกรรม ลึกซึ้ง และเป็นเรื่องราวชีวิต (Storytelling)

กฎการเขียนเนื้อหาเชิงลึก:
1. **ห้ามใช้ศัพท์เทคนิคโหราศาสตร์เด็ดขาด** (แปลดาว/เรือนชะตา ให้กลายเป็นสภาวะจิตใจและพฤติกรรมจริง)
2. **ความลึกของเนื้อหา:** แต่ละหัวข้อต้องเขียนบรรยายเป็นเรื่องราวความยาว 2-3 ย่อหน้า ประกอบด้วย:
   - สภาวะจิตใจ พฤติกรรมภายนอก และสิ่งที่ซ่อนอยู่ภายใน
   - ปมความท้าทาย หรือจุดติดขัดที่เจ้าชะตามักเผชิญ
   - **กลยุทธ์พัฒนาศักยภาพ:** คำแนะนำเชิงพฤติกรรมที่นำไปใช้ได้จริง 1-2 ข้อ
3. **การติดสัญลักษณ์:**
   - หมวดใดมีตรรกะใน Library ของสำนัก -> ไม่ต้องใส่สัญลักษณ์
   - หมวดใดใช้ AI แปลขยายความ -> ต้องใส่ (i) ต่อท้ายชื่อหัวข้อ

โครงสร้าง 7 หมวดหมู่:
1. นิสัย บุคลิกภาพ
2. การเงิน
3. การงาน อาชีพ ที่ตรงกับดวง
4. ความรัก
5. จุดเด่น จุดด้อย และการแก้จุดด้อย
6. ศักยภาพที่มี และวิธีการพัฒนา
7. ปัญหาที่ต้องปรับปรุง เพื่อความก้าวหน้า
"""
            user_content = f"ชื่อผู้ใช้: {req.user_name}\n\n[Natal Planets]\n{json.dumps(natal_planets, ensure_ascii=False, indent=2)}\n\n[Natal Houses]\n{json.dumps(natal_houses, ensure_ascii=False, indent=2)}"
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_content}],
                temperature=0.2
            )
            return {
                "location_info": {"address": address, "timezone": tz_str},
                "birth_chart_degrees": natal_planets,
                "transit_degrees": transit_planets,
                "report": response.choices[0].message.content,
                "chart_svg": chart_svg
            }
        else:
            qa_system_prompt = f"""
คุณคือนักโหราศาสตร์สากลเชิงพัฒนาศักยภาพ
โทนเสียง: ผู้เชี่ยวชาญ มีหลักการ ตรงประเด็น ไม่พูดเยอะ
หน้าที่: ตอบคำถามเจาะจง Transit vs Natal โดยห้ามใช้คำศัพท์โหราศาสตร์เชิงเทคนิคในเนื้อหา
"""
            qa_user_content = f"คำถามผู้ใช้: \"{req.question}\"\n\n[Birth Chart]\n{json.dumps(natal_planets, ensure_ascii=False, indent=2)}\n\n[Transit]\n{json.dumps(transit_planets, ensure_ascii=False, indent=2)}"
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": qa_system_prompt}, {"role": "user", "content": qa_user_content}],
                temperature=0.2
            )
            return {
                "question": req.question,
                "answer": response.choices[0].message.content,
                "birth_chart_degrees": natal_planets,
                "transit_degrees": transit_planets,
                "chart_svg": chart_svg
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis Error: {str(e)}")

# ------------------------------------------------------------------
# 4. ENDPOINT: GENERATE DEEP REPORT (HTML TEMPLATE INJECTION)
# ------------------------------------------------------------------
@app.post("/generate-report", response_class=HTMLResponse)
def generate_deep_report(req: AnalysisRequest):
    """สร้างรายงานฉบับลึก 12 มิติชีวิตจากเทมเพลต report_template.html"""
    try:
        year_ad = req.year - 543 if req.year > 2400 else req.year
        lat, lon, tz_str, address = get_coordinates_fast(req.location_name)
        
        local_tz = pytz.timezone(tz_str)
        local_dt = local_tz.localize(datetime(year_ad, req.month, req.day, req.hour, req.minute))
        utc_dt = local_dt.astimezone(pytz.utc)

        natal_planets, natal_houses = _calculate_chart_data(utc_dt, lat, lon)
        school_rules = load_school_rules()

        if not client:
            raise HTTPException(status_code=500, detail="OPENAI_API_KEY is not configured on server")

        system_prompt = """
คุณคือนักโหราศาสตร์สากลเชิงพัฒนาศักยภาพผู้เชี่ยวชาญ
หน้าที่: วิเคราะห์พื้นดวงชะตาของผู้ใช้เพื่อสร้าง JSON Data สำหรับฉีดลงรายงานฉบับเจาะลึก 12 มิติชีวิต

ข้อบังคับการตอบ:
1. ต้องตอบกลับในรูปแบบ JSON Object เท่านั้น
2. **ห้ามใช้ศัพท์เทคนิคโหราศาสตร์เด็ดขาด** ในข้อความส่วนการวิเคราะห์
3. ภาษาที่ใช้ต้องเป็นสไตล์ Storytelling, อบอุ่น, ตรงประเด็น, ให้ข้อคิดทางจิตวิทยาและการพัฒนาชีวิต

โครงสร้าง JSON ที่ต้องส่งกลับ:
{
  "executive_summary": "ข้อความสรุปภาพรวมชีวิต 2-3 ย่อหน้า",
  "identity_list": ["หัวข้อที่ 1", "หัวข้อที่ 2", "หัวข้อที่ 3"],
  "identity_dev": "คำแนะนำพัฒนาตัวตน",
  "shadow_list": ["ปมที่ 1", "ปมที่ 2", "ปมที่ 3"],
  "shadow_dev": "คำแนะนำรับมือปมลึก",
  "wound_list": ["แผลใจที่ 1", "แผลใจที่ 2"],
  "wound_dev": "คำแนะนำการเยียวยา",
  "sabotage_list": ["จุดพังที่ 1", "จุดพังที่ 2"],
  "sabotage_mechanism": "อธิบายกลไกจิตวิทยาของจุดพัง",
  "career_summary": "สรุปพิมพ์เขียวการงาน",
  "career_match_list": ["อาชีพ 1", "อาชีพ 2", "อาชีพ 3"],
  "career_avoid_list": ["อาชีพที่ควรหลีกเลี่ยง 1", "อาชีพ 2"],
  "career_dev": "คำแนะนำเติบโตในอาชีพ",
  "money_list": ["แนวทางเปิดทรัพย์ 1", "แนวทาง 2"],
  "edu_list": ["สายการเรียนที่เหมาะ 1", "สายการเรียน 2"],
  "rel_list": ["สภาวะความรัก 1", "สภาวะ 2"],
  "health_list": ["ข้อควรระวังสุขภาพจิต 1", "แนวทางฟื้นฟู 2"],
  "life_strategy": "กลยุทธ์ชีวิตระยะยาว",
  "diagnosis": "คำวินิจฉัยและทางแก้หลักจากเมนเทอร์",
  "father_desc": "อธิบายภาพสะท้อนจากพ่อ",
  "mother_desc": "อธิบายภาพสะท้อนจากแม่",
  "family_atmosphere": "บรรยากาศในบ้าน",
  "family_dev": "คำแนะนำความสัมพันธ์ในครอบครัว"
}
"""
        user_content = f"ชื่อผู้ใช้: {req.user_name}\n\n[Natal Planets]\n{json.dumps(natal_planets, ensure_ascii=False, indent=2)}\n\n[Natal Houses]\n{json.dumps(natal_houses, ensure_ascii=False, indent=2)}"

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_content}],
            temperature=0.2
        )

        data = json.loads(response.choices[0].message.content)

        # โหลดไฟล์แม่แบบ HTML
        template_path = "report_template.html"
        if not os.path.exists(template_path):
            raise HTTPException(status_code=500, detail="ไม่พบไฟล์ report_template.html ในระบบ")

        with open(template_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        # แปลง List ให้เป็น <li> HTML
        def to_li(items):
            if isinstance(items, list):
                return "".join([f"<li>{item}</li>" for item in items])
            return f"<li>{items}</li>"

        # แทนที่ตัวแปรใน HTML Template
        replacements = {
            "{{ USER_NAME }}": req.user_name,
            "{{ SUN_SIGN }}": f"{natal_planets['Sun']['sign']} ({natal_planets['Sun']['formatted']})",
            "{{ MOON_SIGN }}": f"{natal_planets['Moon']['sign']} ({natal_planets['Moon']['formatted']})",
            "{{ ASC_SIGN }}": f"{natal_planets['ASC']['sign']} ({natal_planets['ASC']['formatted']})",
            "{{ MC_SIGN }}": f"{natal_planets['MC']['sign']} ({natal_planets['MC']['formatted']})",
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
            "{{ FATHER_DESC }}": data.get("father_desc", ""),
            "{{ MOTHER_DESC }}": data.get("mother_desc", ""),
            "{{ FAMILY_ATMOSPHERE }}": data.get("family_atmosphere", ""),
            "{{ FAMILY_DEV }}": data.get("family_dev", "")
        }

        for key, val in replacements.items():
            html_content = html_content.replace(key, str(val))

        return HTMLResponse(content=html_content)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generate Report Error: {str(e)}")
