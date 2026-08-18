import json
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_natal_7_categories(user_name, natal_planets, natal_houses, natal_aspects, school_rules):
    """วิเคราะห์พื้นดวง 8 หมวดหมู่หลัก ด้วย Pattern ภาษาคนเชิงจิตวิทยา 100%"""
    natal_lib = school_rules.get("natal_categories", {})
    
    # ระบบตรวจสอบและกำหนดสัญลักษณ์ (i) อัตโนมัติด้วย Python
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
โทนเสียง: ผู้เชี่ยวชาญ มีหลักการ ตรงประเด็น ไม่พูดเยอะ เล่าเรื่องด้วยภาษาจิตวิทยาพฤติกรรมมนุษย์อย่างลึกซึ้ง

กฎเหล็กเรื่อง Pattern และภาษา (Strict Master Rules):
1. **ห้ามพิมพ์ชื่อดาว, ราศี, เรือนชะตา หรือ Aspect (เช่น Sun, Moon, Venus, Mars, Gemini, House 10, Square) ในเนื้อหาบรรยายหลักเด็ดขาดทุกหมวด!**
   - ตัวอย่างที่ผิด: "เนื่องจากดวงอาทิตย์ในราศีเมถุน อยู่เรือนที่ 10 ทำให้คุณ..." (ห้ามทำเด็ดขาด)
   - ตัวอย่างที่ถูกต้อง: "คุณเป็นคนที่ภายนอกดูมีตัวตนชัดเจน และมีความต้องการที่จะสร้างสรรค์ผลงานให้มีความหมายต่อสังคม..."
   - ชื่อดาวและตำแหน่งทั้งหมด ต้องถูกนำไปใส่ในส่วน **หลักฐานที่ใช้วิเคราะห์:** ที่อยู่ท้ายหัวข้อเท่านั้น!

2. **โครงสร้างการเล่าเรื่องแบบ Layering (3-4 ย่อหน้าต่อหมวด):**
   - ย่อหน้า 1 (สภาวะภายนอก/พฤติกรรมหลัก): พฤติกรรม หรือภาพลักษณ์ที่แสดงออกให้โลกเห็น
   - ย่อหน้า 2 (ความรู้สึก/ระบบความคิดภายใน): แรงขับทางจิตวิทยา กลไกการประมวลผล หรือความต้องการความปลอดภัยทางอารมณ์
   - ย่อหน้า 3 (ปม/ข้อขัดแย้งและการบริหารจัดการ): ความขัดแย้งในตัวเอง และแนวทางการปรับตัว/วิธีคิดเพื่อก้าวหน้า (สอดแทรกข้อคิดโดยไม่ต้องเขียนหัวข้อแยก)

3. **ห้ามใช้เครื่องหมาย #, ##, ### เด็ดขาด** ให้ใช้ตัวหนา **ชื่อหัวข้อ** ตามที่กำหนดไว้เท่านั้น
4. **ห้ามใส่คำว่า "แนวทางพัฒนา:" เด็ดขาด** ให้หลอมรวมกลยุทธ์การพัฒนาเข้าไปในบทบรรยายหลักทันที
5. ทุกหมวดต้องตบท้ายด้วย **หลักฐานที่ใช้วิเคราะห์:** โดยระบุดาว, ราศี, เรือนชะตา หรือ Aspect ที่ใช้คำนวณจริงเสมอ

โครงสร้างการตอบ (บังคับใช้ชื่อหัวข้อตามนี้):

**{h1}**
[บทวิเคราะห์บุคลิกภาพและตัวตนภาษาคนเชิงจิตวิทยา 3-4 ย่อหน้า]
**หลักฐานที่ใช้วิเคราะห์:** [ระบุดาว/เรือน/Aspect]

**{h2}**
[บทวิเคราะห์การเงินและ Mindset ทรัพย์สินภาษาคน 3-4 ย่อหน้า]
**หลักฐานที่ใช้วิเคราะห์:** [ระบุดาว/เรือน/Aspect]

**{h3}**
[บทวิเคราะห์การงานอาชีพและเป้าหมายชีวิตภาษาคน 3-4 ย่อหน้า]
**หลักฐานที่ใช้วิเคราะห์:** [ระบุดาว/เรือน/Aspect]

**{h4}**
[บทวิเคราะห์รูปแบบความสัมพันธ์และคู่ครองภาษาคน 3-4 ย่อหน้า]
**หลักฐานที่ใช้วิเคราะห์:** [ระบุดาว/เรือน/Aspect]

**{h5}**
[บทวิเคราะห์พรสวรรค์ ปมจิตวิทยา และวิธีรับมือจุดด้อยภาษาคน 3-4 ย่อหน้า]
**หลักฐานที่ใช้วิเคราะห์:** [ระบุดาว/เรือน/Aspect]

**{h6}**
[บทวิเคราะห์ศักยภาพซ่อนเร้นและการยกระดับชีวิตภาษาคน 3-4 ย่อหน้า]
**หลักฐานที่ใช้วิเคราะห์:** [ระบุดาว/เรือน/Aspect]

**{h7}**
[บทวิเคราะห์กับดักพฤติกรรมเดิมและกุญแจการเติบโตภาษาคน 3-4 ย่อหน้า]
**หลักฐานที่ใช้วิเคราะห์:** [ระบุดาว/เรือน/Aspect]

**{h8}**
[บทวิเคราะห์จุดอ่อนทางร่างกายและความเชื่อมโยงจิต-กายภาษาคน 3-4 ย่อหน้า]
**หลักฐานที่ใช้วิเคราะห์:** [ระบุดาว/เรือน/Aspect]

[สูตรและกฎเฉพาะของสำนักจาก Admin]:
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
