from geopy.geocoders import Nominatim

# พจนานุกรมสำรองพิกัดจังหวัดหลัก ป้องกัน KeyError
THAI_PROVINCE_COORDS = {
    "กรุงเทพมหานคร": (13.7563, 100.5018, "Bangkok", "Thailand"),
    "กรุงเทพ": (13.7563, 100.5018, "Bangkok", "Thailand"),
    "เชียงใหม่": (18.7883, 98.9853, "Chiang Mai", "Thailand"),
    "ภูเก็ต": (7.8804, 98.3923, "Phuket", "Thailand"),
    "ชลบุรี": (13.3611, 100.9847, "Chon Buri", "Thailand"),
    "ขอนแก่น": (16.4322, 102.8236, "Khon Kaen", "Thailand"),
    "สงขลา": (7.1988, 100.5951, "Songkhla", "Thailand"),
}

def get_coordinates(location_name):
    """แปลงชื่อสถานที่เกิดเป็น (lat, lon, city, country) รองรับภาษาไทยและอังกฤษ"""
    if not location_name:
        return 13.7563, 100.5018, "Bangkok", "Thailand"
        
    clean_name = str(location_name).strip()

    # 1. ค้นจากพจนานุกรมภาษาไทยลัดก่อน
    if clean_name in THAI_PROVINCE_COORDS:
        return THAI_PROVINCE_COORDS[clean_name]

    # 2. ค้นหาผ่าน Geopy โดยเพิ่มคำว่า Thailand
    try:
        geolocator = Nominatim(user_agent="evolutionary_astro_app_v2", timeout=5)
        query_str = f"{clean_name}, Thailand" if "Thailand" not in clean_name else clean_name
        location = geolocator.geocode(query_str, addressdetails=True)
        
        if location:
            address = location.raw.get('address', {})
            city = address.get('city') or address.get('state') or address.get('province') or clean_name
            country = address.get('country', 'Thailand')
            return location.latitude, location.longitude, city, country
    except Exception:
        pass

    # 3. ค่าสำรองเมื่อหาไม่เจอ ป้องกันโปรแกรมแสดง Error หน้าจอ
    return 13.7563, 100.5018, clean_name, "Thailand"
