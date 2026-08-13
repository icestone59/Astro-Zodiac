import os
import ssl
import urllib.request
from datetime import datetime
import pytz
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import swisseph as swe
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder

app = FastAPI(title="Evolutionary Astrology Engine API")

EPHE_DIR = "/tmp/ephe"
CHIRON_FILE = os.path.join(EPHE_DIR, "seas_18.se1")
CHIRON_URL = "https://raw.githubusercontent.com/aloistr/swisseph/master/ephe/seas_18.se1"

def ensure_ephe():
    os.makedirs(EPHE_DIR, exist_ok=True)
    if not os.path.exists(CHIRON_FILE) or os.path.getsize(CHIRON_FILE) < 200000:
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            req = urllib.request.Request(CHIRON_URL, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, context=ctx) as response, open(CHIRON_FILE, 'wb') as out:
                out.write(response.read())
        except Exception as e:
            print(f"[Ephemeris Warning] {e}")
    swe.set_ephe_path(EPHE_DIR)

geolocator = Nominatim(user_agent="astro_zodiac_app")
tf = TimezoneFinder()

PLANETS = {
    'Sun': swe.SUN, 'Moon': swe.MOON, 'Mercury': swe.MERCURY,
    'Venus': swe.VENUS, 'Mars': swe.MARS, 'Jupiter': swe.JUPITER,
    'Saturn': swe.SATURN, 'Uranus': swe.URANUS, 'Neptune': swe.NEPTUNE,
    'Pluto': swe.PLUTO, 'Chiron': swe.CHIRON, 'North_Node': swe.MEAN_NODE
}

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

