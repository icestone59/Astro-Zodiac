import math

ZODIAC_SYMBOLS = [
    ("Aries", "♈", "#ef4444"),       # เมษ
    ("Taurus", "♉", "#10b981"),      # พฤษภ
    ("Gemini", "♊", "#f59e0b"),      # เมถุน
    ("Cancer", "♋", "#3b82f6"),      # กรกฎ
    ("Leo", "♌", "#ef4444"),         # สิงห์
    ("Virgo", "♍", "#10b981"),       # กันย์
    ("Libra", "♎", "#f59e0b"),       # ตุลย์
    ("Scorpio", "♏", "#3b82f6"),     # พิจิก
    ("Sagittarius", "♐", "#ef4444"), # ธนู
    ("Capricorn", "♑", "#10b981"),   # มังกร
    ("Aquarius", "♒", "#f59e0b"),    # กุมภ์
    ("Pisces", "♓", "#3b82f6")       # มีน
]

PLANET_GLYPHS = {
    "Sun": "☉", "Moon": "☽", "Mercury": "☿", "Venus": "♀",
    "Mars": "♂", "Jupiter": "♃", "Saturn": "♄", "Uranus": "♅",
    "Neptune": "♆", "Pluto": "♇", "North_Node": "☊", "ASC": "ASC", "MC": "MC"
}

def generate_birth_chart_svg(planet_degrees: dict) -> str:
    """
    สร้างรูป SVG Birth Chart Wheel แบบเวกเตอร์ (Dark Mode Theme)
    กำหนดให้ ลัคนา (ASC) อยู่ทางทิศตะวันตก (ฝั่งซ้ายมือ 9 นาฬิกา) เสมอ
    """
    cx, cy = 250, 250
    r_outer = 220
    r_zodiac = 180
    r_inner = 130
    r_center = 40

    asc_deg = planet_degrees.get("ASC", {}).get("deg", 0.0)

    def deg_to_xy(deg: float, radius: float):
        # ปรับสูตรให้ 0 องศาเทียบ ASC อยู่ที่ 9 นาฬิกา (180 องศา) และหมุนทวนเข็มนาฬิกา
        alpha = (180.0 - (deg - asc_deg)) % 360.0
        rad = math.radians(alpha)
        x = cx + radius * math.cos(rad)
        y = cy + radius * math.sin(rad)
        return x, y

    svg_lines = []
    svg_lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 500" class="w-full h-auto max-w-[420px] mx-auto filter drop-shadow-lg">')
    
    # Background Circle
    svg_lines.append(f'<circle cx="{cx}" cy="{cy}" r="{r_outer}" fill="#0f172a" stroke="#334155" stroke-width="2"/>')
    svg_lines.append(f'<circle cx="{cx}" cy="{cy}" r="{r_zodiac}" fill="#1e293b" stroke="#475569" stroke-width="1.5"/>')
    svg_lines.append(f'<circle cx="{cx}" cy="{cy}" r="{r_inner}" fill="#020617" stroke="#334155" stroke-width="1"/>')
    svg_lines.append(f'<circle cx="{cx}" cy="{cy}" r="{r_center}" fill="#0f172a" stroke="#475569" stroke-width="1"/>')

    # 1. วาดเส้นแบ่งและสัญลักษณ์ 12 ราศี (Zodiac Wheel)
    for i, (name, symbol, color) in enumerate(ZODIAC_SYMBOLS):
        z_deg = i * 30.0
        # เส้นแบ่งราศี
        x1, y1 = deg_to_xy(z_deg, r_inner)
        x2, y2 = deg_to_xy(z_deg, r_outer)
        svg_lines.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#334155" stroke-width="1"/>')

        # สัญลักษณ์ราศีตรงกลางกึ่งกลางราศี (+15 องศา)
        sx, sy = deg_to_xy(z_deg + 15.0, (r_outer + r_zodiac) / 2)
        svg_lines.append(f'<text x="{sx:.1f}" y="{sy:.1f}" fill="{color}" font-size="16" font-weight="bold" text-anchor="middle" dominant-baseline="central">{symbol}</text>')

    # 2. วาดแกนสำคัญ ASC-DSC และ MC-IC
    for key, color in [("ASC", "#818cf8"), ("MC", "#f43f5e")]:
        if key in planet_degrees:
            deg = planet_degrees[key]["deg"]
            x1, y1 = deg_to_xy(deg, r_center)
            x2, y2 = deg_to_xy(deg, r_outer)
            svg_lines.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="2" stroke-dasharray="4,2"/>')

    # 3. วาดตำแหน่งดาวชะตา (Planetary Positions)
    planet_radius = (r_zodiac + r_inner) / 2
    for p_name, p_data in planet_degrees.items():
        if p_name in ["ASC", "MC"]:
            continue
        p_deg = p_data.get("deg", 0.0)
        glyph = PLANET_GLYPHS.get(p_name, p_name[:2])
        px, py = deg_to_xy(p_deg, planet_radius)
        
        # จุดตำแหน่งดาว
        svg_lines.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="3" fill="#a5b4fc"/>')
        # ข้อความสัญลักษณ์ดาว
        svg_lines.append(f'<text x="{px:.1f}" y="{py - 8:.1f}" fill="#f8fafc" font-size="13" font-weight="bold" text-anchor="middle" dominant-baseline="central">{glyph}</text>')

    # Center Text Display
    svg_lines.append(f'<text x="{cx}" y="{cy - 5}" fill="#818cf8" font-size="11" font-weight="bold" text-anchor="middle">EVOLUTIONARY</text>')
    svg_lines.append(f'<text x="{cx}" y="{cy + 10}" fill="#94a3b8" font-size="9" text-anchor="middle">NATAL CHART</text>')

    svg_lines.append('</svg>')
    return "".join(svg_lines)
