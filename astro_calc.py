import os
import ssl
import urllib.request
from datetime import datetime
import pytz
import swisseph as swe
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder

EPHE_DIR = "/tmp/ephe"
CHIRON_FILE = os.path.join(EPHE_DIR, "seas_18.se1")

def ensure_ephe():
    os.makedirs(EPHE_DIR, exist_ok=True)
    if os.path.exists(CHIRON_FILE) and os.path.getsize(CHIRON_FILE) > 200000:
        swe.set_ephe_path(EPHE_DIR)
        return True
    url = "https://raw.githubusercontent.com/aloistr/swisseph/master/ephe/seas_18.se1"
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
            with open(CHIRON_FILE, 'wb') as out:
                out.write(response.read())
    except Exception:
        pass
    swe.set_ephe_path(EPHE_DIR)
    return True

geolocator = Nominatim(user_agent="evolutionary_astro_engine")
tf = TimezoneFinder()

PLANETS = {
    'Sun': swe.SUN, 'Moon': swe.MOON, 'Mercury': swe.MERCURY, 'Venus': swe.VENUS, 
    'Mars': swe.MARS, 'Jupiter': swe.JUPITER, 'Saturn': swe.SATURN, 'Uranus': swe.URANUS, 
    'Neptune': swe.NEPTUNE, 'Pluto': swe.PLUTO, 'North_Node': swe.MEAN_NODE, 'Chiron': swe.CHIRON
}

ZODIAC_SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

def get_coordinates(loc_str: str):
    try:
        search_query = f"{loc_str}, Thailand" if "ไทย" not in loc_str else loc_str
        loc = geolocator.geocode(search_query, timeout=10)
        if loc:
            tz_str = tf.timezone_at(lng=loc.longitude, lat=loc.latitude) or "Asia/Bangkok"
            return loc.latitude, loc.longitude, tz_str, loc.address
    except:
        pass
    return 13.7563, 100.5018, "Asia/Bangkok", loc_str

def calculate_aspects(planets_data):
    aspects = []
    aspect_rules = [
        {"name": "Conjunction (☌)", "angle": 0, "orb": 8},
        {"name": "Sextile (✶)", "angle": 60, "orb": 6},
        {"name": "Square (□)", "angle": 90, "orb": 8},
        {"name": "Trine (△)", "angle": 120, "orb": 8},
        {"name": "Opposition (☍)", "angle": 180, "orb": 8}
    ]
    p_names = list(planets_data.keys())
    
    for i in range(len(p_names)):
        for j in range(i + 1, len(p_names)):
            p1, p2 = p_names[i], p_names[j]
            # ข้ามจุดสมมติบางจุดในการหามุม
            if p1 in ['South_Node', 'Sun_Moon_Midpoint', 'ASC', 'MC'] or p2 in ['South_Node', 'Sun_Moon_Midpoint', 'ASC', 'MC']: continue
            
            deg1 = planets_data[p1]['absolute_degree']
            deg2 = planets_data[p2]['absolute_degree']
            diff = abs(deg1 - deg2)
            if diff > 180: diff = 360 - diff
            
            for rule in aspect_rules:
                if abs(diff - rule['angle']) <= rule['orb']:
                    aspects.append(f"{p1} {rule['name']} {p2}")
    return aspects

def calculate_chart(dt_utc: datetime, lat: float, lon: float):
    ensure_ephe()
    dec_hour = dt_utc.hour + (dt_utc.minute / 60.0) + (dt_utc.second / 3600.0)
    julday = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, dec_hour)

    planets = {}
    for name, p_id in PLANETS.items():
        flag = swe.FLG_SWIEPH if p_id == swe.CHIRON else swe.FLG_MOSEPH
        try:
            res, _ = swe.calc_ut(julday, p_id, flag)
            deg = res[0] % 360
            planets[name] = {
                "sign": ZODIAC_SIGNS[int(deg // 30)],
                "formatted": f"{int(deg % 30)}°{int((deg % 1) * 60):02d}'",
                "absolute_degree": round(deg, 4)
            }
        except: pass

    houses, ascmc = swe.houses(julday, lat, lon, b'P')
    planets['ASC'] = {"sign": ZODIAC_SIGNS[int(ascmc[0] // 30)], "absolute_degree": round(ascmc[0], 4)}
    planets['MC'] = {"sign": ZODIAC_SIGNS[int(ascmc[1] // 30)], "absolute_degree": round(ascmc[1], 4)}

    # Map Planets to Houses
    h_cusps = [houses[i] for i in range(12)]
    for p_name, p_data in planets.items():
        p_abs = p_data['absolute_degree']
        for h_idx in range(12):
            h_start, h_end = h_cusps[h_idx], h_cusps[(h_idx + 1) % 12]
            if (h_start < h_end and h_start <= p_abs < h_end) or (h_start >= h_end and (p_abs >= h_start or p_abs < h_end)):
                planets[p_name]['house'] = h_idx + 1
                break

    formatted_houses = {f"House_{i+1}": {"absolute_degree": houses[i]} for i in range(12)}
    aspects = calculate_aspects(planets)
    
    return planets, formatted_houses, aspects
