import json
import os
from openai import OpenAI

# สร้าง Client เชื่อมต่อ OpenAI API
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_natal_7_categories(user_name, natal_planets, natal_houses, natal_aspects, school_rules):
    """วิเคราะห์พื้นดวง 7 หมวดหมู่หลัก พร้อมตรวจสอบสัญลักษณ์ (i) อัตโนมัติ"""
    natal_lib = school_rules.get("natal_categories", {})
    
    # ตรวจสอบว่าคลังความรู้หมวดไหนว่าง เพื่อระบุสถานะการติดสัญลักษณ์ (i)
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


def analyze_transit_qa(user_name, question, natal_planets, transit_planets, transit_aspects, school_rules):
    """วิเคราะห์การตอบคำถามโดยจับคู่ดวงเกิด (Natal) กับ ดาวจร Real-time (Transit)"""
    prompt = f"""
คุณคือนักโหราศาสตร์สากลเชิงพัฒนาศักยภาพ (Evolutionary Astrologer)
โทนเสียง: ผู้เชี่ยวชาญ มีหลักการ ตรงประเด็น ไม่พูดเยอะ

หน้าที่ของคุณ:
1. วิเคราะห์ดาวจร (Transit Planets) ที่มากระทบดาวเกิด (Natal Planets) และมุมสัมพันธ์ (Transit Aspects)
2. ตอบคำถามของผู้ใช้ตรงประเด็น ประเมินจังหวะเวลา (Timing) และเสนอทางออกเชิงจิตวิทยาพัฒนาศักยภาพ
3. ห้ามใช้เครื่องหมาย Markdown Heading (#, ##, ###) ให้ใช้ตัวหนา **ชื่อหัวข้อ** เท่านั้น
4. ต้องตบท้ายด้วยส่วน **หลักฐานที่ใช้วิเคราะห์:** โดยระบุดาวจรที่ทำมุมกับดาวเกิดจริงเสมอ (เช่น Transit Saturn Square Natal MC)

โครงสร้างการตอบ:
**บทวิเคราะห์และจังหวะเวลา**
(คำตอบเจาะจงกับคำถาม)

**แนวทางแก้ไขและข้อคิดพัฒนาตนเอง**
(คำแนะนำเชิงรุก)

**หลักฐานที่ใช้วิเคราะห์:**
(ระบุดาวจร/ดาวเกิด/Aspect ที่ใช้)
"""
    content = f"ผู้ถาม: {user_name}\nคำถาม: {question}\n[Natal Planets]: {json.dumps(natal_planets, ensure_ascii=False)}\n[Transit Planets Realtime]: {json.dumps(transit_planets, ensure_ascii=False)}\n[Transit Aspects]: {json.dumps(transit_aspects, ensure_ascii=False)}"

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": prompt}, {"role": "user", "content": content}],
        temperature=0.2
    )
    return res.choices[0].message.content


def analyze_deep_report_json(user_name, natal_planets, natal_houses, natal_aspects, school_rules):
    """วิเคราะห์รายงานปมลึก 12 มิติ (Deep Report)"""
    deep_rules = school_rules.get("deep_report_rules", "")
    prompt = f"""
คุณคือนักโหราศาสตร์สากลเชิงพัฒนาศักยภาพ (Evolutionary Astrologer)
โทนเสียง: ผู้เชี่ยวชาญ มีหลักการ ตรงประเด็น ไม่พูดเยอะ

วิเคราะห์ Deep Report (12 มิติ) ตามสูตรต่อไปนี้:
{deep_rules}

ห้ามใช้เครื่องหมาย #, ##, ### เด็ดขาด และระบุหลักฐานที่ใช้วิเคราะห์ประกอบทุกมิติ
"""
    content = f"ผู้ถาม: {user_name}\n[Natal Planets]: {json.dumps(natal_planets, ensure_ascii=False)}\n[Natal Houses]: {json.dumps(natal_houses, ensure_ascii=False)}\n[Natal Aspects]: {json.dumps(natal_aspects, ensure_ascii=False)}"

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": prompt}, {"role": "user", "content": content}],
        temperature=0.2
    )
    return res.choices[0].message.content
