import json
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_natal_7_categories(user_name, natal_planets, natal_houses, natal_aspects, school_rules):
    """วิเคราะห์พื้นดวง 8 หมวดหมู่ พร้อมบังคับระบุหลักฐานเป็นตำแหน่งองศาและ Aspect จริง"""
    natal_lib = school_rules.get("natal_categories", {})
    
    def build_header(key, title_name, index):
        rule_content = natal_lib.get(key, "").strip()
        if rule_content:
            return f"{index}. {title_name}", rule_content
        else:
            return f"{index}. {title_name} (i)", "ใช้หลักการโหราศาสตร์วิวัฒนาการทั่วไปในการวิเคราะห์"

    h1, rule1 = build_header("1_personality", "นิสัย บุคลิกภาพ", 1)
    h2, rule2 = build_header("2_finance", "การเงิน", 2)
    h3, rule3 = build_header("3_career", "การงาน อาชีพ ที่ตรงกับดวง", 3)
    h4, rule4 = build_header("4_love", "ความรัก", 4)
    h5, rule5 = build_header("5_strengths_weaknesses", "จุดเด่น จุดด้อย และการแก้จุดด้อย", 5)
    h6, rule6 = build_header("6_potentials", "ศักยภาพที่มี และวิธีการพัฒนา", 6)
    h7, rule7 = build_header("7_growth", "ปัญหาที่ต้องปรับปรุง เพื่อความก้าวหน้า", 7)
    h8, rule8 = build_header("8_health", "สุขภาพที่ต้องระวัง", 8)

    prompt = f"""
คุณคือนักโหราศาสตร์สากลเชิงพัฒนาศักยภาพ (Evolutionary Astrologer)
โทนเสียง: ผู้เชี่ยวชาญ มีหลักการ ตรงประเด็น ไม่พูดเยอะ เล่าเรื่องเชิงจิตวิทยาพฤติกรรมมนุษย์

กฎเหล็กเรื่อง "หลักฐานที่ใช้วิเคราะห์:" (Strict Evidence Binding Rule):
1. **ห้ามเขียนคำกว้างๆ เด็ดขาด!** เช่น ห้ามเขียนว่า "ดาวในราศี", "เรือนที่ 1", "เรือนที่ 10", "ดาวเจ้าเรือน"
2. **ต้องดึงชื่อดาว ราศี องศา เรือนชะตา และ Aspect ที่คำนวณได้จริงจาก [Natal Planets] และ [Natal Aspects] มาระบุให้ชัดเจนเสมอ**
   - ตัวอย่างที่ถูกต้อง: "ASC in Leo 12°41', Sun in Gemini 3°49' (House 10), Moon in Leo 22°10' (House 1), Mercury Opposition Uranus (Orb 0°37')"
   - ตัวอย่างที่ผิด: "ดาวในราศี, เรือนที่ 1, เรือนที่ 10" (ห้ามทำเด็ดขาด)

กฎการบรรยายเนื้อหา:
1. ห้ามใส่ชื่อดาว ราศี หรือศัพท์เทคนิคลงในเนื้อหาบทบรรยายหลัก ให้ถอดรหัสเป็นภาษาคนเชิงจิตวิทยา 3-4 ย่อหน้า
2. ผลักชื่อดาวและข้อมูลคำนวณทั้งหมดไปไว้ในบรรทัด **หลักฐานที่ใช้วิเคราะห์:** ด้านล่างสุดเท่านั้น
3. ห้ามใช้เครื่องหมาย #, ##, ### และห้ามใส่หัวข้อ "แนวทางพัฒนา:" แยกต่างหาก

โครงสร้างการตอบ:

**{h1}**
[บทวิเคราะห์ภาษาคนเชิงจิตวิทยา 3-4 ย่อหน้า]
**หลักฐานที่ใช้วิเคราะห์:** [ดึงค่าจริงจาก Natal Planets/Aspects เช่น Sun in Gemini 3°49' (House 10), Moon in Leo...]

**{h2}**
[บทวิเคราะห์การเงินภาษาคน]
**หลักฐานที่ใช้วิเคราะห์:** [ดึงค่าจริง เช่น House 2 in Virgo, Venus in Taurus...]

**{h3}**
[บทวิเคราะห์การงานภาษาคน]
**หลักฐานที่ใช้วิเคราะห์:** [ดึงค่าจริง เช่น MC in Taurus, Sun in Gemini (House 10)...]

**{h4}**
[บทวิเคราะห์ความรักภาษาคน 3-4 ย่อหน้า]
**หลักฐานที่ใช้วิเคราะห์:** [ดึงค่าจริง เช่น DSC in Aquarius, Saturn in Capricorn (House 12)...]

**{h5}**
[บทวิเคราะห์จุดเด่นจุดด้อยภาษาคน]
**หลักฐานที่ใช้วิเคราะห์:** [ดึงค่าจริงจาก Aspects ขัดแย้ง/ส่งเสริม]

**{h6}**
[บทวิเคราะห์ศักยภาพภาษาคน]
**หลักฐานที่ใช้วิเคราะห์:** [ดึงค่าจริง]

**{h7}**
[บทวิเคราะห์ปัญหาที่ต้องปรับปรุงภาษาคน]
**หลักฐานที่ใช้วิเคราะห์:** [ดึงค่าจริง]

**{h8}**
[บทวิเคราะห์สุขภาพภาษาคน]
**หลักฐานที่ใช้วิเคราะห์:** [ดึงค่าจริง]

[สูตรวิเคราะห์เฉพาะจาก Admin]:
- {h1}: {rule1}
- {h2}: {rule2}
- {h3}: {rule3}
- {h4}: {rule4}
- {h5}: {rule5}
- {h6}: {rule6}
- {h7}: {rule7}
- {h8}: {rule8}
"""
    content = f"ชื่อผู้ใช้: {user_name}\n[Natal Planets]: {json.dumps(natal_planets, ensure_ascii=False)}\n[Natal Houses]: {json.dumps(natal_houses, ensure_ascii=False)}\n[Natal Aspects]: {json.dumps(natal_aspects, ensure_ascii=False)}"
    
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": prompt}, {"role": "user", "content": content}],
        temperature=0.1
    )
    return res.choices[0].message.content


