import swisseph as swe
import datetime

PLANET_IDS = {
    "Sun": swe.SUN, "Moon": swe.MOON, "Mercury": swe.MERCURY,
    "Venus": swe.VENUS, "Mars": swe.MARS, "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN, "Uranus": swe.URANUS, "Neptune": swe.NEPTUNE,
    "Pluto": swe.PLUTO, "Chiron": swe.CHIRON, "North_Node": swe.MEAN_NODE
}

ZODIAC_NAMES = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

def format_degree_dual(deg_raw):
    deg_norm = float(deg_raw) % 360.0
    sign_idx = int(deg_norm // 30) % 12
    rem_deg = deg_norm % 30
    degrees = int(rem_deg)
    minutes = int(round((rem_deg - degrees) * 60))
    if minutes == 60:
        degrees += 1
        minutes = 0
    sign_name = ZODIAC_NAMES[sign_idx]
    return {
        "sign": sign_name,
        "dms": f"{sign_name} {degrees}°{minutes:02d}'",
        "decimal": round(rem_deg, 1),
        "degree_raw": deg_norm
    }

def get_realtime_transits(house_cusps_12=None):
    now = datetime.datetime.now(datetime.timezone.utc)
    jd_now = swe.julday(now.year, now.month, now.day, now.hour + now.minute / 60.0)
    transits = {}
    for name, pid in PLANET_IDS.items():
        res, _ = swe.calc_ut(jd_now, pid)
        lon = res[0] % 360.0
        transits[name] = {
            **format_degree_dual(lon),
            "is_retrograde": res[3] < 0
        }
    return transits
