def analyze_natal_7_categories(user_name, natal_planets, natal_houses, natal_aspects, school_rules):
    # ดึงข้อมูลคลังวิชาจาก Admin
    natal_lib = school_rules.get("natal_categories", {})
    
    # ตรวจสอบสถานะว่าหมวดไหนว่างบ้าง ส่งให้ AI รับรู้ชัดเจน
    lib_status = {
        "1_personality": "มีข้อมูลวิชาของสำนัก" if natal_lib.get("1_personality", "").strip() else "ไม่มีข้อมูล (ต้องเติม (i) หลังชื่อหัวข้อ)",
        "2_finance": "มีข้อมูลวิชาของสำนัก" if natal_lib.get("2_finance", "").strip() else "ไม่มีข้อมูล (ต้องเติม (i) หลังชื่อหัวข้อ)",
        "3_career": "มีข้อมูลวิชาของสำนัก" if natal_lib.get("3_career", "").strip() else "ไม่มีข้อมูล (ต้องเติม (i) หลังชื่อหัวข้อ)",
        "4_love": "มีข้อมูลวิชาของสำนัก" if natal_lib.get("4_love", "").strip() else "ไม่มีข้อมูล (ต้องเติม (i) หลังชื่อหัวข้อ)",
        "5_strengths_weaknesses": "มีข้อมูลวิชาของสำนัก" if natal_lib.get("5_strengths_weaknesses", "").strip() else "ไม่มีข้อมูล (ต้องเติม (i) หลังชื่อหัวข้อ)",
        "6_potentials": "มีข้อมูลวิชาของสำนัก" if natal_lib.get("6_potentials", "").strip() else "ไม่มีข้อมูล (ต้องเติม (i) หลังชื่อหัวข้อ)",
        "7_growth": "มีข้อมูลวิชาของสำนัก" if natal_lib.get("7_growth", "").strip() else "ไม่มีข้อมูล (ต้องเติม (i) หลังชื่อหัวข้อ)"
    }

    prompt = f"""
คุณคือนักโหราศาสตร์สากลเชิงพัฒนาศักยภาพ (Evolutionary Astrologer)
โทนเสียง: ผู้เชี่ยวชาญ มีหลักการ ตรงประเด็น ไม่พูดเยอะ

กฎเหล็กเรื่องรูปแบบการแสดงผล:
1. ห้ามใช้เครื่องหมาย #, ##, ### หรือ #### เด็ดขาด ให้ใช้ตัวหนา **1. ชื่อหัวข้อ** เท่านั้น
2. การติดสัญลักษณ์ (i) ให้ดูจาก [Library Status] ที่ส่งไปให้:
   - หมวดที่เป็น 'มีข้อมูลวิชาของสำนัก' -> ห้ามใส่สัญลักษณ์ (i) เด็ดขาด ให้แสดงแค่ชื่อหัวข้อ เช่น **1. นิสัย บุคลิกภาพ**
   - หมวดที่เป็น 'ไม่มีข้อมูล' -> ต้องเติม (i) ต่อท้ายชื่อหัวข้อ เช่น **1. นิสัย บุคลิกภาพ (i)**
3. ภาษาบรรยาย: เล่าเป็นเรื่องราวเชิงจิตวิทยาและพฤติกรรมมนุษย์ ห้ามใช้ภาษา Dictionary Reading
4. ทุกหมวดต้องตบท้ายด้วย 'แนวทางพัฒนา:' และ 'หลักฐานที่ใช้วิเคราะห์:' เสมอ

[Library Status]:
{json.dumps(lib_status, ensure_ascii=False, indent=2)}

[Library Data]:
{json.dumps(natal_lib, ensure_ascii=False, indent=2)}
"""
    content = f"ชื่อผู้ใช้: {user_name}\n[Natal Planets]: {json.dumps(natal_planets, ensure_ascii=False)}\n[Natal Aspects]: {json.dumps(natal_aspects, ensure_ascii=False)}"
    
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": prompt}, {"role": "user", "content": content}],
        temperature=0.2
    )
    return res.choices[0].message.content
