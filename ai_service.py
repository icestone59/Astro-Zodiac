import os
import json
import openai

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY")) if os.getenv("OPENAI_API_KEY") else None

def analyze_natal_7_categories(user_name, natal_planets, natal_houses, natal_aspects, school_rules):
    prompt = f"""
คุณคือนักโหราศาสตร์สากลเชิงพัฒนาศักยภาพ (Evolutionary Astrologer)
โทนเสียง: ผู้เชี่ยวชาญ มีหลักการ ตรงประเด็น ไม่พูดเยอะ 

ข้อบังคับเรื่องรูปแบบการพิมพ์ (Strict Formatting Rules):
1. **ห้ามใช้เครื่องหมาย #, ##, ### หรือ #### เด็ดขาด** ให้ใช้ข้อความตัวหนาแบบ **1. หัวข้อ** แทนเท่านั้น
2. ต้องพยากรณ์ให้ครบทั้ง 7 หมวดหมู่ตามลำดับ ห้ามตัดทอนหรือข้ามหมวดหมู่ใดหมวดหมู่หนึ่ง
3. ภาษาบรรยาย: ห้ามใช้ศัพท์เทคนิคโหราศาสตร์ในข้อความหลัก เล่าเป็นสภาวะทางจิตวิทยาและพฤติกรรมมนุษย์
4. **ทุกหมวดหมู่ต้องมีกล่องหลักฐาน:** ตบท้ายบทวิเคราะห์ด้วย 'หลักฐาน:' โดยระบุดาว, เรือนชะตา หรือ Aspect ที่ใช้คำนวณจริง

โครงสร้างการตอบ (ต้องตอบให้ครบทั้ง 7 ข้อ):

**1. นิสัย บุคลิกภาพ**
(เนื้อหาบทวิเคราะห์เชิงจิตวิทยาและพฤติกรรม)
**แนวทางพัฒนา:** (คำแนะนำเชิงพฤติกรรม)
**หลักฐาน:** (ระบุดาว/เรือน/Aspect ที่ใช้)

**2. การเงิน**
(เนื้อหาบทวิเคราะห์)
**แนวทางพัฒนา:** (คำแนะนำ)
**หลักฐาน:** (ระบุดาว/เรือน/Aspect)

**3. การงาน อาชีพ ที่ตรงกับดวง**
(เนื้อหาบทวิเคราะห์)
**แนวทางพัฒนา:** (คำแนะนำ)
**หลักฐาน:** (ระบุดาว/เรือน/Aspect)

**4. ความรัก**
(เนื้อหาบทวิเคราะห์)
**แนวทางพัฒนา:** (คำแนะนำ)
**หลักฐาน:** (ระบุดาว/เรือน/Aspect)

**5. จุดเด่น จุดด้อย และการแก้จุดด้อย**
(เนื้อหาบทวิเคราะห์)
**แนวทางพัฒนา:** (คำแนะนำ)
**หลักฐาน:** (ระบุดาว/เรือน/Aspect)

**6. ศักยภาพที่มี และวิธีการพัฒนา**
(เนื้อหาบทวิเคราะห์)
**แนวทางพัฒนา:** (คำแนะนำ)
**หลักฐาน:** (ระบุดาว/เรือน/Aspect)

**7. ปัญหาที่ต้องปรับปรุง เพื่อความก้าวหน้า**
(เนื้อหาบทวิเคราะห์)
**แนวทางพัฒนา:** (คำแนะนำ)
**หลักฐาน:** (ระบุดาว/เรือน/Aspect)
"""
    content = f"ชื่อผู้ใช้: {user_name}\n[Planets]: {json.dumps(natal_planets, ensure_ascii=False)}\n[Aspects]: {json.dumps(natal_aspects, ensure_ascii=False)}\n[Library]: {json.dumps(school_rules, ensure_ascii=False)}"
    
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

ข้อบังคับเรื่องรูปแบบ:
1. **ห้ามใช้เครื่องหมาย #, ##, ### เด็ดขาด**
2. แปลงการกระทบของดาวจรเป็นช่วงเวลา (Timing) สภาวะ และแนวทางแก้ไขเชิงพฤติกรรม
3. ตบท้ายด้วยส่วน **หลักฐาน:** ระบุดาวจรที่ทำมุมกับดาวเกิด

โครงสร้างคำตอบ:
**สภาวะและแนวโน้มปัจจุบัน**
(วิเคราะห์สภาวะอารมณ์และเหตุการณ์)

**จังหวะเวลาและการแก้ไข**
(ระบุช่วงเวลาและทางออก)

**หลักฐาน:**
(ระบุดาวจร และดาวเกิดที่ทำมุมกัน)
"""
    content = f"คำถาม: {question}\n[Natal]: {json.dumps(natal_data, ensure_ascii=False)}\n[Natal Aspects]: {json.dumps(natal_aspects, ensure_ascii=False)}\n[Transit]: {json.dumps(transit_data, ensure_ascii=False)}"
    
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": prompt}, {"role": "user", "content": content}],
        temperature=0.2
    )
    return res.choices[0].message.content


def analyze_deep_report_json(user_name, natal_planets, natal_houses, natal_aspects):
    prompt = """
