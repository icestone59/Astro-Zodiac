import math

# ค่าคงที่สัญลักษณ์และสี
ZODIAC_DATA = [
    ("Aries", "♈", "#e53e3e"), ("Taurus", "♉", "#38a169"), ("Gemini", "♊", "#d69e2e"),
    ("Cancer", "♋", "#3182ce"), ("Leo", "♌", "#e53e3e"), ("Virgo", "♍", "#38a169"),
    ("Libra", "♎", "#d69e2e"), ("Scorpio", "♏", "#3182ce"), ("Sagittarius", "♐", "#e53e3e"),
    ("Capricorn", "♑", "#38a169"), ("Aquarius", "♒", "#d69e2e"), ("Pisces", "♓", "#3182ce")
]

PLANET_GLYPHS = {
    "Sun": "☉", "Moon": "☽", "Mercury": "☿", "Venus": "♀", "Mars": "♂",
    "Jupiter": "♃", "Saturn": "♄", "Uranus": "♅", "Neptune": "♆", "Pluto": "♇",
    "North_Node": "☊", "Chiron": "⚷"
}

def get_xy(degree, radius, asc_deg, cx=400, cy=400):
    """แปลงองศาดาว (0-360) เป็นพิกัด X, Y โดยล็อกให้ลัคนา (ASC) อยู่ซ้ายมือเสมอ (180 องศาแนวราบ)"""
    # Astro-Seek หมุนทวนเข็มนาฬิกา
    chart_angle = (180 - (degree - asc_deg)) % 360
    rad = math.radians(chart_angle)
    return cx + radius * math.cos(rad), cy + radius * math.sin(rad)

def generate_astroseek_svg(planets: dict, houses: list, asc_deg: float) -> str:
    """
    สร้าง SVG Birth Chart สไตล์ Astro-Seek
    - planets: dict ขององศาดาว {"Sun": 63.5, "Moon": 142.1, ...}
    - houses: list ขององศาจุดเริ่มต้นเรือนชะตาทั้ง 12 (Placidus)
    - asc_deg: องศาลัคนา
    """
    cx, cy = 400, 400
    r_outer = 350    # ขอบนอกสุด (ขีดสเกล)
    r_zodiac = 310   # วงราศี
    r_house = 270    # วงเรือนชะตา
    r_inner = 150    # วงในสุด (สำหรับลากเส้น Aspect)

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 800" style="background:#ffffff; font-family:sans-serif;">']
    
    # 1. วาดโครงสร้างวงกลม (Concentric Circles)
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r_outer}" fill="none" stroke="#000" stroke-width="2"/>')
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r_zodiac}" fill="none" stroke="#000" stroke-width="1"/>')
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r_house}" fill="none" stroke="#000" stroke-width="2"/>')
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r_inner}" fill="none" stroke="#000" stroke-width="1"/>')

    # 2. วาดขีดสเกล 360 องศา (Tick marks)
    for deg in range(360):
        length = 10 if deg % 10 == 0 else (5 if deg % 5 == 0 else 3)
        x1, y1 = get_xy(deg, r_outer, asc_deg)
        x2, y2 = get_xy(deg, r_outer - length, asc_deg)
        stroke_w = 1.5 if deg % 10 == 0 else 0.5
        svg.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#333" stroke-width="{stroke_w}"/>')

    # 3. วาดช่องราศี 12 ราศี
    for i, (name, symbol, color) in enumerate(ZODIAC_DATA):
        deg_start = i * 30
        # เส้นแบ่งราศี
        x1, y1 = get_xy(deg_start, r_house, asc_deg)
        x2, y2 = get_xy(deg_start, r_outer, asc_deg)
        svg.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#000" stroke-width="1"/>')
        
        # สัญลักษณ์ราศี (กึ่งกลางช่อง)
        sym_x, sym_y = get_xy(deg_start + 15, (r_outer + r_zodiac) / 2, asc_deg)
        svg.append(f'<text x="{sym_x:.1f}" y="{sym_y:.1f}" fill="{color}" font-size="28" font-weight="bold" text-anchor="middle" dominant-baseline="central">{symbol}</text>')

    # 4. วาดเส้นแบ่งเรือนชะตา (House Cusps)
    for i, h_deg in enumerate(houses):
        is_angle = i in [0, 3, 6, 9] # ASC, IC, DSC, MC
        stroke_w = 3 if is_angle else 1
        color = "#000" if is_angle else "#666"
        x1, y1 = get_xy(h_deg, r_inner, asc_deg)
        x2, y2 = get_xy(h_deg, r_house, asc_deg)
        svg.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="{stroke_w}"/>')
        
        # ใส่ตัวเลขเรือนชะตา (1-12)
        num_deg = (h_deg + houses[(i+1)%12]) / 2
        # แก้ปัญหาองศาคร่อม 360
        if houses[(i+1)%12] < h_deg: num_deg = (h_deg + houses[(i+1)%12] + 360) / 2
        nx, ny = get_xy(num_deg, r_house - 15, asc_deg)
        svg.append(f'<text x="{nx:.1f}" y="{ny:.1f}" fill="#555" font-size="12" text-anchor="middle" dominant-baseline="central">{i+1}</text>')

    # 5. วาดตำแหน่งดาว
    planet_radius = (r_house + r_inner) / 2
    planet_coords = []
    
    for p_name, p_deg in planets.items():
        glyph = PLANET_GLYPHS.get(p_name, p_name[:2])
        px, py = get_xy(p_deg, planet_radius, asc_deg)
        ix, iy = get_xy(p_deg, r_inner, asc_deg) # จุดเชื่อมเส้น Aspect
        planet_coords.append((p_name, p_deg, ix, iy))
        
        # เส้นชี้จากดาวลงมาที่วงใน
        svg.append(f'<line x1="{px:.1f}" y1="{py:.1f}" x2="{ix:.1f}" y2="{iy:.1f}" stroke="#333" stroke-width="0.5" stroke-dasharray="2,2"/>')
        # สัญลักษณ์ดาว
        svg.append(f'<text x="{px:.1f}" y="{py:.1f}" fill="#000" font-size="24" font-weight="bold" text-anchor="middle" dominant-baseline="central">{glyph}</text>')

    # 6. ลากเส้นมุมสัมพันธ์ (Aspect Lines - เฉพาะดาวหลัก)
    # Trine (120°), Sextile (60°) = สีน้ำเงิน / Square (90°), Opposition (180°) = สีแดง
    for i in range(len(planet_coords)):
        for j in range(i + 1, len(planet_coords)):
            p1, d1, x1, y1 = planet_coords[i]
            p2, d2, x2, y2 = planet_coords[j]
            
            diff = abs(d1 - d2)
            if diff > 180: diff = 360 - diff
            
            orb = 6 # ยอมรับความคลาดเคลื่อน 6 องศา
            
            if abs(diff - 120) <= orb or abs(diff - 60) <= orb:
                svg.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#3182ce" stroke-width="1.5"/>') # Blue
            elif abs(diff - 90) <= orb or abs(diff - 180) <= orb:
                svg.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#e53e3e" stroke-width="1.5"/>') # Red

    # แกน ASC/DSC และ MC/IC
    svg.append(f'<text x="{cx - r_inner + 10}" y="{cy - 5}" font-size="12" font-weight="bold">ASC</text>')
    svg.append(f'<text x="{cx + r_inner - 30}" y="{cy - 5}" font-size="12" font-weight="bold">DSC</text>')

    svg.append('</svg>')
    return "".join(svg)
