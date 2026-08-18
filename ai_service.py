import json
import os
from openai import OpenAI

# 1. Export ตัวแปร client ที่ main.py เรียกใช้
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_natal_7_categories(user_name, chart_data, school_rules):
    """วิเคราะห์พื้นดวง 8 หมวดหมู่ บังคับระบุ Ruler และพิกัดดาราศาสตร์ในกล่องหลักฐาน"""
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

กฎเหล็กบทบรรยายหลัก (Strict Narrative Rules):
1. **ห้ามพิมพ์ชื่อดาว, ราศี, เรือนชะตา, Aspect หรือคำว่า Ruler (เช่น Sun, Moon, ASC, Venus, House 1) ลงในบทบรรยายหลักเด็ดขาดทุกหมวด!**
2. ถอดความหมายทั้งหมดเป็นภาษาคนเชิงจิตวิทยา 3-4 ย่อหน้าต่อหมวด
3. ห้ามใช้เครื่องหมาย #, ##, ### และห้ามใส่หัวข้อ "แนวทางพัฒนา:" แยกออกมา

กฎเหล็กสำหรับ "หลักฐานที่ใช้วิเคราะห์:" (Strict Evidence & Ruler Rules):
1. **ต้องระบุค่าตำแหน่งจริง และ Ruler ของเรือนนั้นๆ จาก [Ruler Mapping] เสมอ!**
   - หมวด 1 (นิสัย): ต้องระบุ ASC + Ruler 1 + Sun + Moon
   - หมวด 2 (การเงิน): ต้องระบุ House 2 + Ruler 2 + ดาวใน H2/H8
   - หมวด 3 (การงาน): ต้องระบุ MC + Ruler 10 + House 10
   - หมวด 4 (ความรัก): ต้องระบุ DSC + Ruler 7 + Venus + Moon + Mars
2. ห้ามใช้คำกว้างๆ เช่น "ดาวในราศี" หรือ "เรือนที่ 1" เด็ดขาด ต้องดึงค่าองศาจริงมาใส่เท่านั้น

โครงสร้างการตอบ:

**{h1}**
[บทวิเคราะห์พฤติกรรมและระบบความคิดภาษาคนเชิงจิตวิทยา 3-4 ย่อหน้า]
**หลักฐานที่ใช้วิเคราะห์:** ASC in [Sign], Ruler 1 ([Planet]) in [Sign] (House [X]), Sun in..., Moon in...

**{h2}**
[บทวิเคราะห์การเงินภาษาคน 3-4 ย่อหน้า]
**หลักฐานที่ใช้วิเคราะห์:** House 2 in [Sign], Ruler 2 ([Planet]) in [Sign] (House [X]), Venus in...

**{h3}**
[บทวิเคราะห์การงานอาชีพภาษาคน 3-4 ย่อหน้า]
**หลักฐานที่ใช้วิเคราะห์:** MC in [Sign], Ruler 10 ([Planet]) in [Sign] (House [X]), House 10 in...

**{h4}**
[บทวิเคราะห์ความรักตามสูตร 6 ขั้นตอน ภาษาคน 3-4 ย่อหน้า]
**หลักฐานที่ใช้วิเคราะห์:** DSC in [Sign], Ruler 7 ([Planet]) in [Sign] (House [X]), Venus in..., Moon in..., Mars in...

**{h5}**
[บทวิเคราะห์จุดเด่นจุดด้อยภาษาคน 3-4 ย่อหน้า]
**หลักฐานที่ใช้วิเคราะห์:** [ดาวเด่น/มุมสัมพันธ์ขัดแย้งจริง]

**{h6}**
[บทวิเคราะห์ศักยภาพซ่อนเร้นภาษาคน 3-4 ย่อหน้า]
**หลักฐานที่ใช้วิเคราะห์:** [North Node/ดาวและเรือนที่ส่งเสริม]

**{h7}**
[บทวิเคราะห์ปัญหาที่ต้องปรับปรุงภาษาคน 3-4 ย่อหน้า]
**หลักฐานที่ใช้วิเคราะห์:** [Saturn/Hard Aspects จริง]

**{h8}**
[บทวิเคราะห์สุขภาพภาษาคน 3-4 ย่อหน้า]
**หลักฐานที่ใช้วิเคราะห์:** House 6 in [Sign], Ruler 6 ([Planet]) in..., House 12 in...

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
    content = f"ชื่อผู้ใช้: {user_name}\n[Chart Data & Ruler Mapping]: {json.dumps(chart_data, ensure_ascii=False)}"
    
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": prompt}, {"role": "user", "content": content}],
        temperature=0.1
    )
    return res.choices[0].message.content


def analyze_transit_qa(user_name, question, chart_data):
    """วิเคราะห์คำถามเจาะจงด้วย Transit Real-time vs Natal Chart"""
    prompt = f"""
คุณคือนักโหราศาสตร์สากลเชิงพัฒนาศักยภาพ (Evolutionary Astrologer)
โทนเสียง: ผู้เชี่ยวชาญ มีหลักการ ตรงประเด็น ไม่พูดเยอะ

หน้าที่ของคุณ:
1. นำข้อมูล [Transit Planets Real-time] มาจับคู่กับ [Natal Planets] เพื่อตอบคำถามผู้ใช้
2. ประเมินช่วงเวลา (Timing) สภาวะอารมณ์ และกลยุทธ์ทางออกด้วยภาษาคนเชิงจิตวิทยา
3. ห้ามใส่ชื่อดาวในเนื้อหาบทวิเคราะห์ ให้นำไปใส่ในบรรทัด 'หลักฐานที่ใช้วิเคราะห์:' ท้ายคำตอบเท่านั้น

โครงสร้างการตอบ:
**บทวิเคราะห์และจังหวะเวลา**
(ตอบคำถามตรงประเด็น ประเมิน timing และสภาวะด้วยภาษาคน)

**แนวทางแก้ไขและข้อคิดพัฒนาตนเอง**
(คำแนะนำเชิงกลยุทธ์พฤติกรรม)

**หลักฐานที่ใช้วิเคราะห์:**
(ระบุดาวจร Real-time + ดาวเกิดที่รับมุมกระทบ เช่น Transit Saturn in Pisces (House 10) Square Natal Sun in Gemini)
"""
    content = f"ผู้ถาม: {user_name}\nคำถาม: {question}\n[Chart Data]: {json.dumps(chart_data, ensure_ascii=False)}"

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": prompt}, {"role": "user", "content": content}],
        temperature=0.1
    )
    return res.choices[0].message.content


def analyze_deep_report_json(user_name, chart_data, school_rules):
    """ฟังก์ชันรองรับ Deep Report 12 มิติ ที่เรียกจาก main.py"""
    deep_rules = school_rules.get("deep_report_rules", "")
    prompt = f"""
คุณคือนักโหราศาสตร์สากลเชิงพัฒนาศักยภาพ (Evolutionary Astrologer)
โทนเสียง: ผู้เชี่ยวชาญ มีหลักการ ตรงประเด็น ไม่พูดเยอะ

วิเคราะห์ Deep Report (12 มิติ) ตามสูตรภาษาคนเชิงจิตวิทยา:
{deep_rules}

ห้ามใช้เครื่องหมาย #, ##, ### เด็ดขาด และระบุหลักฐานที่ใช้วิเคราะห์ประกอบทุกมิติไว้ด้านล่างสุด
"""
    content = f"ผู้ถาม: {user_name}\n[Chart Data]: {json.dumps(chart_data, ensure_ascii=False)}"

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": prompt}, {"role": "user", "content": content}],
        temperature=0.1
    )
    return res.choices[0].message.content