คุณคือนักโหราศาสตร์สากลเชิงพัฒนาศักยภาพผู้เชี่ยวชาญ
หน้าที่: วิเคราะห์ดวงชะตาเพื่อสร้าง JSON Data สำหรับฉีดลงรายงานฉบับเจาะลึก 12 มิติชีวิต

ข้อบังคับทางเทคนิคและสไตล์ภาษา:
1. ตอบกลับเป็น JSON Object เท่านั้น ห้ามมีข้อความเกริ่นนำ
2. ห้ามใช้ศัพท์เทคนิคโหราศาสตร์ในข้อความบรรยายหลัก ให้เล่าเป็นเรื่องราวเชิงจิตวิทยา (Psychological Storytelling)
3. ในส่วนที่มีการอ้างอิง ให้ใช้รูปแบบ **แปลมาจาก** หรือ **หลักฐาน:** กำกับเสมอ
4. ข้อมูลที่เป็น List (เช่น identity_list) ให้บรรยายเป็นประโยคยาวละเอียด 2-3 บรรทัดต่อข้อ

โครงสร้าง JSON ที่ต้องส่งกลับ:
{
  "executive_summary": "สรุปภาพรวมตัวตน ความมุ่งมั่น ปมชีวิต และเป้าหมาย 2 ย่อหน้าแน่นๆ\\n\\n**หลักฐานที่ใช้วิเคราะห์**\\nราศี: ...\\nเรือน: ...\\nAspect: ...",
  "identity_list": [
    "บรรยายตัวตนข้อ 1...",
    "บรรยายตัวตนข้อ 2...",
    "บรรยายตัวตนข้อ 3..."
  ],
  "identity_dev": "ลดความคาดหวังที่มีต่อตัวเองลงบ้าง...\\n\\n**แปลมาจาก**\\nราศี: ...\\nลัคนา: ...\\nAspect: ...",
  "shadow_list": [
    "ปมทางอารมณ์ข้อ 1...",
    "ปมทางอารมณ์ข้อ 2..."
  ],
  "shadow_dev": "ฝึกขอความช่วยเหลือ...\\n\\n**แปลมาจาก**\\nเรือน: ...\\nAspect: ...",
  "wound_list": [
    "แผลใจลึกๆ ข้อ 1..."
  ],
  "wound_dev": "เรียนรู้ที่จะแยกคุณค่า...\\n\\n**แปลมาจาก**\\nAspect: ...\\nChiron: ...",
  "sabotage_list": [
    "พฤติกรรมทำลายโอกาสตัวเองข้อ 1...",
    "พฤติกรรมทำลายโอกาสตัวเองข้อ 2..."
  ],
  "sabotage_mechanism": "กลไกจิตวิทยาเบื้องหลังความผิดพลาด...\\n\\n**แปลมาจาก**\\nAspect: ...",
  "career_summary": "สรุปพิมพ์เขียวการงานเชิงลึก...",
  "career_match_list": [
    "อาชีพที่เหมาะ 1",
    "อาชีพที่เหมาะ 2",
    "อาชีพที่เหมาะ 3"
  ],
  "career_avoid_list": [
    "อาชีพที่ไม่เหมาะ 1",
    "อาชีพที่ไม่เหมาะ 2"
  ],
  "career_dev": "อย่าพยายามทำทุกอย่างเอง...\\n\\n**แปลมาจาก**\\nMC: ...\\nAspect: ...",
  "money_list": [
    "พิกัดเปิดทรัพย์ข้อ 1...",
    "พิกัดเปิดทรัพย์ข้อ 2..."
  ],
  "edu_list": [
    "สายการเรียนที่เหมาะ 1...",
    "สายการเรียนที่เหมาะ 2..."
  ],
  "rel_list": [
    "สภาวะความรักและการครองคู่..."
  ],
  "health_list": [
    "ข้อควรระวังสุขภาพจิตและกาย..."
  ],
  "life_strategy": "กลยุทธ์ชีวิตระยะยาวในการเติบโต...",
  "diagnosis": "คำวินิจฉัยและแนวทางแก้ไขหลักจากเมนเทอร์...",
  "father_desc": "ภาพสะท้อนจากพ่อ สิ่งที่สอน ปมในใจ...\\n\\n**หลักฐาน**\\nSun: ...\\nSaturn: ...",
  "mother_desc": "ภาพสะท้อนจากแม่ สิ่งที่สอน ปมในใจ...\\n\\n**หลักฐาน**\\nMoon: ...\\nAspect: ...",
  "family_atmosphere": "บรรยากาศในบ้านและการเลี้ยงดู...\\n\\n**หลักฐาน**\\nMoon เรือน 12\\nSun ☍ Saturn",
  "family_dev": "คำแนะนำความสัมพันธ์ในครอบครัว"
}
"""
    content = f"ชื่อผู้ใช้: {user_name}\n[Planets]: {json.dumps(natal_planets, ensure_ascii=False)}\n[Aspects]: {json.dumps(natal_aspects, ensure_ascii=False)}"
    
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[{"role": "system", "content": prompt}, {"role": "user", "content": content}],
        temperature=0.2
    )
    return res.choices[0].message.content
