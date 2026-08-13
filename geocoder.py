from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder

# กำหนด User-Agent เพื่อเรียกใช้ OpenStreetMap Nominatim
geolocator = Nominatim(user_agent="astro_zodiac_geocoder")
tf = TimezoneFinder()

def get_coordinates_and_tz(location_name: str) -> dict:
    """
    รับชื่อสถานที่ เช่น "Bangkok, Thailand" หรือ "Chiang Mai"
    คืนค่า lat, lon และ timezone string
    """
    try:
        location = geolocator.geocode(location_name, timeout=10)
        if not location:
            return None
        
        lat = location.latitude
        lon = location.longitude
        
        # ค้นหา Timezone จากพิกัด
        tz_name = tf.timezone_at(lng=lon, lat=lat)
        
        return {
            "address": location.address,
            "lat": lat,
            "lon": lon,
            "timezone": tz_name or "UTC"
        }
    except Exception as e:
        print(f"Geocoding Error: {e}")
        return None
