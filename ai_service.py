import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def format_chart_context(chart_data):
    birth = chart_data.get("birth_chart_degrees", {})
    rulers = chart_data.get("ruler_mapping", {})
    transits = chart_data.get("transit_degrees", {})

    text = "=== ตำแหน่งดาวกำเนิด (BIRTH CHART DEGREES) ===\n"
    for planet, info in birth.items():
        text += f"- {planet}: {info.get('sign')} {info.get('formatted')} (House {info.get('house')})\n"

    text += "\n=== ตำแหน่งเจ้าเรือน (HOUSE RULER MAPPING) ===\n"
    for house, info in rulers.items():
        text += f"- {house} ({info.get('sign')}): ดาวเจ้าเรือน {info.get('ruler_planet')} -> สถิตที่ {info.get('ruler_pos')}\n"

    if transits:
        text += "\n=== ตำแหน่งดาวจร REAL-TIME (TRANSIT DEGREES) ===\n"
        for planet, info in transits.items():
            text += f"- Transit {planet}: {info.get('sign')} {info.get('formatted')} (สถิตใน Natal House {info.get('house_in_natal')})\n"

    return text

def analyze_natal_7_categories(user_name, chart_data, school_rules):
    chart_text = format_chart_context(chart_data)

    prompt = f"""
คุณคือนักโหราศาสตร์สากลเชิงพัฒนาศักยภาพ (Evolutionary Astrologer)
โทนเสียง: ผู้เชี่ยวชาญ มีหลักการ ตรงประเด็น ไม่พูดเยอะ วิเคราะห์เจาะลึกโครงสร้างจิตวิทยาพฤติกรรมมนุษย์

📌 โครงสร้างการตอบคำถาม (ต้องตอบครบ 7 หมวดหมู่):
## 1. นิสัย บุคลิกภาพ
## 2. การเงิน
## 3. การงาน อาชีพ ที่ตรงกับดวง
## 4. ความรัก
## 5. จุดเด่น จุดด้อย และการแก้จุดด้อย
## 6. ศักยภาพที่มี และวิธีการพัฒนา
## 7. ปัญหาที่ต้องปรับปรุง เพื่อความก้าวหน้า

กฎการวิเคราะห์:
1. แต่ละหมวดหมู่ต้องบรรยายสอดแทรกตำแหน่ง ดาว, ราศี, เรือนชะตา และ **ดาวเจ้าเรือน (House Ruler)** ลงในมิติการพัฒนาศักยภาพ
2. บรรทัดสุดท้ายของทุกหมวดหมู่ บังคับปิดท้ายด้วยข้อความ '**ที่มา:**' เท่านั้น โดยระบุปัจจัยที่ดึงมาคำนวณจริง
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
โทนเสียง: ผู้เชี่ยวชาญ มีหลักการ ตรงประเด็น ไม่พูดเยอะ มุ่งเน้นทางออกและกลยุทธ์ก้าวหน้า

หน้าที่พยากรณ์ Transit Q&A:
1. นำดาวจร Real-time [Transit Degrees] ทำมุมสัมพันธ์กับดาวกำเนิด [Birth Chart Degrees] และ House Ruler
2. วิเคราะห์ตอบคำถามเรื่อง Timing ช่วงเวลาสุกงอม สภาวะ และกลยุทธ์ทางออกอย่างเป็นรูปธรรม
3. บรรทัดสุดท้ายบังคับปิดท้ายด้วยข้อความ '**ที่มา:**' เท่านั้น สรุปดาวจร ดาวกำเนิด เรือนชะตา และ House Ruler ที่เกี่ยวข้อง
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
วิเคราะห์ปมชีวิต ปมจิตใต้สำนึก และการก้าวข้ามข้อจำกัดรายเรือนชะตา 12 เรือน (House 1 - House 12) อย่างเจาะลึก
ทุกลำดับเรือนต้องระบุตำแหน่ง ดาว, ราศี, เรือนชะตา และ House Ruler ประกอบ และปิดท้ายแต่ละเรือนด้วย '**ที่มา:**'
"""
    content = f"ผู้ถาม: {user_name}\n\n{chart_text}"

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": prompt}, {"role": "user", "content": content}],
        temperature=0.15
    )
    return res.choices[0].message.content