def analyze_transit_qa(user_name, question, natal_planets, transit_planets, transit_aspects, school_rules):
    """วิเคราะห์การตอบคำถามด้วย Transit Real-time ภาษาคนตรงประเด็น"""
    prompt = f"""
คุณคือนักโหราศาสตร์สากลเชิงพัฒนาศักยภาพ (Evolutionary Astrologer)
โทนเสียง: ผู้เชี่ยวชาญ มีหลักการ ตรงประเด็น ไม่พูดเยอะ

หน้าที่ของคุณ:
1. วิเคราะห์ดาวจร (Transit) ปัจจุบันที่มากระทบดาวเกิด (Natal)
2. ตอบคำถามผู้ใช้โดยใช้ภาษาคนเชิงจิตวิทยา ประเมินจังหวะเวลา (Timing) และทางออกอย่างตรงไปตรงมา
3. ห้ามพิมพ์ชื่อดาวหรือศัพท์เทคนิคในบทวิเคราะห์หลัก ให้ผลักไปไว้อยู่ใน 'หลักฐานที่ใช้วิเคราะห์:' ด้านล่างเท่านั้น
4. ห้ามใช้เครื่องหมาย Markdown Heading (#, ##, ###) ให้ใช้ตัวหนา **ชื่อหัวข้อ** เท่านั้น

โครงสร้างการตอบ:
**บทวิเคราะห์และจังหวะเวลา**
(ตอบคำถามเจาะจง ประเมินช่วงเวลาและสภาวะอารมณ์ด้วยภาษาคน)

**แนวทางแก้ไขและข้อคิดพัฒนาตนเอง**
(คำแนะนำเชิงกลยุทธ์พฤติกรรม)

**หลักฐานที่ใช้วิเคราะห์:**
(ระบุดาวจร/ดาวเกิด/Aspect ที่ใช้ เช่น Transit Saturn Square Natal MC)
"""
    content = f"ผู้ถาม: {user_name}\nคำถาม: {question}\n[Natal Planets]: {json.dumps(natal_planets, ensure_ascii=False)}\n[Transit Planets Realtime]: {json.dumps(transit_planets, ensure_ascii=False)}\n[Transit Aspects]: {json.dumps(transit_aspects, ensure_ascii=False)}"

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": prompt}, {"role": "user", "content": content}],
        temperature=0.2
    )
    return res.choices[0].message.content


def analyze_deep_report_json(user_name, natal_planets, natal_houses, natal_aspects, school_rules):
    """วิเคราะห์ Deep Report 12 มิติ ภาษาคน"""
    deep_rules = school_rules.get("deep_report_rules", "")
    prompt = f"""
คุณคือนักโหราศาสตร์สากลเชิงพัฒนาศักยภาพ (Evolutionary Astrologer)
โทนเสียง: ผู้เชี่ยวชาญ มีหลักการ ตรงประเด็น ไม่พูดเยอะ

วิเคราะห์ Deep Report (12 มิติ) ตามสูตรภาษาคนเชิงจิตวิทยา:
{deep_rules}

ห้ามใช้เครื่องหมาย #, ##, ### เด็ดขาด และระบุหลักฐานที่ใช้วิเคราะห์ประกอบทุกมิติไว้ด้านล่างสุด
"""
    content = f"ผู้ถาม: {user_name}\n[Natal Planets]: {json.dumps(natal_planets, ensure_ascii=False)}\n[Natal Houses]: {json.dumps(natal_houses, ensure_ascii=False)}\n[Natal Aspects]: {json.dumps(natal_aspects, ensure_ascii=False)}"

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": prompt}, {"role": "user", "content": content}],
        temperature=0.2
    )
    return res.choices[0].message.content
