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

def analyze_deep_report_json(user_name, natal_planets, natal_houses, natal_aspects, deep_rules):
    prompt = f"""
คุณคือนักโหราศาสตร์สากลเชิงพัฒนาศักยภาพผู้เชี่ยวชาญ
หน้าที่: วิเคราะห์ดวงชะตาอย่างลึกซึ้งเพื่อสร้าง JSON Data 12 มิติ 

ข้อบังคับระดับสูงสุด (CRITICAL):
1. ตอบกลับเป็น JSON Object เท่านั้น
2. **คุณต้องวิเคราะห์ตาม "สูตรและขั้นตอน" ที่สำนักกำหนดไว้ด้านล่างนี้อย่างเคร่งครัด** ห้ามใช้ความหมายแบบกว้างๆ ให้ประมวลผลทีละ Step ตามกฎที่ให้ไป
3. การอธิบายเนื้อหา: ห้ามใช้ศัพท์เทคนิคโหราศาสตร์ เล่าเป็นเรื่องราวและพฤติกรรมมนุษย์
4. ทุกหัวข้อ ต้องมีส่วน **"หลักฐานที่ใช้วิเคราะห์"** หรือ **"แปลมาจาก"** โดยระบุดาว ราศี เรือน หรือ Aspect ที่ตรงตาม 'สูตรของสำนัก'

[สูตรวิเคราะห์ Deep Report ประจำสำนัก]
{deep_rules}

โครงสร้าง JSON ที่ต้องส่งกลับ (ใส่ข้อมูลให้ครบ):
{{
  "executive_summary": "เล่าเรื่องราวตามสูตร Executive Summary 2 ย่อหน้า\\n\\n**หลักฐานที่ใช้วิเคราะห์**\\nราศี: ...\\nเรือน: ...\\nAspect: ...",
  "identity_list": ["เรื่องราวข้อ 1...", "เรื่องราวข้อ 2..."],
  "identity_dev": "คำแนะนำ...\\n\\n**แปลมาจาก**\\nราศี: ...\\nเรือน: ...\\nAspect: ...",
  "shadow_list": ["ปมข้อ 1..."],
  "shadow_dev": "คำแนะนำ...\\n\\n**แปลมาจาก**\\n...",
  "wound_list": ["แผลใจ..."],
  "wound_dev": "วิธีแก้...\\n\\n**แปลมาจาก**\\n...",
  "sabotage_list": ["สิ่งที่ทำให้พลาด..."],
  "sabotage_mechanism": "กลไกในใจ...\\n\\n**แปลมาจาก**\\n...",
  "career_summary": "สรุปทิศทางอาชีพ",
  "career_match_list": ["อาชีพ 1", "อาชีพ 2"],
  "career_avoid_list": ["อาชีพที่ห้ามทำ 1"],
  "career_dev": "ข้อแนะนำ...\\n\\n**แปลมาจาก**\\n...",
  "money_list": ["พิกัดเปิดทรัพย์..."],
  "edu_list": ["สายการเรียน..."],
  "rel_list": ["พลวัตความรัก..."],
  "health_list": ["การฟื้นฟูจิตใจ..."],
  "life_strategy": "กลยุทธ์ระยะยาว...",
  "diagnosis": "คำวินิจฉัยรวม...",
  "father_desc": "ภาพสะท้อนจากพ่อ...\\n\\n**หลักฐาน**\\n...",
  "mother_desc": "ภาพสะท้อนจากแม่...\\n\\n**หลักฐาน**\\n...",
  "family_atmosphere": "บรรยากาศครอบครัว...\\n\\n**หลักฐาน**\\n...",
  "family_dev": "คำแนะนำครอบครัว"
}}
"""
    content = f"ชื่อผู้ใช้: {user_name}\n[Planets]: {json.dumps(natal_planets, ensure_ascii=False)}\n[Aspects]: {json.dumps(natal_aspects, ensure_ascii=False)}"
    
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[{"role": "system", "content": prompt}, {"role": "user", "content": content}],
        temperature=0.2
    )
    return res.choices[0].message.content

