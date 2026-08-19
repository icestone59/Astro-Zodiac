# evidence_engine.py - Evidence Engine คำนวณครั้งเดียว คัดหมวดส่งให้ AI

def build_evidence_matrix(chart_data):
    """
    สร้าง Evidence Matrix ที่รวบรวม House Ruler Chain, Degrees และ Aspects
    เพื่อไม่ให้ AI ต้องคำนวณซ้ำ
    """
    birth = chart_data.get("birth_chart_degrees", {})
    rulers = chart_data.get("ruler_mapping", {})
    transits = chart_data.get("transit_degrees", {})

    evidence_store = {
        "personality": [],
        "finance": [],
        "career": [],
        "love": [],
        "shadow_wound": [],
        "potential_growth": [],
        "transits": []
    }

    # 1. Identity & Personality Evidence
    asc = birth.get("ASC", {})
    h1_ruler = rulers.get("House_1", {})
    evidence_store["personality"].append(f"EVIDENCE_ASC: ASC in {asc.get('dms')} ({asc.get('sign')})")
    evidence_store["personality"].append(f"EVIDENCE_ASC_RULER: House 1 Cusp {h1_ruler.get('sign')}, Ruler is {h1_ruler.get('ruler_planet')} -> Pos: {h1_ruler.get('ruler_pos')}")
    if "Sun" in birth: evidence_store["personality"].append(f"EVIDENCE_SUN: Sun in {birth['Sun'].get('dms')} House {birth['Sun'].get('house')}")
    if "Moon" in birth: evidence_store["personality"].append(f"EVIDENCE_MOON: Moon in {birth['Moon'].get('dms')} House {birth['Moon'].get('house')}")

    # 2. Finance Evidence
    h2_ruler = rulers.get("House_2", {})
    h8_ruler = rulers.get("House_8", {})
    evidence_store["finance"].append(f"EVIDENCE_H2_RULER: House 2 Cusp {h2_ruler.get('sign')}, Ruler is {h2_ruler.get('ruler_planet')} -> Pos: {h2_ruler.get('ruler_pos')}")
    evidence_store["finance"].append(f"EVIDENCE_H8_RULER: House 8 Cusp {h8_ruler.get('sign')}, Ruler is {h8_ruler.get('ruler_planet')} -> Pos: {h8_ruler.get('ruler_pos')}")
    if "Venus" in birth: evidence_store["finance"].append(f"EVIDENCE_VENUS: Venus in {birth['Venus'].get('dms')} House {birth['Venus'].get('house')}")
    if "Jupiter" in birth: evidence_store["finance"].append(f"EVIDENCE_JUPITER: Jupiter in {birth['Jupiter'].get('dms')} House {birth['Jupiter'].get('house')}")

    # 3. Career Evidence
    mc = birth.get("MC", {})
    h10_ruler = rulers.get("House_10", {})
    h6_ruler = rulers.get("House_6", {})
    evidence_store["career"].append(f"EVIDENCE_MC: MC in {mc.get('dms')} ({mc.get('sign')})")
    evidence_store["career"].append(f"EVIDENCE_H10_RULER: House 10 Cusp {h10_ruler.get('sign')}, Ruler is {h10_ruler.get('ruler_planet')} -> Pos: {h10_ruler.get('ruler_pos')}")
    evidence_store["career"].append(f"EVIDENCE_H6_RULER: House 6 Cusp {h6_ruler.get('sign')}, Ruler is {h6_ruler.get('ruler_planet')} -> Pos: {h6_ruler.get('ruler_pos')}")

    # 4. Love & Relationship Evidence
    h7_ruler = rulers.get("House_7", {})
    evidence_store["love"].append(f"EVIDENCE_H7_RULER: House 7 Cusp {h7_ruler.get('sign')}, Ruler is {h7_ruler.get('ruler_planet')} -> Pos: {h7_ruler.get('ruler_pos')}")
    if "Mars" in birth: evidence_store["love"].append(f"EVIDENCE_MARS: Mars in {birth['Mars'].get('dms')} House {birth['Mars'].get('house')}")

    # 5. Shadow, Wound & Challenges
    if "Chiron" in birth: evidence_store["shadow_wound"].append(f"EVIDENCE_CHIRON: Chiron in {birth['Chiron'].get('dms')} House {birth['Chiron'].get('house')}")
    if "Saturn" in birth: evidence_store["shadow_wound"].append(f"EVIDENCE_SATURN: Saturn in {birth['Saturn'].get('dms')} House {birth['Saturn'].get('house')}")
    if "Pluto" in birth: evidence_store["shadow_wound"].append(f"EVIDENCE_PLUTO: Pluto in {birth['Pluto'].get('dms')} House {birth['Pluto'].get('house')}")

    # 6. Transits Evidence
    for p_name, t_info in transits.items():
        evidence_store["transits"].append(f"EVIDENCE_TRANSIT_{p_name}: Transit {p_name} in {t_info.get('dms')} (Activated Natal House {t_info.get('house_in_natal')})")

    return evidence_store

def format_evidence_for_prompt(evidence_store, categories=None):
    """ส่งเฉพาะ Evidence ที่เกี่ยวข้องให้ AI เพื่อประหยัด Token และเร่งความเร็ว"""
    formatted_text = "=== PRE-CALCULATED EVIDENCE ENGINE MATRIX ===\n"
    if categories:
        for cat in categories:
            if cat in evidence_store:
                formatted_text += f"\n[{cat.upper()} EVIDENCE]\n" + "\n".join(evidence_store[cat]) + "\n"
    else:
        for cat, items in evidence_store.items():
            formatted_text += f"\n[{cat.upper()} EVIDENCE]\n" + "\n".join(items) + "\n"
    return formatted_text
