import json
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_natal_7_categories(user_name, natal_planets, natal_houses, natal_aspects, school_rules):
    """วิเคราะห์พื้นดวง 8 หมวดหมู่หลัก (รวมสุขภาพ) พร้อมควบคุมสัญลักษณ์ (i) ด้วย Python"""
    natal_lib = school_rules.get("natal_categories", {})
    
    # ฟังก์ชันตรวจสอบข้อมูลจาก Admin ใน Python โดยตรง (ป้องกัน AI สับสนเรื่อง (i) 100%)
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
โทนเสียง: ผู้เชี่ยวชาญ มีหลักการ ตรงประเด็น ไม่พูดเยอะ เล่าเรื่องเชิงจิตวิทยาพฤติกรรมมนุษย์อย่างลึกซึ้ง

กฎเหล็กเรื่องรูปแบบและการเล่าเรื่อง:
1. ห้ามใช้เครื่องหมาย #, ##, ### หรือ #### เด็ดขาด ให้ใช้ตัวหนา **ชื่อหัวข้อ** ตามที่กำหนดไว้เท่านั้น
2. **ห้ามใส่หัวข้อ "แนวทางพัฒนา:" เด็ดขาด** ให้เล่าบทวิเคราะห์และวิธีบริหารจัดการรวมอยู่ในเนื้อหาหลักทันที
3. บังคับใช้ชื่อหัวข้อตามที่กำหนดให้นี้เท่านั้น (ห้ามแก้ไข เติม หรือลบสัญลักษณ์ (i) ออกเองเด็ดขาด)
4. สไตล์การเล่าเรื่อง: ห้ามแปลแบบสั้นๆ หรือ Dictionary Reading (เช่น ห้ามเขียนแค่ "Sun ใน Gemini แปลว่าช่างพูด") แต่ต้องเล่าร้อยเรียงเป็น Layering เชิงจิตวิทยา:
   - อธิบายภาพที่คนอื่นเห็น (ASC) $\rightarrow$ ตัวตนเชิงสังคม (Sun/House) $\rightarrow$ กระบวนการคิดและการตั้งคำถาม (Mercury/Aspects) $\rightarrow$ แรงผลักในการลงมือทำ (Mars/Venus)
   - ชี้ให้เห็นปม ความขัดแย้งในตัวเอง และศักยภาพที่แท้จริง
5. ทุกหมวดต้องตบท้ายด้วย **หลักฐานที่ใช้วิเคราะห์:** โดยระบุดาว, ราศี, เรือนชะตา หรือ Aspect ที่ใช้คำนวณจริงเสมอ

โครงสร้างการตอบ (ต้องใช้ชื่อหัวข้อตามนี้เป๊ะๆ):

**{h1}**
[บทวิเคราะห์พฤติกรรมและระบบความคิดเชิงลึก]
**หลักฐานที่ใช้วิเคราะห์:** [ระบุดาว/เรือน/Aspect]

**{h2}**
[บทวิเคราะห์สภาวะทางการเงินและการสร้างคุณค่า]
**หลักฐานที่ใช้วิเคราะห์:** [ระบุดาว/เรือน/Aspect]

**{h3}**
[บทวิเคราะห์ทิศทางอาชีพและการแสดงศักยภาพ]
**หลักฐานที่ใช้วิเคราะห์:** [ระบุดาว/เรือน/Aspect]

**{h4}**
[บทวิเคราะห์รูปแบบความสัมพันธ์และอารมณ์ความรัก]
**หลักฐานที่ใช้วิเคราะห์:** [ระบุดาว/เรือน/Aspect]

**{h5}**
[บทวิเคราะห์จุดเด่น ปมในใจ และการบริหารจุดด้อย]
**หลักฐานที่ใช้วิเคราะห์:** [ระบุดาว/เรือน/Aspect]

**{h6}**
[บทวิเคราะห์พรสวรรค์ซ่อนเร้นและการยกระดับชีวิต]
**หลักฐานที่ใช้วิเคราะห์:** [ระบุดาว/เรือน/Aspect]

**{h7}**
[บทวิเคราะห์ข้อผิดพลาดซ้ำๆ และกุญแจในการปลดล็อกตัวเอง]
**หลักฐานที่ใช้วิเคราะห์:** [ระบุดาว/เรือน/Aspect]

**{h8}**
[บทวิเคราะห์จุดอ่อนทางร่างกาย อวัยวะที่ต้องระวัง และความสัมพันธ์ระหว่างสภาวะจิตใจกับสุขภาพ]
**หลักฐานที่ใช้วิเคราะห์:** [ระบุดาว/เรือน 6/เรือน 12/Aspects]

[กฎวิเคราะห์เฉพาะของสำนักที่ Admin กรอกไว้]:
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