def _get_degree_info(degree: float) -> dict:
    degree = degree % 360
    sign_idx = int(degree // 30)
    deg_in_sign = degree % 30

    d = int(deg_in_sign)
    m = int((deg_in_sign - d) * 60)
    s = int(round(((deg_in_sign - d) * 60 - m) * 60))

    if s == 60:
        s = 0
        m += 1
    if m == 60:
        m = 0
        d += 1

    return {
        "sign": ZODIAC_SIGNS[sign_idx],
        "degree": d,
        "minute": m,
        "second": s,
        "formatted": f"{d}°{m:02d}'",
        "absolute_degree": round(degree, 4)
    }

def _calc_planet_degree(julday: float, p_id: int) -> float:
    ensure_ephe()
    try:
        if p_id == swe.CHIRON:
            res, _ = swe.calc_ut(julday, p_id, swe.FLG_SWIEPH)
        else:
            res, _ = swe.calc_ut(julday, p_id, swe.FLG_MOSEPH)
        return res[0]
    except Exception:
        res, _ = swe.calc_ut(julday, p_id, swe.FLG_MOSEPH)
        return res[0]

class NatalRequest(BaseModel):
    year: int
    month: int
    day: int
    hour: int
    minute: int
    location_name: str

@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <!DOCTYPE html>
    <html lang="th">
    <head>
        <meta charset="UTF-8">
        <title>Evolutionary Astrology Engine</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-slate-900 text-white min-h-screen p-6 flex flex-col items-center">
        <div class="max-w-xl w-full bg-slate-800 p-8 rounded-xl shadow-lg border border-slate-700">
            <h1 class="text-2xl font-bold mb-6 text-indigo-400 text-center">ผูกดวงโหราศาสตร์สากล (Natal Chart)</h1>
            <form id="astroForm" class="space-y-4">
                <div class="grid grid-cols-3 gap-3">
                    <div>
                        <label class="block text-xs mb-1">ปี (ค.ศ.)</label>
                        <input type="number" id="year" value="1977" class="w-full p-2 bg-slate-700 rounded border border-slate-600">
                    </div>
                    <div>
                        <label class="block text-xs mb-1">เดือน</label>
                        <input type="number" id="month" value="5" class="w-full p-2 bg-slate-700 rounded border border-slate-600">
                    </div>
                    <div>
                        <label class="block text-xs mb-1">วัน</label>
                        <input type="number" id="day" value="25" class="w-full p-2 bg-slate-700 rounded border border-slate-600">
                    </div>
                </div>
                <div class="grid grid-cols-2 gap-3">
                    <div>
                        <label class="block text-xs mb-1">ชั่วโมง (0-23)</label>
                        <input type="number" id="hour" value="10" class="w-full p-2 bg-slate-700 rounded border border-slate-600">
                    </div>
                    <div>
                        <label class="block text-xs mb-1">นาที</label>
                        <input type="number" id="minute" value="51" class="w-full p-2 bg-slate-700 rounded border border-slate-600">
                    </div>
                </div>
                <div>
                    <label class="block text-xs mb-1">สถานที่เกิด</label>
                    <input type="text" id="location" value="Bangkok, Thailand" class="w-full p-2 bg-slate-700 rounded border border-slate-600">
                </div>
                <button type="button" onclick="calculateNatal()" class="w-full py-3 bg-indigo-600 hover:bg-indigo-500 rounded font-bold transition">คำนวณตำแหน่งดาว</button>
            </form>
            <div id="result" class="mt-6 p-4 bg-slate-900 rounded border border-slate-700 text-xs hidden overflow-auto max-h-96"></div>
        </div>

        <script>
            async function calculateNatal() {
                const resultDiv = document.getElementById('result');
                resultDiv.classList.remove('hidden');
                resultDiv.innerText = 'กำลังคำนวณ...';

                const payload = {
                    year: parseInt(document.getElementById('year').value),
                    month: parseInt(document.getElementById('month').value),
                    day: parseInt(document.getElementById('day').value),
                    hour: parseInt(document.getElementById('hour').value),
                    minute: parseInt(document.getElementById('minute').value),
                    location_name: document.getElementById('location').value
                };

                try {
                    const res = await fetch('/natal', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(payload)
                    });
                    const data = await res.json();
                    resultDiv.innerText = JSON.stringify(data, null, 2);
                } catch (err) {
                    resultDiv.innerText = 'Error: ' + err.message;
                }
            }
        </script>
    </body>
    </html>
    """

@app.get("/transit")
def get_realtime_transit():
    try:
        now_utc = datetime.now(pytz.utc)
        dec_hour = now_utc.hour + (now_utc.minute / 60.0) + (now_utc.second / 3600.0)
        julday = swe.julday(now_utc.year, now_utc.month, now_utc.day, dec_hour)

        transits = {}
        for name, p_id in PLANETS.items():
            deg = _calc_planet_degree(julday, p_id)
            transits[name] = _get_degree_info(deg)

        transits['South_Node'] = _get_degree_info((transits['North_Node']['absolute_degree'] + 180) % 360)
        return {"timestamp_utc": now_utc.isoformat(), "transits": transits}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transit Error: {str(e)}")

@app.post("/natal")
def get_birth_chart(req: NatalRequest):
    try:
        loc = geolocator.geocode(req.location_name, timeout=10)
        if not loc:
            raise HTTPException(status_code=400, detail="Location not found")
        
        lat, lon = loc.latitude, loc.longitude
        tz_str = tf.timezone_at(lng=lon, lat=lat) or "UTC"

        local_tz = pytz.timezone(tz_str)
        local_dt = local_tz.localize(datetime(req.year, req.month, req.day, req.hour, req.minute))
        utc_dt = local_dt.astimezone(pytz.utc)

        dec_hour = utc_dt.hour + (utc_dt.minute / 60.0) + (utc_dt.second / 3600.0)
        julday = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, dec_hour)

        planets = {}
        for name, p_id in PLANETS.items():
            deg = _calc_planet_degree(julday, p_id)
            planets[name] = _get_degree_info(deg)

        planets['South_Node'] = _get_degree_info((planets['North_Node']['absolute_degree'] + 180) % 360)

        # คำนวณ Houses ระบบ Placidus
        houses, ascmc = swe.houses(julday, lat, lon, b'P')
        planets['ASC'] = _get_degree_info(ascmc[0])
        planets['MC'] = _get_degree_info(ascmc[1])

        # ระบุ House ของดาวแต่ละดวง
        house_cusps = [houses[i] for i in range(12)]
        for p_name, p_data in planets.items():
            p_abs = p_data['absolute_degree']
            for h_idx in range(12):
                h_start = house_cusps[h_idx]
                h_end = house_cusps[(h_idx + 1) % 12]
                if h_start < h_end:
                    if h_start <= p_abs < h_end:
                        planets[p_name]['house'] = h_idx + 1
                        break
                else:  # ครอบช่วง 360/0 องศา
                    if p_abs >= h_start or p_abs < h_end:
                        planets[p_name]['house'] = h_idx + 1
                        break

        formatted_houses = {f"House_{i+1}": _get_degree_info(houses[i]) for i in range(12)}

        return {
            "resolved_location": loc.address,
            "coordinates": {"lat": lat, "lon": lon, "timezone": tz_str},
            "utc_time": utc_dt.isoformat(),
            "planets": planets,
            "houses": formatted_houses
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Natal Error: {str(e)}")
