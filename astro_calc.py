import os
import math
import logging
import urllib.request
import datetime
import swisseph as swe
from geopy.geocoders import Nominatim

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AstroEngine")

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
            except Exception as e:
                logger.warning(f"Failed to download {fname}: {e}")

download_missing_ephe_files()
swe.set_ephe_path(EPHE_DIR)

THAI_PROVINCES = {
    "กรุงเทพมหานคร": (13.7563, 100.5018), "กรุงเทพ": (13.7563, 100.5018),
    "นนทบุรี": (13.8591, 100.5217), "ปทุมธานี": (14.0208, 100.5250),
    "สมุทรปราการ": (13.5991, 100.5968), "สมุทรสาคร": (13.5475, 100.2744),
    "นครปฐม": (13.8196, 100.0622), "อยุธยา": (14.3532, 100.5684),
    "เชียงใหม่": (18.7883, 98.9853), "เชียงราย": (19.9076, 99.8325),
    "ภูเก็ต": (7.8804, 98.3923), "ขอนแก่น": (16.4322, 102.8236),
    "ชลบุรี": (13.3611, 100.9847), "สงขลา": (7.1988, 100.5951)
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

ZODIAC_SYMBOLS = ["♈", "♉", "♊", "♋", "♌", "♍", "♎", "♏", "♐", "♑", "♒", "♓"]

PLANET_SYMBOLS = {
    "Sun": "☉", "Moon": "☽", "Mercury": "☿", "Venus": "♀",
    "Mars": "♂", "Jupiter": "♃", "Saturn": "♄", "Uranus": "♅",
    "Neptune": "♆", "Pluto": "♇", "Chiron": "⚷", "North_Node": "☊",
    "ASC": "ASC", "MC": "MC"
}

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
        geolocator = Nominatim(user_agent="evolutionary_astro_engine_v15", timeout=5)
        query = f"{clean}, Thailand" if "Thailand" not in clean else clean
        loc = geolocator.geocode(query)
        if loc:
            return loc.latitude, loc.longitude, clean
    except Exception:
        pass
    return 13.7563, 100.5018, clean

def format_degree(deg):
    deg_norm = float(deg) % 360.0
    idx = int(deg_norm // 30) % 12
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

def generate_chart_svg(birth_degrees, house_cusps_12):
    """สร้าง SVG วงกลมดวงชะตา พร้อมอัลกอริทึมแก้ปัญหาข้อความซ้อนทับ"""
    cx, cy = 200, 200
    r_outer, r_zodiac, r_inner, r_core = 180, 155, 115, 60
    asc_deg = birth_degrees.get("ASC", {}).get("degree_raw", 0.0)

    svg = ['<svg viewBox="0 0 400 400" class="w-full h-full font-sans" xmlns="http://www.w3.org/2000/svg">']
    svg.append('<defs><style>.astro-sym { font-family: "Segoe UI Symbol", "Arial Unicode MS", sans-serif; }</style></defs>')
    
    # วงกลมฐาน
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r_outer}" fill="#FAF5FF" stroke="#6B21A8" stroke-width="2"/>')
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r_zodiac}" fill="#FFFFFF" stroke="#9333EA" stroke-width="1.5"/>')
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r_inner}" fill="#FAF5FF" stroke="#C084FC" stroke-width="1"/>')
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r_core}" fill="#F3E8FF" stroke="#A855F7" stroke-width="1.5"/>')

    # วาดสัญลักษณ์ 12 ราศีตรงวงแหวนนอก (Zodiac Ring)
    for i in range(12):
        z_start_deg = i * 30.0
        # ปรับมุมให้ ASC อยู่ทิศตะวันตก (9 o'clock / 180°)
        angle_chart = (180.0 - (z_start_deg + 15.0 - asc_deg)) % 360.0
        rad = math.radians(angle_chart)
        zx = cx + (r_outer - 12.5) * math.cos(rad)
        zy = cy - (r_outer - 12.5) * math.sin(rad)
        svg.append(f'<text x="{zx}" y="{zy+5}" font-size="14" font-weight="bold" fill="#581C87" text-anchor="middle" class="astro-sym">{ZODIAC_SYMBOLS[i]}</text>')

    # วาดเส้นแบ่งเรือนชะตา (House Cusps Lines)
    for h_idx, c_deg in enumerate(house_cusps_12):
        angle_chart = (180.0 - (c_deg - asc_deg)) % 360.0
        rad = math.radians(angle_chart)
        x1 = cx + r_core * math.cos(rad)
        y1 = cy - r_core * math.sin(rad)
        x2 = cx + r_zodiac * math.cos(rad)
        y2 = cy - r_zodiac * math.sin(rad)
        stroke_w = "2" if h_idx in [0, 3, 6, 9] else "0.8"
        stroke_c = "#6B21A8" if h_idx in [0, 3, 6, 9] else "#E9D5FF"
        svg.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke_c}" stroke-width="{stroke_w}"/>')

    # จัดกลุ่มดาวเพื่อป้องกันการซ้อนทับ (Collision Detection & Offset)
    planet_list = []
    for name, data in birth_degrees.items():
        if "degree_raw" in data:
            deg = data["degree_raw"]
            angle_chart = (180.0 - (deg - asc_deg)) % 360.0
            planet_list.append({
                "name": name,
                "degree": deg,
                "angle_chart": angle_chart,
                "formatted": data.get("formatted", ""),
                "symbol": PLANET_SYMBOLS.get(name, name[:2])
            })

    # เรียงลำดับดาวตามมุมบน SVG
    planet_list.sort(key=lambda p: p["angle_chart"])

    # คำนวณระยะรัศมีสลับระดับ (Radial Staggering) เพื่อหลบดาวที่องศาใกล้กัน
    radii_levels = [r_inner + 18, r_inner + 30, r_inner + 6]
    for idx, p in enumerate(planet_list):
        # สุ่ม/สลับระดับรัศมีหากดาวอยู่ใกล้กันน้อยกว่า 8 องศา
        level = idx % len(radii_levels)
        if idx > 0 and abs(p["angle_chart"] - planet_list[idx-1]["angle_chart"]) < 8.0:
            level = (planet_list[idx-1]["level"] + 1) % len(radii_levels)
        p["level"] = level
        p["radius"] = radii_levels[level]

    # วาดจุดและป้ายชื่อดาว
    for p in planet_list:
        rad = math.radians(p["angle_chart"])
        # จุดพิกัดจริงบนเส้นวงกลม
        px = cx + r_zodiac * math.cos(rad)
        py = cy - r_zodiac * math.sin(rad)
        # พิกัดป้ายข้อความที่ขยับรัศมีหลบ
        tx = cx + p["radius"] * math.cos(rad)
        ty = cy - p["radius"] * math.sin(rad)

        svg.append(f'<circle cx="{px}" cy="{py}" r="2.5" fill="#7E22CE"/>')
        svg.append(f'<line x1="{px}" y1="{py}" x2="{tx}" y2="{ty}" stroke="#C084FC" stroke-width="0.5" stroke-dasharray="1 1"/>')
        
        lbl_text = f'{p["symbol"]} {p["formatted"].split("°")[0]}°'
        svg.append(f'<text x="{tx}" y="{ty+3}" font-size="9" font-weight="bold" fill="#3B0764" text-anchor="middle" class="astro-sym">{lbl_text}</text>')

    svg.append('</svg>')
    return "".join(svg)

def calculate_natal_degrees(jul_day_natal, lat, lon):
    cusps, ascmc = swe.houses(jul_day_natal, lat, lon, b'P')
    house_cusps_12 = [float(c) % 360.0 for c in (cusps[1:13] if len(cusps) >= 13 else cusps[:12])]

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

    return {
        "birth_chart_degrees": birth_degrees,
        "transit_degrees": transit_degrees,
        "ruler_mapping": ruler_mapping,
        "chart_svg": generate_chart_svg(birth_degrees, house_cusps_12)
    }
