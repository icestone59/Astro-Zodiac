import os
import json
import openai

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY")) if os.getenv("OPENAI_API_KEY") else None

def analyze_natal_7_categories(user_name, natal_planets, natal_houses, natal_aspects, school_rules):
    prompt = f"""
คุณคือนักโหราศาสตร์สากลเชิงพัฒนาศักยภาพ (Evolutionary Astrologer)
โทนเสียง: ผู้เชี่ยวชาญ มีหลักการ ตรงประเด็น ไม่พูดเยอะ 

หน้าที่: แปลง Birth Chart เป็นบทวิเคราะห์พฤติกรรมเชิงจิตวิทยา
เงื่อนไขสำคัญ:
1. การอธิบายเนื้อหา ห้ามใช้ศัพท์เทคนิคโหราศาสตร์ ให้เล่าเป็นเรื่องราวและพฤติกรรมมนุษย์
2. **บังคับ:** ท้ายการวิเคราะห์ทุกหมวดหมู่ ต้องมีส่วน 'หลักฐาน' เพื่อบอกว่าคุณใช้ดาว, เรือน หรือ Aspect อะไรในการแปลผล (เช่น หลักฐาน: Sun ☍ Saturn, Moon ในเรือน 12)
3. ตบท้ายด้วยแนวทางพัฒนาศักยภาพเสมอ

วิเคราะห์ 7 หมวดหมู่:
1. นิสัย บุคลิกภาพ
2. การเงิน
3. การงาน อาชีพ ที่ตรงกับดวง
4. ความรัก
5. จุดเด่น จุดด้อย และการแก้จุดด้อย
6. ศักยภาพที่มี และวิธีการพัฒนา
7. ปัญหาที่ต้องปรับปรุง เพื่อความก้าวหน้า

[ตัวอย่างโครงสร้างคำตอบ 1 หมวด]
## 4. ความรัก
(อธิบายเป็นสภาวะอารมณ์และพฤติกรรม...)
**แนวทางพัฒนา:** (ข้อแนะนำ...)

**หลักฐาน:**
- Venus ใน Taurus (ความมั่นคงในรัก)
- Venus ☍ Pluto (ความรักที่มีความคาดหวังและซับซ้อน)
- เรือนที่ 7...
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
2. แปลงดาวกระทบกันเป็นช่วงเวลาและเหตุการณ์จริง ห้ามใช้ศัพท์เทคนิคในเนื้อหาคำอธิบาย
3. **บังคับ:** ท้ายคำตอบต้องมี 'หลักฐาน' ระบุชัดเจนว่าดาวจรดวงไหน ทำมุมอะไรกับดาวเกิด หรือเข้าเรือนไหน

[ตัวอย่างคำตอบ]
(วิเคราะห์สภาวะที่เจอ...)
(ระบุช่วงเวลาและทางแก้...)

**หลักฐาน:**
- Transit Saturn เล็ง Natal Sun...
- Transit Jupiter เข้าเรือนที่ 10...
"""
    content = f"คำถาม: {question}\n[Natal]: {json.dumps(natal_data)}\n[Natal Aspects]: {json.dumps(natal_aspects)}\n[Transit]: {json.dumps(transit_data)}"
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": prompt}, {"role": "user", "content": content}],
        temperature=0.2
    )
    return res.choices[0].message.content
