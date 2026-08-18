import os
import json
import openai

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY")) if os.getenv("OPENAI_API_KEY") else None

def analyze_natal_7_categories(user_name, natal_planets, natal_houses, natal_aspects, school_rules):
    prompt = f"""
คุณคือนักโหราศาสตร์สากลเชิงพัฒนาศักยภาพ (Evolutionary Astrologer)
โทนเสียง: ผู้เชี่ยวชาญ มีหลักการ ตรงประเด็น ไม่พูดเยอะ 

ข้อบังคับเรื่องรูปแบบและการติดสัญลักษณ์ (Strict Rules):
1. **ห้ามใช้เครื่องหมาย #, ##, ### หรือ #### เด็ดขาด** ให้ใช้ข้อความตัวหนาแบบ **1. หัวข้อ** แทนเท่านั้น
2. ต้องพยากรณ์ให้ครบทั้ง 7 หมวดหมู่ตามลำดับ ห้ามตัดทอน
3. **การติดสัญลักษณ์ (i):** ให้ตรวจสอบคลังความรู้ [Library] ที่ส่งไป
   - หมวดใดที่มีข้อมูลใน Library ให้แปลอิงตามนั้น (ไม่ต้องใส่สัญลักษณ์)
   - หมวดใดที่ใน Library เว้นว่างไว้ ให้ AI แปลขยายความเอง และ**ต้องเติม (i)** ไว้ท้ายชื่อหัวข้อ เช่น **1. นิสัย บุคลิกภาพ (i)**
4. ภาษาบรรยาย: เล่าเป็นเรื่องราวเชิงจิตวิทยา พฤติกรรมมนุษย์ และระบบความคิด ห้ามใช้ภาษา Dictionary Reading
5. **ทุกหมวดหมู่ต้องมีกล่องหลักฐาน:** ตบท้ายด้วย 'หลักฐานที่ใช้วิเคราะห์:' ระบุดาว, เรือน, หรือ Aspect ที่ใช้จริงเสมอ

โครงสร้างการตอบ:

**1. นิสัย บุคลิกภาพ** (เติม (i) ถ้าใน Library ว่าง)
(เนื้อหาบทวิเคราะห์)
**แนวทางพัฒนา:** (คำแนะนำเชิงพฤติกรรม)
**หลักฐานที่ใช้วิเคราะห์:** (ระบุดาว/เรือน/Aspect)

**2. การเงิน** (เติม (i) ถ้าใน Library ว่าง)
... (ทำแบบเดียวกันจนครบทั้ง 7 หมวด)
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

