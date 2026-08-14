# --- 1. In-Memory Cache สำหรับสถานที่เกิดยอดนิยม (ตัด Geocoding Latency) ---
LOCATION_CACHE = {
    "bangkok, thailand": (13.7563, 100.5018, "Asia/Bangkok"),
    "bangkok": (13.7563, 100.5018, "Asia/Bangkok"),
    "กรุงเทพ": (13.7563, 100.5018, "Asia/Bangkok"),
    "กรุงเทพมหานคร": (13.7563, 100.5018, "Asia/Bangkok")
}

def get_coordinates_fast(location_str: str):
    """ค้นหาพิกัดจาก Cache ก่อน หากไม่มีจึงเรียก Geopy"""
    loc_key = location_str.strip().lower()
    if loc_key in LOCATION_CACHE:
        lat, lon, tz = LOCATION_CACHE[loc_key]
        return lat, lon, tz, location_str

    # หากไม่มีใน Cache ค่อยยิง Geopy
    try:
        from geopy.geocoders import Nominatim
        from timezonefinder import TimezoneFinder
        geolocator = Nominatim(user_agent="astro_engine_fast")
        loc = geolocator.geocode(location_str)
        if loc:
            tf = TimezoneFinder()
            tz_str = tf.timezone_at(lat=loc.latitude, lng=loc.longitude) or "UTC"
            # บันทึกลง Cache ไว้ใช้รอบถัดไป
            LOCATION_CACHE[loc_key] = (loc.latitude, loc.longitude, tz_str)
            return loc.latitude, loc.longitude, tz_str, loc.address
    except Exception:
        pass
    
    # Default Fallback: Bangkok
    return 13.7563, 100.5018, "Asia/Bangkok", location_str

# --- 2. Fast DB Lookup (ดึงจาก SQLite แบบ Instant) ---
def get_natal_interpretation_fast(category: str, lookup_key: str) -> str:
    """ดึงข้อมูลจาก SQLite โดยตรง หากไม่เจอ Key เป๊ะ ให้ Fallback เป็น Default ใน DB"""
    db_path = "astro_rules.db"
    if not os.path.exists(db_path):
        return f"[{lookup_key}] กำลังอัปเดตข้อมูลบทวิเคราะห์"

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. ค้นหา Key ตรงตัว
        cursor.execute("SELECT content FROM natal_interpretations WHERE category = ? AND lookup_key = ?", (category, lookup_key))
        row = cursor.fetchone()
        if row:
            conn.close()
            return row[0]
            
        # 2. ค้นหา Key ระดับราศีหลัก (ถ้า Key ละเอียดไม่มี)
        main_sign_key = lookup_key.split('_')[0] if '_' in lookup_key else lookup_key
        cursor.execute("SELECT content FROM natal_interpretations WHERE category = ? AND lookup_key LIKE ?", (category, f"{main_sign_key}%"))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return row[0]
            
    except Exception as e:
        print(f"DB Error: {e}")

    return f"ตำแหน่งดาว {lookup_key} ส่งผลเน้นการเรียนรู้และพัฒนาศักยภาพเฉพาะตน"
