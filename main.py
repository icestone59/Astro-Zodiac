from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import pytz
import swisseph as swe

app = FastAPI(title="Astrology Engine API")

# กำหนดให้ใช้ Moshier Ephemeris (คำนวณในตัว ไม่ต้องใช้ไฟล์ .se1 บน Server)
CALC_FLAG = swe.FLG_MOSEPH

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
    return {
        "sign": ZODIAC_SIGNS[sign_idx],
        "degree_in_sign": round(degree % 30, 2),
        "absolute_degree": round(degree, 4)
    }

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
    """1. คำนวณ Real-time Transit ของดาวทุกดวง (UTC)"""
    try:
        now_utc = datetime.now(pytz.utc)
        decimal_hour = now_utc.hour + (now_utc.minute / 60.0) + (now_utc.second / 3600.0)
        julday = swe.julday(now_utc.year, now_utc.month, now_utc.day, decimal_hour)

        transits = {}
        for name, p_id in PLANETS.items():
            res, _ = swe.calc_ut(julday, p_id, CALC_FLAG)
            transits[name] = _get_degree_info(res[0])

        return {"timestamp_utc": now_utc.isoformat(), "transits": transits}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transit Error: {str(e)}")

@app.post("/natal")
def get_birth_chart(req: NatalRequest):
    """2. คำนวณ Birth Chart (ตำแหน่งดาว + เรือนชะตา)"""
    try:
        local_tz = pytz.timezone(req.timezone)
        local_dt = local_tz.localize(datetime(req.year, req.month, req.day, req.hour, req.minute))
        utc_dt = local_dt.astimezone(pytz.utc)
        
        decimal_hour = utc_dt.hour + (utc_dt.minute / 60.0) + (utc_dt.second / 3600.0)
        julday = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, decimal_hour)

        # คำนวณองศาดาว
        planets = {}
        for name, p_id in PLANETS.items():
            res, _ = swe.calc_ut(julday, p_id, CALC_FLAG)
            planets[name] = _get_degree_info(res[0])

        # คำนวณ Houses ระบบ Placidus (b'P')
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
