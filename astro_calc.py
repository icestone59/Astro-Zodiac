import datetime
import swisseph as swe
from geopy.geocoders import Nominatim

# พจนานุกรมพิกัด 77 จังหวัดประเทศไทย
THAI_PROVINCE_COORDS = {
    "กรุงเทพมหานคร": (13.7563, 100.5018, "Bangkok", "Thailand"),
    "กรุงเทพ": (13.7563, 100.5018, "Bangkok", "Thailand"),
    "นนทบุรี": (13.8591, 100.5217, "Nonthaburi", "Thailand"),
    "ปทุมธานี": (14.0208, 100.5250, "Pathum Thani", "Thailand"),
    "สมุทรปราการ": (13.5991, 100.5968, "Samut Prakan", "Thailand"),
    "สมุทรสาคร": (13.5475, 100.2744, "Samut Sakhon", "Thailand"),
    "นครปฐม": (13.8196, 100.0622, "Nakhon Pathom", "Thailand"),
    "อยุธยา": (14.3532, 100.5684, "Ayutthaya", "Thailand"),
    "พระนครศรีอยุธยา": (14.3532, 100.5684, "Ayutthaya", "Thailand"),
    "เชียงใหม่": (18.7883, 98.9853, "Chiang Mai", "Thailand"),
    "เชียงราย": (19.9076, 99.8325, "Chiang Rai", "Thailand"),
    "ภูเก็ต": (7.8804, 98.3923, "Phuket", "Thailand"),
    "ขอนแก่น": (16.4322, 102.8236, "Khon Kaen", "Thailand"),
    "ชลบุรี": (13.3611, 100.9847, "Chon Buri", "Thailand"),
    "สงขลา": (7.1988, 100.5951, "Songkhla", "Thailand"),
    "หาดใหญ่": (7.0086, 100.4747, "Hat Yai", "Thailand"),
    "สุราษฎร์ธานี": (9.1382, 99.3217, "Surat Thani", "Thailand"),
    "นครราชสีมา": (14.9799, 102.0978, "Nakhon Ratchasima", "Thailand"),
    "โคราช": (14.9799, 102.0978, "Nakhon Ratchasima", "Thailand"),
    "อุดรธานี": (17.4138, 102.7872, "Udon Thani", "Thailand"),
    "อุบลราชธานี": (15.2287, 104.8594, "Ubon Ratchathani", "Thailand")
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
    "Pluto": swe.PLUTO, "Chiron": swe.CHIRON, "North Node": swe.MEAN_NODE
}

# 📌 กำหนด Flag บังคับใช้สูตร Moshier ไม่พึ่งพาไฟล์ .se1 ภายนอก
EPHE_FLAG = swe.FLG_MOSEPH

def get_coordinates(location_name):
    if not location_name:
        return 13.7563, 100.5018, "Bangkok", "Thailand"
        
    clean_name = str(location_name).strip()
    if clean_name in THAI_PROVINCE_COORDS:
        return THAI_PROVINCE_COORDS[clean_name]

    try:
        geolocator = Nominatim(user_agent="evolutionary_astro_engine_v5", timeout=5)
        query_str = f"{clean_name}, Thailand" if "Thailand" not in clean_name else clean_name
        location = geolocator.geocode(query_str, addressdetails=True)
        if location:
            address = location.raw.get('address', {})
            city = address.get('city') or address.get('state') or clean_name
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
    swe.set_ephe_path('')
    
    # 1. Natal JulDay
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

    # 2. Natal Planets (ใช้ EPHE_FLAG แก้ไขปัญหาไฟล์ .se1 หาย)
    natal_planets = {}
    for name, pid in PLANET_IDS.items():
        res, _ = swe.calc_ut(jul_day_natal, pid, EPHE_FLAG)
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

    # 3. House Rulers Mapping
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

    # 4. Real-time Transits
    if not transit_dt_utc:
        transit_dt_utc = datetime.datetime.now(datetime.timezone.utc)

    jul_day_transit = swe.julday(
        transit_dt_utc.year, transit_dt_utc.month, transit_dt_utc.day,
        transit_dt_utc.hour + transit_dt_utc.minute / 60.0
    )

    transit_planets = {}
    for name, pid in PLANET_IDS.items():
        res, _ = swe.calc_ut(jul_day_transit, pid, EPHE_FLAG)
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
