import datetime
import swisseph as swe
from geopy.geocoders import Nominatim

# พจนานุกรมพิกัด 77 จังหวัดทั่วประเทศไทย (Latitude, Longitude, English Name, Country)
THAI_PROVINCE_COORDS = {
    # ภาคกลาง / ปริมณฑล
    "กรุงเทพมหานคร": (13.7563, 100.5018, "Bangkok", "Thailand"),
    "กรุงเทพ": (13.7563, 100.5018, "Bangkok", "Thailand"),
    "นนทบุรี": (13.8591, 100.5217, "Nonthaburi", "Thailand"),
    "ปทุมธานี": (14.0208, 100.5250, "Pathum Thani", "Thailand"),
    "สมุทรปราการ": (13.5991, 100.5968, "Samut Prakan", "Thailand"),
    "สมุทรสาคร": (13.5475, 100.2744, "Samut Sakhon", "Thailand"),
    "นครปฐม": (13.8196, 100.0622, "Nakhon Pathom", "Thailand"),
    "พระนครศรีอยุธยา": (14.3532, 100.5684, "Phra Nakhon Si Ayutthaya", "Thailand"),
    "อยุธยา": (14.3532, 100.5684, "Phra Nakhon Si Ayutthaya", "Thailand"),
    "อ่างทอง": (14.5896, 100.4550, "Ang Thong", "Thailand"),
    "ลพบุรี": (14.7995, 100.6534, "Lopburi", "Thailand"),
    "สิงห์บุรี": (14.8878, 100.3967, "Sing Buri", "Thailand"),
    "ชัยนาท": (15.1852, 100.1251, "Chai Nat", "Thailand"),
    "สระบุรี": (14.5289, 100.9101, "Saraburi", "Thailand"),
    "นครนายก": (14.2069, 101.2131, "Nakhon Nayok", "Thailand"),
    "สุพรรณบุรี": (14.4745, 100.1177, "Suphan Buri", "Thailand"),
    "สมุทรสงคราม": (13.4098, 100.0023, "Samut Songkhram", "Thailand"),
    "เพชรบูรณ์": (16.4190, 101.1560, "Phetchabun", "Thailand"),

    # ภาคเหนือ
    "เชียงใหม่": (18.7883, 98.9853, "Chiang Mai", "Thailand"),
    "เชียงราย": (19.9076, 99.8325, "Chiang Rai", "Thailand"),
    "ลำปาง": (18.2888, 99.4923, "Lampang", "Thailand"),
    "ลำพูน": (18.5745, 99.0087, "Lamphun", "Thailand"),
    "แม่ฮ่องสอน": (19.3021, 97.9654, "Mae Hong Son", "Thailand"),
    "น่าน": (18.7838, 100.7782, "Nan", "Thailand"),
    "พะเยา": (19.1658, 99.9022, "Phayao", "Thailand"),
    "แพร่": (18.1446, 100.1403, "Phrae", "Thailand"),
    "อุตรดิตถ์": (17.6201, 100.0957, "Uttaradit", "Thailand"),
    "ตาก": (16.8839, 99.1258, "Tak", "Thailand"),
    "สุโขทัย": (17.0078, 99.8230, "Sukhothai", "Thailand"),
    "พิษณุโลก": (16.8211, 100.2659, "Phitsanulok", "Thailand"),
    "พิจิตร": (16.4419, 100.3486, "Phichit", "Thailand"),
    "กำแพงเพชร": (16.4828, 99.5227, "Kamphaeng Phet", "Thailand"),
    "นครสวรรค์": (15.6987, 100.1199, "Nakhon Sawan", "Thailand"),
    "อุทัยธานี": (15.3831, 100.0247, "Uthai Thani", "Thailand"),

    # ภาคตะวันออกเฉียงเหนือ (อีสาน)
    "ขอนแก่น": (16.4322, 102.8236, "Khon Kaen", "Thailand"),
    "นครราชสีมา": (14.9799, 102.0978, "Nakhon Ratchasima", "Thailand"),
    "โคราช": (14.9799, 102.0978, "Nakhon Ratchasima", "Thailand"),
    "อุดรธานี": (17.4138, 102.7872, "Udon Thani", "Thailand"),
    "อุบลราชธานี": (15.2287, 104.8594, "Ubon Ratchathani", "Thailand"),
    "บุรีรัมย์": (14.9930, 103.1029, "Buri Ram", "Thailand"),
    "สุรินทร์": (14.8824, 103.4936, "Surin", "Thailand"),
    "ศรีสะเกษ": (15.1186, 104.3220, "Si Sa Ket", "Thailand"),
    "ร้อยเอ็ด": (16.0538, 103.6520, "Roi Et", "Thailand"),
    "มหาสารคาม": (16.1851, 103.3007, "Maha Sarakham", "Thailand"),
    "กาฬสินธุ์": (16.4339, 103.5061, "Kalasin", "Thailand"),
    "สกลนคร": (17.1542, 104.1350, "Sakon Nakhon", "Thailand"),
    "นครพนม": (17.3920, 104.7696, "Nakhon Phanom", "Thailand"),
    "มุกดาหาร": (16.5453, 104.7236, "Mukdahan", "Thailand"),
    "ยโสธร": (15.7924, 104.1453, "Yasothon", "Thailand"),
    "อำนาจเจริญ": (15.8615, 104.6258, "Amnat Charoen", "Thailand"),
    "หนองคาย": (17.8783, 102.7420, "Nong Khai", "Thailand"),
    "เลย": (17.4860, 101.7223, "Loei", "Thailand"),
    "หนองบัวลำภู": (17.2038, 102.4402, "Nong Bua Lam Phu", "Thailand"),
    "บึงกาฬ": (18.3636, 103.6520, "Bueng Kan", "Thailand"),
    "ชัยภูมิ": (15.8068, 102.0315, "Chaiyaphum", "Thailand"),

    # ภาคตะวันออก
    "ชลบุรี": (13.3611, 100.9847, "Chon Buri", "Thailand"),
    "ระยอง": (12.6814, 101.2816, "Rayong", "Thailand"),
    "จันทบุรี": (12.6114, 102.1039, "Chanthaburi", "Thailand"),
    "ตราด": (12.2428, 102.5165, "Trat", "Thailand"),
    "ฉะเชิงเทรา": (13.6904, 101.0779, "Chachoengsao", "Thailand"),
    "ปราจีนบุรี": (14.0509, 101.3730, "Prachin Buri", "Thailand"),
    "สระแก้ว": (13.8140, 102.0712, "Sa Kaeo", "Thailand"),

    # ภาคตะวันตก
    "กาญจนบุรี": (14.0228, 99.5328, "Kanchanaburi", "Thailand"),
    "ราชบุรี": (13.5373, 99.8164, "Ratchaburi", "Thailand"),
    "เพชรบุรี": (13.1069, 99.9447, "Phetchaburi", "Thailand"),
    "ประจวบคีรีขันธ์": (11.8124, 99.7972, "Prachuap Khiri Khan", "Thailand"),

    # ภาคใต้
    "ภูเก็ต": (7.8804, 98.3923, "Phuket", "Thailand"),
    "สงขลา": (7.1988, 100.5951, "Songkhla", "Thailand"),
    "หาดใหญ่": (7.0086, 100.4747, "Hat Yai", "Thailand"),
    "สุราษฎร์ธานี": (9.1382, 99.3217, "Surat Thani", "Thailand"),
    "นครศรีธรรมราช": (8.4304, 99.9631, "Nakhon Si Thammarat", "Thailand"),
    "กระบี่": (8.0863, 98.9063, "Krabi", "Thailand"),
    "พังงา": (8.4501, 98.5255, "Phang Nga", "Thailand"),
    "ตรัง": (7.5563, 99.6114, "Trang", "Thailand"),
    "พัทลุง": (7.6167, 100.0740, "Phatthalung", "Thailand"),
    "ชุมพร": (10.4930, 99.1800, "Chumphon", "Thailand"),
    "ระนอง": (9.9658, 98.6348, "Ranong", "Thailand"),
    "สตูล": (6.6238, 100.0674, "Satun", "Thailand"),
    "ปัตตานี": (6.8663, 101.2501, "Pattani", "Thailand"),
    "ยะลา": (6.5412, 101.2813, "Yala", "Thailand"),
    "นราธิวาส": (6.4255, 101.8253, "Narathiwat", "Thailand")
}

# เกษตรเจ้าเรือน (Rulers) ตามหลักโหราศาสตร์สากลวิวัฒนาการ
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
        geolocator = Nominatim(user_agent="evolutionary_astro_app_v4", timeout=5)
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

    # เรือนชะตา Placidus
    cusps, ascmc = swe.houses(jul_day_natal, lat, lon, b'P')
    house_cusps = list(cusps)
    
    asc_deg, mc_deg = ascmc[0], ascmc[1]
    dsc_deg = (asc_deg + 180) % 360
    
    asc_sign, asc_orb = get_zodiac_sign(asc_deg)
    dsc_sign, dsc_orb = get_zodiac_sign(dsc_deg)
    mc_sign, mc_orb = get_zodiac_sign(mc_deg)

    # 2. ตำแหน่งดาวเกิด (Natal)
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

    # 3. คำนวณ Ruler Mapping
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

    # 4. ดาวจร Real-time ณ วินาทีปัจจุบัน
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
