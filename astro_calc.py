import swisseph as swe
from datetime import datetime, timezone

# พิกัดภูมิศาสตร์จังหวัดหลักในไทย (Latitude, Longitude)
LOCATION_COORDS = {
    "กรุงเทพมหานคร": (13.7563, 100.5018),
    "เชียงใหม่": (18.7883, 98.9853),
    "ขอนแก่น": (16.4322, 102.8236),
    "ชลบุรี": (13.3611, 100.9847),
    "สงขลา": (7.1988, 100.5951),
    "นครราชสีมา": (14.9799, 102.0978),
    "ภูเก็ต": (7.8804, 98.3923),
    "นนทบุรี": (13.8591, 100.5217),
    "ปทุมธานี": (14.0208, 100.5250),
    "สมุทรปราการ": (13.5991, 100.5998)
}

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

def get_coordinates(location_name: str) -> tuple:
    """แปลงชื่อจังหวัดเป็นพิกัด (latitude, longitude)"""
    return LOCATION_COORDS.get(location_name, (13.7563, 100.5018))

def deg_to_dms(deg_float: float) -> dict:
    """แปลงองศา Decimal เป็น ราศี องศา ลิปดา (DMS)"""
    deg_float = deg_float % 360
    d = int(deg_float)
    m = int((deg_float - d) * 60)
    s = int((((deg_float - d) * 60) - m) * 60)
    sign_idx = d // 30
    deg_in_sign = d % 30
    return {
        "degree_total": round(deg_float, 4),
        "sign": ZODIAC_SIGNS[sign_idx],
        "degree_in_sign": deg_in_sign,
        "minute": m,
        "second": s,
        "dms_str": f"{deg_in_sign}°{ZODIAC_SIGNS[sign_idx]} {m}'{s}\""
    }

def get_realtime_transits() -> dict:
    """ข้อ 1: คำนวณตำแหน่งดาวจร Real-time ปัจจุบัน (UTC) ทั้ง 10 ดาวหลัก และ 8 ดาวทิพย์ยูเรเนียน"""
    now = datetime.now(timezone.utc)
    jul_day = swe.julday(now.year, now.month, now.day, now.hour + now.minute / 60.0 + now.second / 3600.0)
    
    planets = {
        "Sun": swe.SUN, "Moon": swe.MOON, "Mercury": swe.MERCURY,
        "Venus": swe.VENUS, "Mars": swe.MARS, "Jupiter": swe.JUPITER,
        "Saturn": swe.SATURN, "Uranus": swe.URANUS, "Neptune": swe.NEPTUNE,
        "Pluto": swe.PLUTO, "Cupido": swe.CUPIDO, "Hades": swe.HADES,
        "Zeus": swe.ZEUS, "Kronos": swe.KRONOS, "Apollon": swe.APOLLON,
        "Admetos": swe.ADMETOS, "Vulkanus": swe.VULCANUS, "Poseidon": swe.POSEIDON
    }
    
    transits = {}
    for name, pid in planets.items():
        res, _ = swe.calc_ut(jul_day, pid)
        deg = float(res[0])
        dms = deg_to_dms(deg)
        transits[name] = {
            "deg_dec": round(deg, 4),
            "sign": dms["sign"],
            "dms": dms["dms_str"]
        }
    return transits

def calculate_natal_chart(day: int, month: int, year_buddhist: int, hour: int, minute: int, location_name: str = "กรุงเทพมหานคร") -> dict:
    """ข้อ 2: คำนวณองศาดาวกำเนิด ลัคนา MC และเรือนชะตา Placidus สำหรับพยากรณ์ 7 หมวดพัฒนาศักยภาพ"""
    year_gregorian = year_buddhist - 543 if year_buddhist > 2400 else year_buddhist
    lat, lon = get_coordinates(location_name)
    
    hour_utc = hour - 7  # แปลงเวลาไทย (UTC+7) เป็น UTC
    jul_day = swe.julday(year_gregorian, month, day, hour_utc + minute / 60.0)
    
    planets = {
        "Sun": swe.SUN, "Moon": swe.MOON, "Mercury": swe.MERCURY,
        "Venus": swe.VENUS, "Mars": swe.MARS, "Jupiter": swe.JUPITER,
        "Saturn": swe.SATURN, "Uranus": swe.URANUS, "Neptune": swe.NEPTUNE,
        "Pluto": swe.PLUTO, "Chiron": swe.CHIRON, "NorthNode": swe.MEAN_NODE,
        "Cupido": swe.CUPIDO, "Hades": swe.HADES, "Zeus": swe.ZEUS,
        "Kronos": swe.KRONOS, "Apollon": swe.APOLLON, "Admetos": swe.ADMETOS,
        "Vulkanus": swe.VULCANUS, "Poseidon": swe.POSEIDON
    }
    
    natal_planets = {}
    for name, pid in planets.items():
        res, _ = swe.calc_ut(jul_day, pid)
        deg = float(res[0])
        dms = deg_to_dms(deg)
        natal_planets[name] = {
            "deg_dec": round(deg, 4),
            "sign": dms["sign"],
            "dms": dms["dms_str"]
        }
    
    cusps, ascmc = swe.houses(jul_day, lat, lon, b'P')
    asc_deg = float(ascmc[0])
    mc_deg = float(ascmc[1])
    
    angles = {
        "ASC": {"deg_dec": round(asc_deg, 4), "dms": deg_to_dms(asc_deg)["dms_str"]},
        "MC": {"deg_dec": round(mc_deg, 4), "dms": deg_to_dms(mc_deg)["dms_str"]}
    }
    
    house_cusps = {}
    for i in range(12):
        c_deg = float(cusps[i])
        house_cusps[f"House_{i+1}"] = {
            "deg_dec": round(c_deg, 4),
            "dms": deg_to_dms(c_deg)["dms_str"]
        }
        
    return {
        "user_info": {
            "dob": f"{day}/{month}/{year_buddhist}",
            "time": f"{hour:02d}:{minute:02d}",
            "location": location_name,
            "lat": lat, "lon": lon
        },
        "planets": natal_planets,
        "angles": angles,
        "houses": house_cusps
    }

# ALIAS MAPPING FOR MAIN.PY
calculate_chart = calculate_natal_chart
calculate_current_transits = get_realtime_transits
