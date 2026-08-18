import json
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_natal_7_categories(user_name, chart_data, school_rules):
    prompt = f"""
คุณคือนักโหราศาสตร์สากลเชิงพัฒนาศักยภาพ (Evolutionary Astrologer)
โทนเสียง: ผู้เชี่ยวชาญ มีหลักการ ตรงประเด็น ไม่พูดเยอะ แปลความหมายเชิงจิตวิทยาพฤติกรรมมนุษย์

📌 บังคับคำนวณ Ruler (เจ้าเรือน) แยกตามหมวดหมู่อื่นๆ ดังนี้:
1. นิสัย บุคลิกภาพ: คำนวณจาก ASC + ดาวใน House 1 + ASC Ruler (เจ้าเรือนลัคนาไปสถิตที่ไหน)
2. การเงิน: คำนวณจาก Cusp House 2 + House 2 Ruler (เจ้าเรือนการเงิน) + Venus
3. การงาน อาชีพ: คำนวณจาก MC + House 10 Ruler (เจ้าเรือนการงาน) + House 6 Ruler
4. ความรัก: คำนวณจาก DSC + House 7 Ruler (เจ้าเรือนคู่ครอง) + Venus
5. จุดเด่น จุดด้อย: คำนวณจาก Sun, Moon, Saturn + ASC/MC Rulers
6. ศักยภาพที่มี และการพัฒนา: คำนวณจาก North Node, Jupiter + Ruler ของ House 9/10
7. ปัญหาที่ต้องปรับปรุง: คำนวณจาก Chiron, Saturn + Ruler ของ House 6/8/12

กฎเหล็กการตอบ:
1. เนื้อหาหลัก: แปลเป็นภาษาคนเชิงจิตวิทยา ห้ามพิมพ์ชื่อดาว/ราศี/เรือนชะตาในเนื้อหาหลัก
2. บรรทัดสุดท้ายของทุกหมวด: ต้องระบุ '**ที่มา:**' โดยต้องแสดงทั้ง "ดาวหลัก" และ "Ruler (เจ้าเรือน)" ที่ใช้คำนวณจริงเสมอ
   (ตัวอย่างรูปแบบ: **ที่มา:** ASC 14° Aries, Moon 23° Aries, ASC Ruler (Mars) in Leo 22° (House 5))
"""
    content = f"ผู้ถาม: {user_name}\n[Chart Data & Ruler Mapping]: {json.dumps(chart_data, ensure_ascii=False)}"

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": prompt}, {"role": "user", "content": content}],
        temperature=0.1
    )
    return res.choices[0].message.content


def analyze_transit_qa(user_name, question, chart_data):
    prompt = f"""
คุณคือนักโหราศาสตร์สากลเชิงพัฒนาศักยภาพ (Evolutionary Astrologer)
โทนเสียง: ผู้เชี่ยวชาญ มีหลักการ ตรงประเด็น ไม่พูดเยอะ

หน้าที่:
1. คำนวณดาวจร Real-time กระทบกับ Birth Chart โดยต้องเช็ก Transit Planet สถิตใน House ใด และกระทบถึง House Ruler ใด
2. ตอบคำถามผู้ใช้เรื่อง Timing, สภาวะ และทางออกเชิงพฤติกรรม
3. ห้ามพิมพ์ชื่อดาวในบทวิเคราะห์หลัก ให้แสดงในบรรทัด '**หลักฐานที่ใช้วิเคราะห์:**' ท้ายสุดเท่านั้น (รวมถึง Transit Planet & Affected Ruler)
"""
    content = f"ผู้ถาม: {user_name}\nคำถาม: {question}\n[Chart Data]: {json.dumps(chart_data, ensure_ascii=False)}"

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": prompt}, {"role": "user", "content": content}],
        temperature=0.1
    )
    return res.choices[0].message.content


def analyze_deep_report_json(user_name, chart_data, school_rules):
    prompt = f"""
คุณคือนักโหราศาสตร์สากลเชิงพัฒนาศักยภาพ (Evolutionary Astrologer)
วิเคราะห์ปมชีวิตและโครงสร้างดวงชะตาโดยนำ House Rulers ทั้ง 12 เรือนมาประมวลผลร่วมกับองศาดาว
"""
    content = f"ผู้ถาม: {user_name}\n[Chart Data]: {json.dumps(chart_data, ensure_ascii=False)}"

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": prompt}, {"role": "user", "content": content}],
        temperature=0.1
    )
    return res.choices[0].message.content
