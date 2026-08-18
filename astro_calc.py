import datetime
import swisseph as swe
from geopy.geocoders import Nominatim

# บังคับใช้ Moshier Analytical Model ไม่พึ่งพาไฟล์ .se1 ภายนอก
EPHE_FLAG = swe.FLG_MOSEPH

THAI_PROVINCES = {
    "กรุงเทพมหานคร": (13.7563, 100.5018), "กรุงเทพ": (13.7563, 100.5018),
    "นนทบุรี": (13.8591, 100.5217), "ปทุมธานี": (14.0208, 100.5250),
    "สมุทรปราการ": (13.5991, 100.5968), "สมุทรสาคร": (13.5475, 100.2744),
    "นครปฐม": (13.8196, 100.0622), "อยุธยา": (14.3532, 100.5684),
    "เชียงใหม่": (18.7883, 98.9853), "เชียงราย": (19.9076, 99.8325),
    "ภูเก็ต": (7.8804, 98.3923), "ขอนแก่น": (16.4322, 102.8236),
    "ชลบุรี": (13.3611, 100.9847), "สงขลา": (7.1988, 100.5951),
    "หาดใหญ่": (7.0086, 100.4747), "สุราษฎร์ธานี": (9.1382, 99.3217),
    "นครราชสีมา": (14.9799, 102.0978), "อุดรธานี": (17.4138, 102.7872),
    "อุบลราชธานี": (15.2287, 104.8594)
}

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
    "Pluto": swe.PLUTO, "Chiron": swe.CHIRON, "North_Node": swe.MEAN_NODE
}

def get_coordinates(location_name):
    if not location_name:
        return 13.7563, 100.5018, "กรุงเทพมหานคร"
    clean_name = str(location_name).strip()
    if clean_name in THAI_PROVINCES:
        lat, lon = THAI_PROVINCES[clean_name]
        return lat, lon, clean_name

    try:
        geolocator = Nominatim(user_agent="evolutionary_astro_engine_v7", timeout=5)
        query = f"{clean_name}, Thailand" if "Thailand" not in clean_name else clean_name
        loc = geolocator.geocode(query)
        if loc:
            return loc.latitude, loc.longitude, clean_name
    except Exception:
        pass
    return 13.7563, 100.5018, clean_name

def format_degree(deg):
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

def calculate_natal_degrees(jul_day_natal, lat, lon):
    cusps, ascmc = swe.houses(jul_day_natal, lat, lon, b'P')
    house_cusps = list(cusps)
    
    degrees = {}
    asc_deg, mc_deg = ascmc[0], ascmc[1]
    
    asc_sign, asc_formatted = format_degree(asc_deg)
    mc_sign, mc_formatted = format_degree(mc_deg)
    
    degrees["ASC"] = {"sign": asc_sign, "formatted": asc_formatted, "degree_raw": asc_deg, "house": 1}
    degrees["MC"] = {"sign": mc_sign, "formatted": mc_formatted, "degree_raw": mc_deg, "house": 10}

    for name, pid in PLANET_IDS.items():
        res, _ = swe.calc_ut(jul_day_natal, pid, EPHE_FLAG)
        lon_deg = res[0]
        is_retro = res[3] < 0
        sign, formatted = format_degree(lon_deg)
        house = get_house_of_position(lon_deg, house_cusps)
        degrees[name] = {
            "sign": sign,
            "formatted": formatted,
            "degree_raw": lon_deg,
            "is_retrograde": is_retro,
            "house": house
        }
    return degrees, house_cusps

def calculate_current_transits(house_cusps=None):
    now = datetime.datetime.now(datetime.timezone.utc)
    jul_day_transit = swe.julday(now.year, now.month, now.day, now.hour + now.minute / 60.0)
    transits = {}
    for name, pid in PLANET_IDS.items():
        res, _ = swe.calc_ut(jul_day_transit, pid, EPHE_FLAG)
        lon_deg = res[0]
        is_retro = res[3] < 0
        sign, formatted = format_degree(lon_deg)
        
        house_in_natal = get_house_of_position(lon_deg, house_cusps) if house_cusps else 1
        transits[name] = {
            "sign": sign,
            "formatted": formatted,
            "degree_raw": lon_deg,
            "is_retrograde": is_retro,
            "house_in_natal": house_in_natal
        }
    return transits

def calculate_chart(birth_dt_utc, lat, lon):
    swe.set_ephe_path('')
    jul_day_natal = swe.julday(
        birth_dt_utc.year, birth_dt_utc.month, birth_dt_utc.day,
        birth_dt_utc.hour + birth_dt_utc.minute / 60.0 + birth_dt_utc.second / 3600.0
    )

    birth_degrees, house_cusps = calculate_natal_degrees(jul_day_natal, lat, lon)
    transit_degrees = calculate_current_transits(house_cusps)

    # Ruler mapping
    ruler_mapping = {}
    for h_num in range(1, 13):
        h_sign, _ = format_degree(house_cusps[h_num - 1])
        r_planet = ZODIAC_RULERS[h_sign]
        ruler_pos = birth_degrees.get(r_planet, {})
        ruler_mapping[f"House_{h_num}"] = {
            "sign": h_sign,
            "ruler_planet": r_planet,
            "ruler_pos": f"{r_planet} in {ruler_pos.get('sign')} {ruler_pos.get('formatted')} (House {ruler_pos.get('house')})"
        }

    return {
        "birth_chart_degrees": birth_degrees,
        "transit_degrees": transit_degrees,
        "ruler_mapping": ruler_mapping
    }
