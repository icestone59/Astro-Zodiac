import datetime
import swisseph as swe
from geopy.geocoders import Nominatim

# พจนานุกรมสำรองพิกัดจังหวัดหลัก ป้องกัน KeyError / Geopy Timeout
THAI_PROVINCE_COORDS = {
    "กรุงเทพมหานคร": (13.7563, 100.5018, "Bangkok", "Thailand"),
    "กรุงเทพ": (13.7563, 100.5018, "Bangkok", "Thailand"),
    "เชียงใหม่": (18.7883, 98.9853, "Chiang Mai", "Thailand"),
    "ภูเก็ต": (7.8804, 98.3923, "Phuket", "Thailand"),
    "ชลบุรี": (13.3611, 100.9847, "Chon Buri", "Thailand"),
    "ขอนแก่น": (16.4322, 102.8236, "Khon Kaen", "Thailand"),
    "สงขลา": (7.1988, 100.5951, "Songkhla", "Thailand"),
}

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

def get_coordinates(location_name):
    """แปลงชื่อสถานที่เกิดเป็น (lat, lon, city, country) คืนค่าครบ 4 ตัวแปร"""
    if not location_name:
        return 13.7563, 100.5018, "Bangkok", "Thailand"
        
    clean_name = str(location_name).strip()

    if clean_name in THAI_PROVINCE_COORDS:
        return THAI_PROVINCE_COORDS[clean_name]

    try:
        geolocator = Nominatim(user_agent="evolutionary_astro_app_v3", timeout=5)
        query_str = f"{clean_name}, Thailand" if "Thailand" not in clean_name else clean_name
        location = geolocator.geocode(query_str, addressdetails=True)
        
        if location:
            address = location.raw.get('address', {})
            city = address.get('city') or address.get('state') or address.get('province') or clean_name
            country = address.get('country', 'Thailand')
            return location.latitude, location.longitude, city, country
    except Exception:
        pass

    return 13.7563, 100.5018, clean_name, "Thailand"

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

def calculate_chart(birth_dt_utc, lat, lon, transit_dt_utc=None):
    """คำนวณตำแหน่งองศาดาวเกิด ดาวจร Real-time และ House Rulers จาก Swiss Ephemeris"""
    swe.set_ephe_path('')
    
    # 1. คำนวณ Julian Day ดวงเกิด
    jul_day_natal = swe.julday(
        birth_dt_utc.year, birth_dt_utc.month, birth_dt_utc.day,
        birth_dt_utc.hour + birth_dt_utc.minute / 60.0 + birth_dt_utc.second / 3600.0
    )

    # คำนวณเรือนชะตา (Placidus System)
    cusps, ascmc = swe.houses(jul_day_natal, lat, lon, b'P')
    house_cusps = list(cusps)
    
    asc_deg, mc_deg = ascmc[0], ascmc[1]
    dsc_deg = (asc_deg + 180) % 360
    
    asc_sign, asc_orb = get_zodiac_sign(asc_deg)
    dsc_sign, dsc_orb = get_zodiac_sign(dsc_deg)
    mc_sign, mc_orb = get_zodiac_sign(mc_deg)

    # 2. คำนวณตำแหน่งดาวเกิด (Natal Planets)
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

    # 3. คำนวณ Ruler Mapping ของทุกมุมและเรือนชะตา
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

    # 4. คำนวณดาวจร Real-time ณ เวลาปัจจุบัน
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
