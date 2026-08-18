import datetime
import swisseph as swe
from geopy.geocoders import Nominatim

# 1. ฟังก์ชันแปลงสถานที่เกิดเป็นพิกัด lat, lon ที่ main.py เรียกหา
def get_coordinates(location_name):
    """แปลงชื่อเมือง/สถานที่เกิดเป็น พิกัด (lat, lon)"""
    try:
        geolocator = Nominatim(user_agent="evolutionary_astro_app")
        location = geolocator.geocode(location_name)
        if location:
            return location.latitude, location.longitude
        return 13.7563, 100.5018  # ค่าเริ่มต้น กรุงเทพฯ หากหาไม่พบ
    except Exception:
        return 13.7563, 100.5018

# กำหนดเกษตรเจ้าเรือน (Rulers) ตามหลักโหราศาสตร์สากลวิวัฒนาการ
ZODIAC_RULERS = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury",
    "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury",
    "Libra": "Venus", "Scorpio": "Pluto", "Sagittarius": "Jupiter",
    "Capricorn": "Saturn", "Aquarius": "Uranus", "Pisces": "Neptune"
}

ZODIAC_NAMES = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

PLANET_IDS = {
    "Sun": swe.SUN, "Moon": swe.MOON, "Mercury": swe.MERCURY,
    "Venus": swe.VENUS, "Mars": swe.MARS, "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN, "Uranus": swe.URANUS, "Neptune": swe.NEPTUNE,
    "Pluto": swe.PLUTO, "Chiron": swe.CHIRON, "North Node": swe.MEAN_NODE
}

def get_zodiac_sign(deg):
    idx = int(deg // 30)
    rem_deg = deg % 30
    d = int(rem_deg)
    m = int((rem_deg - d) * 60)
    return ZODIAC_NAMES[idx], f"{d}°{m:02d}'"

def get_house_of_position(deg, house_cusps):
    for i in range(12):
        c_start = house_cusps[i]
        c_end = house_cusps[(i + 1) % 12]
        if c_start < c_end:
            if c_start <= deg < c_end:
                return i + 1
        else:
            if deg >= c_start or deg < c_end:
                return i + 1
    return 1

def calculate_chart_data(birth_dt_utc, lat, lon, transit_dt_utc=None):
    """คำนวณดวงเกิดและ Transit Real-time พร้อม Ruler Mapping"""
    swe.set_ephe_path('')
    
    # คำนวณ Julian Day ดวงเกิด
    jul_day_natal = swe.julday(
        birth_dt_utc.year, birth_dt_utc.month, birth_dt_utc.day,
        birth_dt_utc.hour + birth_dt_utc.minute / 60.0 + birth_dt_utc.second / 3600.0
    )

    cusps, ascmc = swe.houses(jul_day_natal, lat, lon, b'P')
    house_cusps = list(cusps)
    
    asc_deg, mc_deg = ascmc[0], ascmc[1]
    dsc_deg = (asc_deg + 180) % 360
    
    asc_sign, asc_orb = get_zodiac_sign(asc_deg)
    dsc_sign, dsc_orb = get_zodiac_sign(dsc_deg)
    mc_sign, mc_orb = get_zodiac_sign(mc_deg)

    # ตำแหน่งดาวเกิด (Natal)
    natal_planets = {}
    for name, pid in PLANET_IDS.items():
        res, _ = swe.calc_ut(jul_day_natal, pid)
        lon_deg = res[0]
        sign, orb = get_zodiac_sign(lon_deg)
        house = get_house_of_position(lon_deg, house_cusps)
        natal_planets[name] = {
            "degree_raw": lon_deg,
            "sign": sign,
            "orb": orb,
            "house": house,
            "formatted": f"{name} in {sign} {orb} (House {house})"
        }

    # คำนวณ Ruler Mapping
    ruler_mapping = {
        "ASC": {"sign": asc_sign, "ruler_planet": ZODIAC_RULERS[asc_sign], "ruler_pos": natal_planets[ZODIAC_RULERS[asc_sign]]["formatted"]},
        "DSC": {"sign": dsc_sign, "ruler_planet": ZODIAC_RULERS[dsc_sign], "ruler_pos": natal_planets[ZODIAC_RULERS[dsc_sign]]["formatted"]},
        "MC": {"sign": mc_sign, "ruler_planet": ZODIAC_RULERS[mc_sign], "ruler_pos": natal_planets[ZODIAC_RULERS[mc_sign]]["formatted"]}
    }

    for h_num in range(1, 13):
        h_sign, _ = get_zodiac_sign(house_cusps[h_num - 1])
        r_planet = ZODIAC_RULERS[h_sign]
        ruler_mapping[f"House_{h_num}"] = {
            "sign": h_sign,
            "ruler_planet": r_planet,
            "ruler_pos": natal_planets[r_planet]["formatted"]
        }

    # คำนวณ Transit Real-time
    if not transit_dt_utc:
        transit_dt_utc = datetime.datetime.now(datetime.timezone.utc)

    jul_day_transit = swe.julday(
        transit_dt_utc.year, transit_dt_utc.month, transit_dt_utc.day,
        transit_dt_utc.hour + transit_dt_utc.minute / 60.0
    )

    transit_planets = {}
    for name, pid in PLANET_IDS.items():
        res, _ = swe.calc_ut(jul_day_transit, pid)
        lon_deg = res[0]
        sign, orb = get_zodiac_sign(lon_deg)
        house = get_house_of_position(lon_deg, house_cusps)
        transit_planets[name] = {
            "sign": sign,
            "orb": orb,
            "house_in_natal": house,
            "formatted": f"Transit {name} in {sign} {orb} (House {house})"
        }

    return {
        "asc": f"ASC in {asc_sign} {asc_orb}",
        "dsc": f"DSC in {dsc_sign} {dsc_orb}",
        "mc": f"MC in {mc_sign} {mc_orb}",
        "natal_planets": natal_planets,
        "ruler_mapping": ruler_mapping,
        "transit_planets": transit_planets,
        "transit_timestamp_utc": transit_dt_utc.strftime("%Y-%m-%d %H:%M:%S UTC")
    }

# 2. ทำ Alias ชื่อฟังก์ชันให้ตรงกับที่ main.py เรียกใช้
calculate_chart = calculate_chart_data
