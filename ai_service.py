import json
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def format_chart_context(chart_data):
    """จัดฟอร์แมตข้อมูลดวงและ Ruler เป็นข้อความชัดเจน ป้องกัน AI ข้ามการอ่าน Ruler"""
    birth = chart_data.get("birth_chart_degrees", {})
    rulers = chart_data.get("ruler_mapping", {})
    transits = chart_data.get("transit_degrees", {})

    text = "=== ตำแหน่งดาวกำเนิด (BIRTH CHART DEGREES) ===\n"
    for planet, info in birth.items():
        text += f"- {planet}: {info.get('sign')} {info.get('formatted')} (House {info.get('house')})\n"

    text += "\n=== ตำแหน่งเจ้าเรือน (HOUSE RULER MAPPING - บังคับนำไปแปลทุกหมวด) ===\n"
    for house, info in rulers.items():
        text += f"- {house} (ราศี {info.get('sign')}): ดาวเจ้าเรือนคือ {info.get('ruler_planet')} -> ไปสถิตที่ {info.get('ruler_pos')}\n"

    if transits:
        text += "\n=== ตำแหน่งดาวจร REAL-TIME (TRANSIT DEGREES) ===\n"
        for planet, info in transits.items():
            text += f"- Transit {planet}: {info.get('sign')} {info.get('formatted')} (สถิตใน Natal House {info.get('house_in_natal')})\n"

    return text


def analyze_natal_7_categories(user_name, chart_data, school_rules):
    chart_text = format_chart_context(chart_data)

    prompt = f"""
คุณคือนักโหราศาสตร์สากลเชิงพัฒนาศักยภาพ (Evolutionary Astrologer)
โทนเสียง: ผู้เชี่ยวชาญ มีหลักการ ตรงประเด็น วิเคราะห์เจาะลึกเชิงจิตวิทยาพฤติกรรมมนุษย์ ไม่ใช้คำอธิบายตื้นๆ

📌 กฎเหล็กการคำนวณและการแปลความหมาย (บังคับความยาว 3 ย่อหน้าต่อหมวด):
1. ในบทบรรยายของทุกหมวดหมู่ ต้องระบุชื่อ ดาว, ราศี (Sign), เรือนชะตา (House), มุมสัมพันธ์ (Aspect) และ **เจ้าเรือน (House Ruler)** สอดแทรกอธิบายลงในเนื้อหาอย่างละเอียด
2. บังคับเชื่อมโยงตำแหน่งเจ้าเรือน (House Ruler) ในคำแปลตามหมวดดังนี้:
   - 1. นิสัย บุคลิกภาพ: บังคับแปล ASC + ดาวใน House 1 + **ASC Ruler (เจ้าเรือนลัคนาไปสถิตที่ไหน)**
   - 2. การเงิน: บังคับแปล House 2 + **House 2 Ruler (เจ้าเรือนการเงินไปสถิตที่ไหน)** + Venus
   - 3. การงาน อาชีพ: บังคับแปล MC (House 10) + **House 10 Ruler (เจ้าเรือนการงานไปสถิตที่ไหน)** + House 6 Ruler
   - 4. ความรัก: บังคับแปล DSC (House 7) + **House 7 Ruler (เจ้าเรือนคู่ครองไปสถิตที่ไหน)** + Venus
   - 5. จุดเด่น จุดด้อย: บังคับแปล Sun, Moon, Saturn + **ASC/MC Rulers**
   - 6. ศักยภาพและการพัฒนา: บังคับแปล North Node, Jupiter + **House 9/10 Ruler**
   - 7. ปัญหาที่ต้องปรับปรุง: บังคับแปล Chiron, Saturn + **House 6/8/12 Ruler**

3. โครงสร้างการตอบ ต้องตอบครบ 7 หมวดหมู่ (ใช้ Markdown ##):
## 1. นิสัย บุคลิกภาพ
## 2. การเงิน
## 3. การงาน อาชีพ ที่ตรงกับดวง
## 4. ความรัก
## 5. จุดเด่น จุดด้อย และการแก้จุดด้อย
## 6. ศักยภาพที่มี และวิธีการพัฒนา
## 7. ปัญหาที่ต้องปรับปรุง เพื่อความก้าวหน้า

4. บรรทัดสุดท้ายของทุกหมวดหมู่ บังคับปิดท้ายด้วยคำว่า '**ที่มา:**' เท่านั้น (ห้ามใช้คำอื่น) โดยต้องแสดงรายการ ดาว, ราศี, เรือนชะตา และ **House Ruler** ที่นำมาคำนวณในหมวดนั้นจริง
   (ตัวอย่างรูปแบบ: **ที่มา:** ASC Leo, Moon Leo House 1, ASC Ruler (Sun) in Gemini 3°40' House 10)
"""
    content = f"ผู้ถาม: {user_name}\n\n{chart_text}"

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": prompt}, {"role": "user", "content": content}],
        temperature=0.15
    )
    return res.choices[0].message.content


def analyze_transit_qa(user_name, question, chart_data):
    chart_text = format_chart_context(chart_data)

    prompt = f"""
คุณคือนักโหราศาสตร์สากลเชิงพัฒนาศักยภาพ (Evolutionary Astrologer)
โทนเสียง: ผู้เชี่ยวชาญ มีหลักการ ตรงประเด็น วิเคราะห์เจาะลึก มุ่งเน้นการแก้ปัญหาและพัฒนาศักยภาพ

หน้าที่พยากรณ์:
1. นำดาวจร Real-time [Transit Degrees] มาทำมุมสัมพันธ์ (Aspect) กับดาวกำเนิด [Birth Chart Degrees] และวิเคราะห์กระทบไปถึง House และ **House Ruler ที่ได้รับผลกระทบ**
2. ตอบคำถามผู้ใช้เรื่อง Timing ช่วงเวลาสุกงอม สภาวะอารมณ์ และกลยุทธ์ทางออกอย่างเป็นรูปธรรม ความยาวอย่างน้อย 3 ย่อหน้า
3. ในบทบรรยาย ต้องระบุชื่อดาวจร, ดาวกำเนิด, ราศี, เรือนชะตา, มุมสัมพันธ์ และ **House Ruler**
4. บรรทัดสุดท้ายบังคับปิดท้ายด้วยคำว่า '**ที่มา:**' เท่านั้น โดยสรุปดาวจร ดาวกำเนิด เรือน และ House Ruler ที่ทำมุมสัมพันธ์กันจริง
"""
    content = f"ผู้ถาม: {user_name}\nคำถาม: {question}\n\n{chart_text}"

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": prompt}, {"role": "user", "content": content}],
        temperature=0.15
    )
    return res.choices[0].message.content


def analyze_deep_report_json(user_name, chart_data, school_rules):
    chart_text = format_chart_context(chart_data)

    prompt = f"""
คุณคือนักโหราศาสตร์สากลเชิงพัฒนาศักยภาพ (Evolutionary Astrologer)
วิเคราะห์ปมชีวิตและโครงสร้างจิตใต้สำนึก 12 เรือนชะตาอย่างละเอียด โดยระบุ ดาว, ราศี, เรือนชะตา, มุมสัมพันธ์ และ House Ruler ประกอบการวิเคราะห์ทุกมิติ
"""
    content = f"ผู้ถาม: {user_name}\n\n{chart_text}"

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": prompt}, {"role": "user", "content": content}],
        temperature=0.15
    )
    return res.choices[0].message.content
