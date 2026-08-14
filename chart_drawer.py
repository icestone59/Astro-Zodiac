import math

# ข้อมูลสัญลักษณ์ราศีและสีประจำธาตุ
ZODIAC_DATA = [
    ("Aries", "♈", "#e53e3e"), ("Taurus", "♉", "#38a169"), ("Gemini", "♊", "#d69e2e"),
    ("Cancer", "♋", "#3182ce"), ("Leo", "♌", "#e53e3e"), ("Virgo", "♍", "#38a169"),
    ("Libra", "♎", "#d69e2e"), ("Scorpio", "♏", "#3182ce"), ("Sagittarius", "♐", "#e53e3e"),
    ("Capricorn", "♑", "#38a169"), ("Aquarius", "♒", "#d69e2e"), ("Pisces", "♓", "#3182ce")
]

# สัญลักษณ์ดาวโหราศาสตร์สากลครบชุด
PLANET_GLYPHS = {
    "Sun": "☉", "Moon": "☽", "Mercury": "☿", "Venus": "♀", "Mars": "♂",
    "Jupiter": "♃", "Saturn": "♄", "Uranus": "♅", "Neptune": "♆", "Pluto": "♇",
    "North_Node": "☊", "Chiron": "⚷"
}

def get_xy(degree: float, radius: float, asc_deg: float, cx=400, cy=400):
    """คำนวณพิกัด X, Y บนวงกลม โดยล็อกให้ลัคนา (ASC) อยู่ฝั่งซ้ายมือ (180 องศา) เสมอ"""
    chart_angle = (180.0 - (degree - asc_deg)) % 360.0
    rad = math.radians(chart_angle)
    return cx + radius * math.cos(rad), cy + radius * math.sin(rad)

