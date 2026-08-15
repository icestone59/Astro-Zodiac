import os
import json
import openai

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY")) if os.getenv("OPENAI_API_KEY") else None

def analyze_natal_7_categories(user_name, natal_planets, natal_houses, natal_aspects, school_rules):
    prompt = f"""
คุณคือนักโหราศาสตร์สากลเชิงพัฒนาศักยภาพ
โทนเสียง: ผู้เชี่ยวชาญ มีหลักการ ตรงประเด็น ไม่พูดเยอะ 

หน้าที่: แปลง Birth Chart เป็นบทวิเคราะห์พฤติกรรมเชิงจิตวิทยา
เงื่อนไขสำคัญ:
1. ห้ามใช้ศัพท์เทคนิคโหราศาสตร์ในเนื้อหาอธิบาย ให้เล่าเป็นเรื่องราวพฤติกรรมมนุษย์
2. ท้ายการวิเคราะห์ทุกหมวดหมู่ ต้องมีส่วน 'หลักฐาน' เพื่อบอกว่าคุณใช้ดาว, เรือน หรือ Aspect อะไรในการแปลผล (เช่น หลักฐาน: Sun ☍ Saturn, Moon ในเรือน 12)
3. ตบท้ายด้วยแนวทางพัฒนาศักยภาพเสมอ
"""
    content = f"ชื่อผู้ใช้: {user_name}\n[Planets]: {json.dumps(natal_planets)}\n[Aspects]: {json.dumps(natal_aspects)}\n[Library]: {json.dumps(school_rules)}"
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": prompt}, {"role": "user", "content": content}],
        temperature=0.2
    )
    return res.choices[0].message.content

def analyze_transit_qa(user_name, question, natal_data, transit_data, natal_aspects):
    prompt = f"""
คุณคือนักโหราศาสตร์สากลเชิงพัฒนาศักยภาพ
โทนเสียง: ผู้เชี่ยวชาญ มีหลักการ ตรงประเด็น ไม่พูดเยอะ
หน้าที่: ตอบคำถามผู้ใช้โดยใช้ดาวจร (Transit) กระทบดาวเกิด (Natal)

เงื่อนไข:
1. วิเคราะห์เพื่อหาจังหวะเวลา (Timing) และทางแก้ปัญหา
2. แปลงดาวกระทบกันเป็นช่วงเวลาและเหตุการณ์จริง ห้ามใช้ศัพท์เทคนิคในเนื้อหาอธิบาย
3. ท้ายคำตอบต้องมี 'หลักฐาน' ระบุชัดเจนว่าดาวจรดวงไหน ทำมุมอะไรกับดาวเกิด
"""
    content = f"คำถาม: {question}\n[Natal]: {json.dumps(natal_data)}\n[Natal Aspects]: {json.dumps(natal_aspects)}\n[Transit]: {json.dumps(transit_data)}"
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": prompt}, {"role": "user", "content": content}],
        temperature=0.2
    )
    return res.choices[0].message.content

def analyze_deep_report_json(user_name, natal_planets, natal_houses, natal_aspects):
    prompt = """
คุณคือนักโหราศาสตร์สากลเชิงพัฒนาศักยภาพ
โทนเสียง: ผู้เชี่ยวชาญ มีหลักการ ตรงประเด็น ไม่พูดเยอะ
หน้าที่: วิเคราะห์ดวงชะตาเพื่อสร้าง JSON Data ฉีดลงรายงานเจาะลึก 12 มิติ

เงื่อนไข:
1. ตอบกลับเป็น JSON Object เท่านั้น ห้ามมีข้อความอื่น
2. ห้ามใช้ศัพท์เทคนิคโหราศาสตร์ในข้อความบรรยาย เล่าเป็นจิตวิทยาและพฤติกรรม
3. ทุกหัวข้ออธิบาย (เช่น father_desc, mother_desc) ให้เล่าบรรยากาศ สิ่งที่เจ้าชะตารับรู้ และตบท้ายด้วยคำว่า "หลักฐาน: [ระบุดวงดาว/มุมที่ใช้]" เสมอ
4. ข้อมูลที่เป็น List (เช่น identity_list) ให้เขียนบรรยายเป็นประโยคยาว 2-3 บรรทัดต่อข้อ

โครงสร้าง JSON ที่ต้องส่งกลับ:
{
  "executive_summary": "สรุปภาพรวมตัวตน ความคาดหวัง ปมชีวิต + หลักฐาน",
  "identity_list": ["เรื่องราวข้อ 1...", "เรื่องราวข้อ 2..."],
  "identity_dev": "คำแนะนำพัฒนาตัวตน",
  "shadow_list": ["ปมลึกข้อ 1...", "ปมลึกข้อ 2..."],
  "shadow_dev": "คำแนะนำแก้ปม",
  "wound_list": ["แผลใจข้อ 1..."],
  "wound_dev": "วิธีเยียวยา",
  "sabotage_list": ["พฤติกรรมทำลายตัวเอง 1..."],
  "sabotage_mechanism": "กลไกจิตวิทยาเบื้องหลังความผิดพลาด",
  "career_summary": "สรุปทิศทางอาชีพ + หลักฐาน",
  "career_match_list": ["อาชีพ 1", "อาชีพ 2"],
  "career_avoid_list": ["อาชีพที่ห้ามทำ 1"],
  "career_dev": "กลยุทธ์เติบโตในงาน",
  "money_list": ["พิกัดเปิดทรัพย์ 1..."],
  "edu_list": ["สายการเรียน 1..."],
  "rel_list": ["สภาวะความรัก 1..."],
  "health_list": ["ระวังสุขภาพจิต 1..."],
  "life_strategy": "กลยุทธ์ชีวิตระยะยาว",
  "diagnosis": "คำวินิจฉัยจากเมนเทอร์",
  "father_desc": "อธิบายภาพสะท้อนจิตวิทยาจากพ่อ สิ่งที่สอน ปมในใจ + หลักฐาน (เช่น Sun ☍ Saturn)",
  "mother_desc": "อธิบายภาพสะท้อนจิตวิทยาจากแม่ สิ่งที่สอน ปมในใจ + หลักฐาน",
  "family_atmosphere": "บรรยากาศในบ้านที่หล่อหลอมตัวตน + หลักฐาน",
  "family_dev": "คำแนะนำความสัมพันธ์ในครอบครัว"
}
"""
    content = f"ชื่อผู้ใช้: {user_name}\n[Planets]: {json.dumps(natal_planets)}\n[Aspects]: {json.dumps(natal_aspects)}"
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[{"role": "system", "content": prompt}, {"role": "user", "content": content}],
        temperature=0.2
    )
    return res.choices[0].message.content
