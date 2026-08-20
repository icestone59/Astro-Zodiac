from database import get_cached_chart, save_chart_cache
from astro_engine import get_realtime_transits

def get_or_create_evidence(user_id, birth_data, calculate_chart_fn):
    # 1. เช็ก Cache ใน Database ก่อน
    cached = get_cached_chart(user_id)
    if not cached:
        # คำนวณใหม่เฉพาะครั้งแรก
        chart_data = calculate_chart_fn(birth_data)
        save_chart_cache(user_id, birth_data, chart_data["birth_chart_degrees"], chart_data["ruler_mapping"])
        cached = chart_data

    birth = cached["birth_chart_degrees"]
    rulers = cached["ruler_mapping"]
    transits = get_realtime_transits()

    # 2. สกัด Evidence Matrix แยกตามหมวดหมู่
    evidence_matrix = {
        "personality": [
            f"ASC: {birth.get('ASC', {}).get('dms')}",
            f"ASC Ruler: {rulers.get('House_1', {}).get('ruler_planet')} in {rulers.get('House_1', {}).get('ruler_pos')}",
            f"Sun: {birth.get('Sun', {}).get('dms')} (H{birth.get('Sun', {}).get('house')})",
            f"Moon: {birth.get('Moon', {}).get('dms')} (H{birth.get('Moon', {}).get('house')})"
        ],
        "finance": [
            f"House 2 Cusp: {rulers.get('House_2', {}).get('sign')}",
            f"House 2 Ruler: {rulers.get('House_2', {}).get('ruler_planet')} in {rulers.get('House_2', {}).get('ruler_pos')}",
            f"Venus: {birth.get('Venus', {}).get('dms')} (H{birth.get('Venus', {}).get('house')})"
        ],
        "career": [
            f"MC: {birth.get('MC', {}).get('dms')}",
            f"House 10 Ruler: {rulers.get('House_10', {}).get('ruler_planet')} in {rulers.get('House_10', {}).get('ruler_pos')}",
            f"House 6 Ruler: {rulers.get('House_6', {}).get('ruler_planet')} in {rulers.get('House_6', {}).get('ruler_pos')}"
        ],
        "love": [
            f"House 7 Cusp: {rulers.get('House_7', {}).get('sign')}",
            f"House 7 Ruler: {rulers.get('House_7', {}).get('ruler_planet')} in {rulers.get('House_7', {}).get('ruler_pos')}",
            f"Mars: {birth.get('Mars', {}).get('dms')} (H{birth.get('Mars', {}).get('house')})"
        ],
        "transits": [
            f"Transit {p}: {info['dms']}" for p, info in transits.items()
        ]
    }
    
    return evidence_matrix
