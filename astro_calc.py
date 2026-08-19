import os
import math
import urllib.request
import datetime
import swisseph as swe
from geopy.geocoders import Nominatim

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EPHE_DIR = os.path.join(BASE_DIR, 'ephe')
os.makedirs(EPHE_DIR, exist_ok=True)

NEEDED_SE1_FILES = ['seas_18.se1', 'sepl_18.se1', 'semo_18.se1']
ASTRO_FTP_URL = 'https://www.astro.com/ftp/swisseph/ephe/'

def download_missing_ephe_files():
    for fname in NEEDED_SE1_FILES:
        fpath = os.path.join(EPHE_DIR, fname)
        if not os.path.exists(fpath):
            try:
                urllib.request.urlretrieve(ASTRO_FTP_URL + fname, fpath)
            except Exception:
                pass

download_missing_ephe_files()
swe.set_ephe_path(EPHE_DIR)

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
    clean = str(location_name).strip()
    if clean in THAI_PROVINCES:
        lat, lon = THAI_PROVINCES[clean]
        return lat, lon, clean
    try:
        geolocator = Nominatim(user_agent="evolutionary_astro_engine_v12", timeout=5)
        query = f"{clean}, Thailand" if "Thailand" not in clean else clean
        loc = geolocator.geocode(query)
        if loc:
            return loc.latitude, loc.longitude, clean
    except Exception:
        pass
    return 13.7563, 100.5018, clean

def format_degree(deg):
    deg_norm = float(deg) % 360.0
    idx = int(deg_norm // 30) % 12  # ป้องกัน Index Out of Range
    rem_deg = deg_norm % 30
    d = int(rem_deg)
    m = int((rem_deg - d) * 60)
    return ZODIAC_NAMES[idx], f"{d}°{m:02d}'"

def get_house_of_position(deg, house_cusps_12):
    deg_norm = float(deg) % 360.0
    for i in range(12):
        c_start = house_cusps_12[i]
        c_end = house_cusps_12[(i + 1) % 12]
        if c_start < c_end:
            if c_start <= deg_norm < c_end:
                return i + 1
        else:
            if deg_norm >= c_start or deg_norm < c_end:
                return i + 1
    return 1

def generate_chart_svg(birth_degrees):
    svg = ['<svg viewBox="0 0 300 300" class="w-full h-full">']
    svg.append('<circle cx="150" cy="150" r="140" fill="none" stroke="#6b21a8" stroke-width="2"/>')
    svg.append('<circle cx="150" cy="150" r="100" fill="none" stroke="#c084fc" stroke-width="1" stroke-dasharray="2 2"/>')
    svg.append('<circle cx="150" cy="150" r="60" fill="#f3e8ff" stroke="#a855f7" stroke-width="1"/>')
    
    for i in range(12):
        angle = math.radians(i * 30)
        x1 = 150 + 100 * math.cos(angle)
        y1 = 150 + 100 * math.sin(angle)
        x2 = 150 + 140 * math.cos(angle)
        y2 = 150 + 140 * math.sin(angle)
        svg.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#e9d5ff" stroke-width="1.5"/>')

    for name, data in birth_degrees.items():
        if "degree_raw" in data:
            deg = data["degree_raw"]
            rad = math.radians(deg - 90)
            px = 150 + 120 * math.cos(rad)
            py = 150 + 120 * math.sin(rad)
            svg.append(f'<circle cx="{px}" cy="{py}" r="4" fill="#7e22ce"/>')
            svg.append(f'<text x="{px}" y="{py-6}" font-size="8" font-weight="bold" fill="#3b0764" text-anchor="middle">{name[:2]}</text>')

    svg.append('</svg>')
    return "".join(svg)

def calculate_natal_degrees(jul_day_natal, lat, lon):
    cusps, ascmc = swe.houses(jul_day_natal, lat, lon, b'P')
    # ดึงค่าเฉพาะ Cusp 1 ถึง 12 (ตัด Index 0 ออก)
    house_cusps_12 = [float(c) % 360.0 for c in cusps[1:13]]
    
    degrees = {}
    asc_deg, mc_deg = ascmc[0] % 360.0, ascmc[1] % 360.0
    asc_sign, asc_fmt = format_degree(asc_deg)
    mc_sign, mc_fmt = format_degree(mc_deg)
    
    degrees["ASC"] = {"sign": asc_sign, "formatted": asc_fmt, "degree_raw": asc_deg, "house": 1}
    degrees["MC"] = {"sign": mc_sign, "formatted": mc_fmt, "degree_raw": mc_deg, "house": 10}

    for name, pid in PLANET_IDS.items():
        try:
            res, _ = swe.calc_ut(jul_day_natal, pid, swe.FLG_SWIEPH)
        except swe.Error:
            res, _ = swe.calc_ut(jul_day_natal, pid, swe.FLG_MOSEPH)
            
        lon_deg = res[0] % 360.0
        is_retro = res[3] < 0
        sign, formatted = format_degree(lon_deg)
        house = get_house_of_position(lon_deg, house_cusps_12)
        degrees[name] = {
            "sign": sign,
            "formatted": formatted,
            "degree_raw": lon_deg,
            "is_retrograde": is_retro,
            "house": house
        }

    return degrees, house_cusps_12

def calculate_current_transits(house_cusps_12=None):
    now = datetime.datetime.now(datetime.timezone.utc)
    jul_day_transit = swe.julday(now.year, now.month, now.day, now.hour + now.minute / 60.0)
    transits = {}
    for name, pid in PLANET_IDS.items():
        try:
            res, _ = swe.calc_ut(jul_day_transit, pid, swe.FLG_SWIEPH)
        except swe.Error:
            res, _ = swe.calc_ut(jul_day_transit, pid, swe.FLG_MOSEPH)
            
        lon_deg = res[0] % 360.0
        is_retro = res[3] < 0
        sign, formatted = format_degree(lon_deg)
        house = get_house_of_position(lon_deg, house_cusps_12) if house_cusps_12 else 1
        transits[name] = {
            "sign": sign,
            "formatted": formatted,
            "degree_raw": lon_deg,
            "is_retrograde": is_retro,
            "house_in_natal": house
        }
    return transits

def calculate_chart(birth_dt_utc, lat, lon):
    jul_day_natal = swe.julday(
        birth_dt_utc.year, birth_dt_utc.month, birth_dt_utc.day,
        birth_dt_utc.hour + birth_dt_utc.minute / 60.0 + birth_dt_utc.second / 3600.0
    )

    birth_degrees, house_cusps_12 = calculate_natal_degrees(jul_day_natal, lat, lon)
    transit_degrees = calculate_current_transits(house_cusps_12)

    ruler_mapping = {}
    for h_num in range(1, 13):
        h_sign, _ = format_degree(house_cusps_12[h_num - 1])
        r_planet = ZODIAC_RULERS[h_sign]
        r_pos = birth_degrees.get(r_planet, {})
        ruler_mapping[f"House_{h_num}"] = {
            "sign": h_sign,
            "ruler_planet": r_planet,
            "ruler_pos": f"{r_planet} in {r_pos.get('sign', '')} {r_pos.get('formatted', '')} (House {r_pos.get('house', '')})" if r_pos else "N/A"
        }

    chart_svg = generate_chart_svg(birth_degrees)

    return {
        "birth_chart_degrees": birth_degrees,
        "transit_degrees": transit_degrees,
        "ruler_mapping": ruler_mapping,
        "chart_svg": chart_svg
    }
