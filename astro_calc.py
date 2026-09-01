# astro_calc.py
import os
import math
import logging
import urllib.request
import datetime
import swisseph as swe
from geopy.geocoders import Nominatim
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AstroEngine")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EPHE_DIR = os.path.join(BASE_DIR, 'ephe')
os.makedirs(EPHE_DIR, exist_ok=True)

NEEDED_SE1_FILES = ['seas_18.se1', 'sepl_18.se1', 'semo_18.se1']
ASTRO_FTP_URL = 'https://www.astro.com/ftp/swisseph/ephe/'

def get_realtime_transits():
    """คำนวณตำแหน่งดาวจร Real-time ทั้ง 10 ดาวหลัก และ 8 ดาวทิพย์ยูเรเนียน"""
    now = datetime.now(timezone.utc)
    jul_day = swe.julday(now.year, now.month, now.day, now.hour + now.minute/60.0)
    
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
        deg = res[0]
        transits[name] = {"deg_dec": round(deg, 4), "dms": f"{int(deg)}°{int((deg%1)*60)}'"}
    return transits

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
    "กรุงเทพมหานคร": (13.7563, 100.5018), "นนทบุรี": (13.8591, 100.5217), 
    "ปทุมธานี": (14.0208, 100.5250), "สมุทรปราการ": (13.5991, 100.5968),
    "เชียงใหม่": (18.7883, 98.9853), "ภูเก็ต": (7.8804, 98.3923),
    "ขอนแก่น": (16.4322, 102.8236), "ชลบุรี": (13.3611, 100.9847)
}

ZODIAC_RULERS = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury",
    "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury",
    "Libra": "Venus", "Scorpio": "Pluto", "Sagittarius": "Jupiter",
    "Capricorn": "Saturn", "Aquarius": "Uranus", "Pisces": "Neptune"
}

ZODIAC_NAMES = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
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
        return THAI_PROVINCES[clean][0], THAI_PROVINCES[clean][1], clean
    try:
        geolocator = Nominatim(user_agent="evo_astro_engine", timeout=5)
        loc = geolocator.geocode(f"{clean}, Thailand" if "Thailand" not in clean else clean)
        if loc:
            return loc.latitude, loc.longitude, clean
    except Exception:
        pass
    return 13.7563, 100.5018, clean

