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
        geolocator = Nominatim(user_agent="evolutionary_astro_engine_v17", timeout=5)
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
    return ZODIAC_NAMES[idx], f"{rem_deg:.1f}°", rem_deg

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
    cx, cy = 250, 250
    r_outer, r_zodiac, r_inner, r_core = 230, 195, 145, 75

    svg = ['<svg viewBox="0 0 500 500" class="w-full h-full font-sans" xmlns="http://www.w3.org/2000/svg">']
    svg.append('<defs>')
    svg.append('<linearGradient id="goldGrad" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#FDE047"/><stop offset="100%" stop-color="#D97706"/></linearGradient>')
    svg.append('<linearGradient id="purpleBg" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#2E1065"/><stop offset="100%" stop-color="#1E1B4B"/></linearGradient>')
    svg.append('<style>.astro-text { font-family: system-ui, -apple-system, sans-serif; paint-order: stroke fill; stroke-linecap: round; stroke-linejoin: round; }</style>')
    svg.append('</defs>')

    # วงกลมพื้นหลังและโครงสร้างดวง
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r_outer}" fill="url(#purpleBg)" stroke="url(#goldGrad)" stroke-width="3"/>')
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r_zodiac}" fill="#3B0764" stroke="#7C3AED" stroke-width="2"/>')
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r_inner}" fill="#2E1065" stroke="url(#goldGrad)" stroke-width="1.5"/>')
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r_core}" fill="#1E1B4B" stroke="#7C3AED" stroke-width="2"/>')

    # 📌 คำนวณให้ 0° ราศีเมษ (Aries) ตั้งตรงที่ทิศเหนือ (12 o'clock / 270° SVG)
    def deg_to_svg_angle(deg):
        return (270.0 - deg) % 360.0

    # วาดสัญลักษณ์ 12 ราศีและเส้นแบ่งราศี
    for i in range(12):
        z_start = i * 30.0
        z_mid = z_start + 15.0
        
        # เส้นแบ่งราศี
        l_rad = math.radians(deg_to_svg_angle(z_start))
        lx1 = cx + r_zodiac * math.cos(l_rad)
        ly1 = cy + r_zodiac * math.sin(l_rad)
        lx2 = cx + r_outer * math.cos(l_rad)
        ly2 = cy + r_outer * math.sin(l_rad)
        svg.append(f'<line x1="{lx1}" y1="{ly1}" x2="{lx2}" y2="{ly2}" stroke="url(#goldGrad)" stroke-width="1.5"/>')

        # สัญลักษณ์ราศี
        s_rad = math.radians(deg_to_svg_angle(z_mid))
        zx = cx + (r_outer - 17.5) * math.cos(s_rad)
        zy = cy + (r_outer - 17.5) * math.sin(s_rad)
        svg.append(f'<text x="{zx}" y="{zy+6}" font-size="18" font-weight="bold" fill="url(#goldGrad)" text-anchor="middle" class="astro-text">{ZODIAC_SYMBOLS[i]}</text>')

    # วาดเส้นแบ่งเรือนชะตาและป้าย H1-H12
    for h_idx in range(12):
        c_deg = house_cusps_12[h_idx]
        next_c_deg = house_cusps_12[(h_idx + 1) % 12]
        
        rad = math.radians(deg_to_svg_angle(c_deg))
        x1 = cx + r_core * math.cos(rad)
        y1 = cy + r_core * math.sin(rad)
        x2 = cx + r_zodiac * math.cos(rad)
        y2 = cy + r_zodiac * math.sin(rad)
        
        is_cardinal = h_idx in [0, 3, 6, 9]
        stroke_c = "url(#goldGrad)" if is_cardinal else "#8B5CF6"
        stroke_w = "2.5" if is_cardinal else "1"
        svg.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke_c}" stroke-width="{stroke_w}"/>')

        # กำกับเลขเรือนชะตา (H1-H12)
        diff = (next_c_deg - c_deg) % 360.0
        h_mid_deg = (c_deg + diff / 2.0) % 360.0
        h_rad = math.radians(deg_to_svg_angle(h_mid_deg))
        hx = cx + (r_core + 22) * math.cos(h_rad)
        hy = cy + (r_core + 22) * math.sin(h_rad)
        svg.append(f'<text x="{hx}" y="{hy+4}" font-size="11" font-weight="bold" fill="#A7F3D0" stroke="#064E3B" stroke-width="3" text-anchor="middle" class="astro-text">H{h_idx+1}</text>')

    # คำนวณพิกัดดาว + กระจายรัศมีลดการซ้อนทับ
    planet_list = []
    for name, data in birth_degrees.items():
        if "degree_raw" in data:
            deg = data["degree_raw"]
            deg_in_sign = data.get("degree_in_sign", deg % 30.0)
            angle_svg = deg_to_svg_angle(deg)
            planet_list.append({
                "name": name,
                "degree_raw": deg,
                "deg_in_sign": deg_in_sign,
                "angle_svg": angle_svg,
                "symbol": PLANET_SYMBOLS.get(name, name[:2])
            })

    planet_list.sort(key=lambda p: p["angle_svg"])

    # แบ่งระยะรัศมีสลับระดับดาวกุมกัน
    radii_levels = [r_inner + 30, r_inner + 45, r_inner + 15]
    for idx, p in enumerate(planet_list):
        level = idx % len(radii_levels)
        if idx > 0 and abs(p["angle_svg"] - planet_list[idx-1]["angle_svg"]) < 8.0:
            level = (planet_list[idx-1]["level"] + 1) % len(radii_levels)
        p["level"] = level
        p["radius"] = radii_levels[level]

    # วาดหมุดดาวและป้ายข้อความคมชัดสูง
    for p in planet_list:
        rad = math.radians(p["angle_svg"])
        px = cx + r_zodiac * math.cos(rad)
        py = cy + r_zodiac * math.sin(rad)
        tx = cx + p["radius"] * math.cos(rad)
        ty = cy + p["radius"] * math.sin(rad)

        # หมุดดาวทองคำ
        svg.append(f'<circle cx="{px}" cy="{py}" r="3.5" fill="#FDE047" stroke="#1E1B4B" stroke-width="1"/>')
        
        # เส้นประทองคำโยงตำแหน่งดาว
        if abs(p["radius"] - r_zodiac) > 5:
            svg.append(f'<line x1="{px}" y1="{py}" x2="{tx}" y2="{ty}" stroke="#FDE047" stroke-width="1" stroke-dasharray="2 2"/>')
        
        # ป้ายข้อความดาวพร้อม Stroke ขอบดำอ่านง่าย
        lbl_text = f'{p["symbol"]} {p["deg_in_sign"]:.1f}°'
        svg.append(f'<text x="{tx}" y="{ty+4}" font-size="12" font-weight="bold" fill="#FFFFFF" stroke="#0F172A" stroke-width="3.5" text-anchor="middle" class="astro-text">{lbl_text}</text>')

    svg.append('</svg>')
    return "".join(svg)