def generate_astroseek_svg(planets: dict, houses: list, asc_deg: float) -> str:
    cx, cy = 400, 400
    r_outer = 350    # ขอบนอกขีดสเกล 360 องศา
    r_zodiac = 310   # วงราศี
    r_house = 270    # วงเรือนชะตา
    r_inner = 150    # วงในสุด (พื้นที่ลากเส้น Aspect)

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 800" style="background:#ffffff; font-family:sans-serif;">']

    # 1. วงกลมหลัก 4 ชั้น
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r_outer}" fill="none" stroke="#000000" stroke-width="2"/>')
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r_zodiac}" fill="none" stroke="#000000" stroke-width="1"/>')
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r_house}" fill="none" stroke="#000000" stroke-width="2"/>')
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r_inner}" fill="none" stroke="#000000" stroke-width="1"/>')

    # 2. ขีดสเกลไม้บรรทัด 360 องศา
    for deg in range(360):
        length = 10 if deg % 10 == 0 else (5 if deg % 5 == 0 else 3)
        x1, y1 = get_xy(deg, r_outer, asc_deg)
        x2, y2 = get_xy(deg, r_outer - length, asc_deg)
        stroke_w = 1.5 if deg % 10 == 0 else 0.5
        svg.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#333333" stroke-width="{stroke_w}"/>')

    # 3. ช่องสัญลักษณ์ 12 ราศี
    for i, (name, symbol, color) in enumerate(ZODIAC_DATA):
        deg_start = i * 30.0
        x1, y1 = get_xy(deg_start, r_house, asc_deg)
        x2, y2 = get_xy(deg_start, r_outer, asc_deg)
        svg.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#000000" stroke-width="1"/>')

        sym_x, sym_y = get_xy(deg_start + 15.0, (r_outer + r_zodiac) / 2.0, asc_deg)
        svg.append(f'<text x="{sym_x:.1f}" y="{sym_y:.1f}" fill="{color}" font-size="28" font-weight="bold" text-anchor="middle" dominant-baseline="central">{symbol}</text>')

    # 4. เส้นแบ่งเรือนชะตา (House Cusps 1-12) และระบุองศาแกน
    for i, h_deg in enumerate(houses):
        is_angle = i in [0, 3, 6, 9] # ASC, IC, DSC, MC
        stroke_w = 3 if is_angle else 1
        color = "#000000" if is_angle else "#666666"
        x1, y1 = get_xy(h_deg, r_inner, asc_deg)
        x2, y2 = get_xy(h_deg, r_house, asc_deg)
        svg.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="{stroke_w}"/>')

        # ตัวเลขเรือนชะตา 1-12
        next_h = houses[(i + 1) % 12]
        diff = (next_h - h_deg) % 360.0
        num_deg = (h_deg + diff / 2.0) % 360.0
        nx, ny = get_xy(num_deg, r_house - 15.0, asc_deg)
        svg.append(f'<text x="{nx:.1f}" y="{ny:.1f}" fill="#777777" font-size="12" font-weight="bold" text-anchor="middle" dominant-baseline="central">{i + 1}</text>')

        # แสดงองศาตรงแกน ASC และ MC
        if is_angle:
            label = "ASC" if i == 0 else ("IC" if i == 3 else ("DSC" if i == 6 else "MC"))
            c_deg = int(h_deg % 30)
            c_min = int((h_deg * 60) % 60)
            lx, ly = get_xy(h_deg, r_inner - 14.0, asc_deg)
            svg.append(f'<text x="{lx:.1f}" y="{ly:.1f}" fill="#000000" font-size="11" font-weight="bold" text-anchor="middle" dominant-baseline="central">{label} {c_deg}°{c_min:02d}\'</text>')

    # 5. แสดงตำแหน่งดาว สัญลักษณ์ องศา/ลิปดา และจัดระยะไม่ให้ซ้อนทับกัน
    sorted_planets = sorted(planets.items(), key=lambda x: x[1])
    r_base = (r_house + r_inner) / 2.0 # 210
    planet_positions = []

    for idx, (p_name, p_deg) in enumerate(sorted_planets):
        glyph = PLANET_GLYPHS.get(p_name, p_name[:2])
        deg_in_sign = int(p_deg % 30)
        min_in_sign = int((p_deg * 60) % 60)
        deg_str = f"{deg_in_sign}°{min_in_sign:02d}'"

        # กระจายรัศมีออกเมื่อดาวอยู่ใกล้กันน้อยกว่า 6 องศา
        r_curr = r_base
        if idx > 0:
            prev_deg = sorted_planets[idx - 1][1]
            if (p_deg - prev_deg) % 360.0 < 6.0:
                r_curr = r_base + (22.0 if idx % 2 == 1 else -22.0)

        px, py = get_xy(p_deg, r_curr, asc_deg)
        ix, iy = get_xy(p_deg, r_inner, asc_deg)

        planet_positions.append({
            "name": p_name, "deg": p_deg, "glyph": glyph,
            "deg_str": deg_str, "px": px, "py": py, "ix": ix, "iy": iy
        })

        # เส้นประโยงตำแหน่งดาวลงวงใน
        svg.append(f'<line x1="{px:.1f}" y1="{py:.1f}" x2="{ix:.1f}" y2="{iy:.1f}" stroke="#999999" stroke-width="0.8" stroke-dasharray="2,2"/>')

        # วาดสัญลักษณ์ดาว และ องศา/ลิปดา ด้านล่าง
        svg.append(f'<text x="{px:.1f}" y="{py - 7:.1f}" fill="#000000" font-size="18" font-weight="bold" text-anchor="middle" dominant-baseline="central">{glyph}</text>')
        svg.append(f'<text x="{px:.1f}" y="{py + 10:.1f}" fill="#222222" font-size="10" font-weight="bold" text-anchor="middle" dominant-baseline="central">{deg_str}</text>')

    # 6. ลากเส้นมุมสัมพันธ์ (Aspect Lines)
    for i in range(len(planet_positions)):
        for j in range(i + 1, len(planet_positions)):
            p1 = planet_positions[i]
            p2 = planet_positions[j]
            diff = abs(p1["deg"] - p2["deg"])
            if diff > 180.0:
                diff = 360.0 - diff

            orb = 6.0
            if abs(diff - 120.0) <= orb or abs(diff - 60.0) <= orb:
                svg.append(f'<line x1="{p1["ix"]:.1f}" y1="{p1["iy"]:.1f}" x2="{p2["ix"]:.1f}" y2="{p2["iy"]:.1f}" stroke="#3182ce" stroke-width="1.2"/>') # มุมดี (น้ำเงิน)
            elif abs(diff - 90.0) <= orb or abs(diff - 180.0) <= orb:
                svg.append(f'<line x1="{p1["ix"]:.1f}" y1="{p1["iy"]:.1f}" x2="{p2["ix"]:.1f}" y2="{p2["iy"]:.1f}" stroke="#e53e3e" stroke-width="1.2"/>') # มุมขัดแย้ง (แดง)

    svg.append('</svg>')
    return "".join(svg)
