import json
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_natal_7_categories(user_name, chart_data, school_rules):
    prompt = f"""
คุณคือนักโหราศาสตร์สากลเชิงพัฒนาศักยภาพ (Evolutionary Astrologer)
โทนเสียง: ผู้เชี่ยวชาญ มีหลักการ ตรงประเด็น ไม่พูดเยอะ เน้นวิเคราะห์เชิงจิตวิทยาพฤติกรรมมนุษย์

🎯 บังคับโครงสร้างการวิเคราะห์ 7 หมวดหมู่ (ใช้ Markdown ##):
## 1. นิสัย บุคลิกภาพ
## 2. การเงิน
## 3. การงาน อาชีพ ที่ตรงกับดวง
## 4. ความรัก
## 5. จุดเด่น จุดด้อย และการแก้จุดด้อย
## 6. ศักยภาพที่มี และวิธีการพัฒนา
## 7. ปัญหาที่ต้องปรับปรุง เพื่อความก้าวหน้า

กฎการแปลความหมาย:
1. วิเคราะห์ความหมายโดยแทรก ดาว, ราศี (Sign), เรือนชะตา (House), มุมสัมพันธ์ (Aspect) และ **เจ้าเรือน (House Ruler)** สอดแทรกในบทบรรยาย
2. บังคับใช้ Ruler ประจำเรือน:
   - นิสัย: ASC + House 1 + ASC Ruler
   - การเงิน: House 2 + House 2 Ruler + Venus
   - การงาน: MC + House 10 Ruler + House 6 Ruler
   - ความรัก: DSC + House 7 Ruler + Venus
   - จุดเด่น/ด้อย: Sun, Moon, Saturn + ASC/MC Rulers
   - ศักยภาพ: North Node, Jupiter + House 9/10 Ruler
   - ปรับปรุง: Chiron, Saturn + House 6/8/12 Ruler
3. บรรทัดสุดท้ายของทุกหมวด บังคับใส่ '**หลักฐานที่ใช้วิเคราะห์:**' สรุปดาว ราศี เรือน และ House Ruler
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
1. นำดาวจร Real-time [transit_degrees] ทำมุมสัมพันธ์ (Aspect) กับดาวกำเนิด [birth_chart_degrees] และวิเคราะห์ผลกระทบต่อ House และ House Ruler ที่เกี่ยวข้อง
2. ตอบคำถามผู้ใช้ (เช่น เรื่องการงาน การแก้ปัญหา) โดยระบุ Timing ช่วงเวลา สภาวะอารมณ์ และกลยุทธ์ทางออกเชิงพฤติกรรม
3. บรรทัดสุดท้ายใส่ '**หลักฐานที่ใช้วิเคราะห์:**' สรุปดาวจร ดาวกำเนิด เรือน และ House Ruler ที่ได้รับผลกระทบ
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
วิเคราะห์ปมชีวิตและโครงสร้างจิตใต้สำนึก 12 เรือนชะตา โดยนำ House Rulers มาประมวลผลอย่างเป็นระบบ
"""
    content = f"ผู้ถาม: {user_name}\n[Chart Data]: {json.dumps(chart_data, ensure_ascii=False)}"

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": prompt}, {"role": "user", "content": content}],
        temperature=0.1
    )
    return res.choices[0].message.content