def calculate_natal_degrees(jul_day_natal, lat, lon):
    cusps, ascmc = swe.houses(jul_day_natal, lat, lon, b'P')
    house_cusps_12 = [float(c) % 360.0 for c in (cusps[1:13] if len(cusps) >= 13 else cusps[:12])]

    degrees = {}
    asc_deg, mc_deg = ascmc[0] % 360.0, ascmc[1] % 360.0
    asc_sign, asc_fmt, asc_in_sign = format_degree(asc_deg)
    mc_sign, mc_fmt, mc_in_sign = format_degree(mc_deg)
    
    degrees["ASC"] = {"sign": asc_sign, "formatted": asc_fmt, "degree_raw": asc_deg, "degree_in_sign": asc_in_sign, "house": 1}
    degrees["MC"] = {"sign": mc_sign, "formatted": mc_fmt, "degree_raw": mc_deg, "degree_in_sign": mc_in_sign, "house": 10}

    for name, pid in PLANET_IDS.items():
        try:
            res, _ = swe.calc_ut(jul_day_natal, pid, swe.FLG_SWIEPH)
        except swe.Error:
            res, _ = swe.calc_ut(jul_day_natal, pid, swe.FLG_MOSEPH)
            
        lon_deg = res[0] % 360.0
        is_retro = res[3] < 0
        sign, formatted, deg_in_sign = format_degree(lon_deg)
        house = get_house_of_position(lon_deg, house_cusps_12)
        degrees[name] = {
            "sign": sign,
            "formatted": formatted,
            "degree_raw": lon_deg,
            "degree_in_sign": deg_in_sign,
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
        sign, formatted, deg_in_sign = format_degree(lon_deg)
        house = get_house_of_position(lon_deg, house_cusps_12) if house_cusps_12 else 1
        transits[name] = {
            "sign": sign,
            "formatted": formatted,
            "degree_raw": lon_deg,
            "degree_in_sign": deg_in_sign,
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
        h_sign, _, _ = format_degree(house_cusps_12[h_num - 1])
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