def format_degree_dual(deg_raw):
    """ส่งออกค่า 2 รูปแบบ: DMS (3°49') และ Decimal (3.8°)"""
    deg_norm = float(deg_raw) % 360.0
    sign_idx = int(deg_norm // 30) % 12
    rem_deg = deg_norm % 30
    
    degrees = int(rem_deg)
    minutes = int(round((rem_deg - degrees) * 60))
    if minutes == 60:
        degrees += 1
        minutes = 0
        
    sign_name = ZODIAC_NAMES[sign_idx]
    dms_str = f"{sign_name} {degrees}°{minutes:02d}'"
    decimal_str = f"{rem_deg:.1f}°"
    
    return {
        "sign": sign_name,
        "dms": dms_str,
        "decimal": decimal_str,
        "formatted": f"{dms_str} ({decimal_str})",
        "degree_in_sign": rem_deg
    }

# Alias ป้องกัน NameError ในกรณีที่มีจุดเรียกใช้ฟังก์ชันชื่อเดิม
format_degree = format_degree_dual

def get_house_of_position(deg, house_cusps_12):
    deg_norm = float(deg) % 360.0
    for i in range(12):
        c_start = house_cusps_12[i]
        c_end = house_cusps_12[(i + 1) % 12]
        if c_start < c_end:
            if c_start <= deg_norm < c_end: return i + 1
        else:
            if deg_norm >= c_start or deg_norm < c_end: return i + 1
    return 1

def generate_chart_svg(birth_degrees, house_cusps_12):
    cx, cy = 250, 250
    r_outer, r_zodiac, r_inner, r_core = 230, 195, 145, 75

    svg = ['<svg viewBox="0 0 500 500" class="w-full h-full font-sans" xmlns="http://www.w3.org/2000/svg">']
    svg.append('<defs>')
    svg.append('<linearGradient id="goldGrad" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#F59E0B"/><stop offset="100%" stop-color="#B45309"/></linearGradient>')
    svg.append('<linearGradient id="purpleGrad" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#6B21A8"/><stop offset="100%" stop-color="#3B0764"/></linearGradient>')
    svg.append('</defs>')

    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r_outer}" fill="#FFFFFF" stroke="url(#goldGrad)" stroke-width="2.5"/>')
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r_zodiac}" fill="#FAF5FF" stroke="#6B21A8" stroke-width="1.5"/>')
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r_inner}" fill="#FFFFFF" stroke="url(#goldGrad)" stroke-width="1.5"/>')
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r_core}" fill="#F3E8FF" stroke="#6B21A8" stroke-width="1.5"/>')

    def deg_to_svg_angle(deg):
        return (270.0 - deg) % 360.0

    for i in range(12):
        z_start = i * 30.0
        z_mid = z_start + 15.0
        
        l_rad = math.radians(deg_to_svg_angle(z_start))
        lx1, ly1 = cx + r_zodiac * math.cos(l_rad), cy + r_zodiac * math.sin(l_rad)
        lx2, ly2 = cx + r_outer * math.cos(l_rad), cy + r_outer * math.sin(l_rad)
        svg.append(f'<line x1="{lx1}" y1="{ly1}" x2="{lx2}" y2="{ly2}" stroke="#D97706" stroke-width="1"/>')

        s_rad = math.radians(deg_to_svg_angle(z_mid))
        zx, zy = cx + (r_outer - 17.5) * math.cos(s_rad), cy + (r_outer - 17.5) * math.sin(s_rad)
        svg.append(f'<text x="{zx}" y="{zy+6}" font-size="20" font-weight="bold" fill="url(#purpleGrad)" text-anchor="middle">{ZODIAC_SYMBOLS[i]}</text>')

    for h_idx in range(12):
        c_deg = house_cusps_12[h_idx]
        next_c_deg = house_cusps_12[(h_idx + 1) % 12]
        
        rad = math.radians(deg_to_svg_angle(c_deg))
        x1, y1 = cx + r_core * math.cos(rad), cy + r_core * math.sin(rad)
        x2, y2 = cx + r_zodiac * math.cos(rad), cy + r_zodiac * math.sin(rad)
        
        is_cardinal = h_idx in [0, 3, 6, 9]
        stroke_c = "url(#goldGrad)" if is_cardinal else "#C084FC"
        stroke_w = "2" if is_cardinal else "1"
        svg.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke_c}" stroke-width="{stroke_w}"/>')

        diff = (next_c_deg - c_deg) % 360.0
        h_mid_deg = (c_deg + diff / 2.0) % 360.0
        h_rad = math.radians(deg_to_svg_angle(h_mid_deg))
        hx, hy = cx + (r_core + 22) * math.cos(h_rad), cy + (r_core + 22) * math.sin(h_rad)
        svg.append(f'<text x="{hx}" y="{hy+4}" font-size="12" font-weight="bold" fill="#B45309" stroke="#FFFFFF" stroke-width="2" text-anchor="middle">H{h_idx+1}</text>')

    for name, data in birth_degrees.items():
        if "degree_raw" in data:
            deg = data["degree_raw"]
            angle_svg = deg_to_svg_angle(deg)
            rad = math.radians(angle_svg)
            px, py = cx + r_inner * math.cos(rad), cy + r_inner * math.sin(rad)
            sym = PLANET_SYMBOLS.get(name, name[:2])
            svg.append(f'<circle cx="{px}" cy="{py}" r="3" fill="#D97706"/>')
            svg.append(f'<text x="{px}" y="{py-5}" font-size="10" font-weight="bold" fill="#3B0764" text-anchor="middle">{sym}</text>')

    svg.append('</svg>')
    return "".join(svg)

def calculate_natal_degrees(jul_day_natal, lat, lon):
    cusps, ascmc = swe.houses(jul_day_natal, lat, lon, b'P')
    house_cusps_12 = [float(c) % 360.0 for c in (cusps[1:13] if len(cusps) >= 13 else cusps[:12])]

    degrees = {}
    asc_deg, mc_deg = ascmc[0] % 360.0, ascmc[1] % 360.0
    
    degrees["ASC"] = {**format_degree_dual(asc_deg), "degree_raw": asc_deg, "house": 1}
    degrees["MC"] = {**format_degree_dual(mc_deg), "degree_raw": mc_deg, "house": 10}

    for name, pid in PLANET_IDS.items():
        try:
            res, _ = swe.calc_ut(jul_day_natal, pid, swe.FLG_SWIEPH)
        except swe.Error:
            res, _ = swe.calc_ut(jul_day_natal, pid, swe.FLG_MOSEPH)
            
        lon_deg = res[0] % 360.0
        is_retro = res[3] < 0
        house = get_house_of_position(lon_deg, house_cusps_12)
        degrees[name] = {
            **format_degree_dual(lon_deg),
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
        house = get_house_of_position(lon_deg, house_cusps_12) if house_cusps_12 else 1
        transits[name] = {
            **format_degree_dual(lon_deg),
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
        h_sign = format_degree_dual(house_cusps_12[h_num - 1])["sign"]
        r_planet = ZODIAC_RULERS[h_sign]
        r_pos = birth_degrees.get(r_planet, {})
        ruler_mapping[f"House_{h_num}"] = {
            "sign": h_sign,
            "ruler_planet": r_planet,
            "ruler_pos": f"{r_planet} in {r_pos.get('sign', '')} (House {r_pos.get('house', '')})" if r_pos else "N/A"
        }

    return {
        "birth_chart_degrees": birth_degrees,
        "transit_degrees": transit_degrees,
        "ruler_mapping": ruler_mapping,
        "chart_svg": generate_chart_svg(birth_degrees, house_cusps_12)
    }
