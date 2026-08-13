import os
import urllib.request
from datetime import datetime
import pytz
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import swisseph as swe

app = FastAPI(title="Astrology Engine API")

# 1. กำหนดตำแหน่งเก็บไฟล์ Ephemeris ไปที่ /tmp/ephe
EPHE_DIR = "/tmp/ephe"
os.makedirs(EPHE_DIR, exist_ok=True)
chiron_file = os.path.join(EPHE_DIR, "seas_18.se1")

# 2. ตรวจสอบและดาวน์โหลดไฟล์ seas_18.se1 สำหรับ Chiron
if not os.path.exists(chiron_file) or os.path.getsize(chiron_file) == 0:
    try:
        url = "https://www.astro.com/ftp/swisseph/ephe/seas_18.se1"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response, open(chiron_file, 'wb') as out_file:
            out_file.write(response.read())
    except Exception as e:
        print(f"Ephemeris Download Error: {e}")

# 3. กำหนดให้ Swiss Ephemeris อ่านไฟล์จาก /tmp/ephe
swe.set_ephe_path(EPHE_DIR)

PLANETS = {
    'Sun': swe.SUN, 'Moon': swe.MOON, 'Mercury': swe.MERCURY,
    'Venus': swe.VENUS, 'Mars': swe.MARS, 'Jupiter': swe.JUPITER,
    'Saturn': swe.SATURN, 'Uranus': swe.URANUS, 'Neptune': swe.NEPTUNE,
    'Pluto': swe.PLUTO, 'North_Node': swe.MEAN_NODE
}

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

def _get_degree_info(degree: float) -> dict:
    degree = degree % 360
    sign_idx = int(degree // 30)
    return {
        "sign": ZODIAC_SIGNS[sign_idx],
        "degree_in_sign": round(degree % 30, 2),
        "absolute_degree": round(degree, 4)
    }

def _calc_planet_degree(julday: float, p_id: int) -> float:
    res, _ = swe.calc_ut(julday, p_id, swe.FLG_MOSEPH)
    return res[0]

def _calc_chiron_degree(julday: float) -> float:
    try:
        res, _ = swe.calc_ut(julday, swe.CHIRON, swe.FLG_SWIEPH)
        return res[0]
    except Exception:
        return 0.0

class NatalRequest(BaseModel):
    year: int
    month: int
    day: int
    hour: int
    minute: int
    lat: float
    lon: float
    timezone: str = "Asia/Bangkok"

@app.get("/")
def read_root():
    return {"status": "Astro Engine is running"}

@app.get("/transit")
def get_realtime_transit():
    try:
        now_utc = datetime.now(pytz.utc)
        decimal_hour = now_utc.hour + (now_utc.minute / 60.0) + (now_utc.second / 3600.0)
        julday = swe.julday(now_utc.year, now_utc.month, now_utc.day, decimal_hour)

        transits = {}
        for name, p_id in PLANETS.items():
            deg = _calc_planet_degree(julday, p_id)
            transits[name] = _get_degree_info(deg)

        # คำนวณ Chiron
        chiron_deg = _calc_chiron_degree(julday)
        if chiron_deg > 0:
            transits['Chiron'] = _get_degree_info(chiron_deg)

        transits['South_Node'] = _get_degree_info((transits['North_Node']['absolute_degree'] + 180) % 360)
        return {"timestamp_utc": now_utc.isoformat(), "transits": transits}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transit Error: {str(e)}")

@app.post("/natal")
def get_birth_chart(req: NatalRequest):
    try:
        local_tz = pytz.timezone(req.timezone)
        local_dt = local_tz.localize(datetime(req.year, req.month, req.day, req.hour, req.minute))
        utc_dt = local_dt.astimezone(pytz.utc)

        decimal_hour = utc_dt.hour + (utc_dt.minute / 60.0) + (utc_dt.second / 3600.0)
        julday = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, decimal_hour)

        planets = {}
        for name, p_id in PLANETS.items():
            deg = _calc_planet_degree(julday, p_id)
            planets[name] = _get_degree_info(deg)

        chiron_deg = _calc_chiron_degree(julday)
        if chiron_deg > 0:
            planets['Chiron'] = _get_degree_info(chiron_deg)

        planets['South_Node'] = _get_degree_info((planets['North_Node']['absolute_degree'] + 180) % 360)

        houses, ascmc = swe.houses(julday, req.lat, req.lon, b'P')
        planets['ASC'] = _get_degree_info(ascmc[0])
        planets['MC'] = _get_degree_info(ascmc[1])

        house_cusps = {f"House_{i+1}": _get_degree_info(houses[i]) for i in range(12)}

        return {
            "utc_time": utc_dt.isoformat(),
            "planets": planets,
            "houses": house_cusps
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Natal Error: {str(e)}")
