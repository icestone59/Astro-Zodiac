# evidence_engine.py - เพิ่มระบบคำนวณ Aspects และคัดแยก Evidence ลึก 3 มิติ

ASPECT_TYPES = [
    ("conjunct", 0, 8.0, "☌"),
    ("sextile", 60, 6.0, "⚹"),
    ("square", 90, 7.0, "□"),
    ("trine", 120, 8.0, "△"),
    ("opposite", 180, 8.0, "☍")
]

def calculate_aspects(degrees_dict):
    """คำนวณมุมสัมพันธ์ระหว่างดาวเดิมทุกดวง พร้อมระยะ Orb"""
    aspects = []
    planets = list(degrees_dict.keys())
    
    for i in range(len(planets)):
        for j in range(i + 1, len(planets)):
            p1_name, p2_name = planets[i], planets[j]
            d1 = degrees_dict[p1_name].get("degree_raw", 0)
            d2 = degrees_dict[p2_name].get("degree_raw", 0)
            
            diff = abs(d1 - d2) % 360
            if diff > 180:
                diff = 360 - diff
                
            for asp_name, target_deg, max_orb, symbol in ASPECT_TYPES:
                orb = abs(diff - target_deg)
                if orb <= max_orb:
                    aspects.append({
                        "p1": p1_name,
                        "p2": p2_name,
                        "aspect": asp_name,
                        "symbol": symbol,
                        "orb": round(orb, 2),
                        "text": f"{p1_name} {symbol} {p2_name} (Orb {round(orb, 1)}°)"
                    })
    return aspects

def build_evidence_matrix(chart_data):
    birth = chart_data.get("birth_chart_degrees", {})
    rulers = chart_data.get("ruler_mapping", {})
    transits = chart_data.get("transit_degrees", {})
    
    # คำนวณ Aspects ทั้งหมดในพื้นดวง
    natal_aspects = calculate_aspects(birth)

    evidence_store = {
        "personality": [],
        "finance": [],
        "career": [],
        "love": [],
        "shadow_wound": [],
        "potential_growth": [],
        "transits": []
    }

    # Helper ค้นหา Aspect ที่เกี่ยวข้องกับดาวชุดนั้นๆ
    def get_related_aspects(planet_names):
        res = []
        for asp in natal_aspects:
            if asp["p1"] in planet_names or asp["p2"] in planet_names:
                res.append(asp["text"])
        return res

    # 1. Personality
    asc = birth.get("ASC", {})
    h1_ruler = rulers.get("House_1", {})
    evidence_store["personality"].append(f"ASC: {asc.get('dms')} ({asc.get('sign')})")
    evidence_store["personality"].append(f"ASC Ruler: {h1_ruler.get('ruler_planet')} in {h1_ruler.get('ruler_pos')}")
    if "Sun" in birth: evidence_store["personality"].append(f"Sun: {birth['Sun'].get('dms')} (House {birth['Sun'].get('house')})")
    if "Moon" in birth: evidence_store["personality"].append(f"Moon: {birth['Moon'].get('dms')} (House {birth['Moon'].get('house')})")
    evidence_store["personality"].extend([f"Aspect: {asp}" for asp in get_related_aspects(["ASC", "Sun", "Moon"])])

    # 2. Finance
    h2_ruler = rulers.get("House_2", {})
    h8_ruler = rulers.get("House_8", {})
    evidence_store["finance"].append(f"House 2 Cusp: {h2_ruler.get('sign')}")
    evidence_store["finance"].append(f"House 2 Ruler: {h2_ruler.get('ruler_planet')} in {h2_ruler.get('ruler_pos')}")
    evidence_store["finance"].append(f"House 8 Ruler: {h8_ruler.get('ruler_planet')} in {h8_ruler.get('ruler_pos')}")
    if "Venus" in birth: evidence_store["finance"].append(f"Venus: {birth['Venus'].get('dms')} (House {birth['Venus'].get('house')})")
    evidence_store["finance"].extend([f"Aspect: {asp}" for asp in get_related_aspects(["Venus", "Jupiter", h2_ruler.get('ruler_planet')])])

    # 3. Career
    mc = birth.get("MC", {})
    h10_ruler = rulers.get("House_10", {})
    h6_ruler = rulers.get("House_6", {})
    evidence_store["career"].append(f"MC: {mc.get('dms')} ({mc.get('sign')})")
    evidence_store["career"].append(f"House 10 Ruler: {h10_ruler.get('ruler_planet')} in {h10_ruler.get('ruler_pos')}")
    evidence_store["career"].append(f"House 6 Ruler: {h6_ruler.get('ruler_planet')} in {h6_ruler.get('ruler_pos')}")
    evidence_store["career"].extend([f"Aspect: {asp}" for asp in get_related_aspects(["MC", "Saturn", h10_ruler.get('ruler_planet')])])

    # 4. Love
    h7_ruler = rulers.get("House_7", {})
    evidence_store["love"].append(f"House 7 Cusp: {h7_ruler.get('sign')}")
    evidence_store["love"].append(f"House 7 Ruler: {h7_ruler.get('ruler_planet')} in {h7_ruler.get('ruler_pos')}")
    if "Mars" in birth: evidence_store["love"].append(f"Mars: {birth['Mars'].get('dms')} (House {birth['Mars'].get('house')})")
    evidence_store["love"].extend([f"Aspect: {asp}" for asp in get_related_aspects(["Venus", "Mars", h7_ruler.get('ruler_planet')])])

    # 5. Shadow & Potential
    if "Chiron" in birth: evidence_store["shadow_wound"].append(f"Chiron: {birth['Chiron'].get('dms')} (House {birth['Chiron'].get('house')})")
    if "Saturn" in birth: evidence_store["shadow_wound"].append(f"Saturn: {birth['Saturn'].get('dms')} (House {birth['Saturn'].get('house')})")
    if "North_Node" in birth: evidence_store["potential_growth"].append(f"North Node: {birth['North_Node'].get('dms')} (House {birth['North_Node'].get('house')})")
    evidence_store["shadow_wound"].extend([f"Aspect: {asp}" for asp in get_related_aspects(["Chiron", "Saturn", "Pluto"])])

    # 6. Transits
    for p_name, t_info in transits.items():
        evidence_store["transits"].append(f"Transit {p_name}: {t_info.get('dms')} (Activated Natal House {t_info.get('house_in_natal')})")

    return evidence_store

def format_evidence_for_prompt(evidence_store, categories=None):
    formatted_text = "=== PRE-CALCULATED EVIDENCE ENGINE MATRIX ===\n"
    if categories:
        for cat in categories:
            if cat in evidence_store:
                formatted_text += f"\n[{cat.upper()} EVIDENCE]\n" + "\n".join(evidence_store[cat]) + "\n"
    else:
        for cat, items in evidence_store.items():
            formatted_text += f"\n[{cat.upper()} EVIDENCE]\n" + "\n".join(items) + "\n"
    return formatted_text
