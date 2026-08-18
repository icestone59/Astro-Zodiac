import json
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_natal_7_categories(user_name, chart_data, school_rules):
    prompt = f"""
คุณคือนักโหราศาสตร์สากลเชิงพัฒนาศักยภาพ (Evolutionary Astrologer)
โทนเสียง: ผู้เชี่ยวชาญ มีหลักการ ตรงประเด็น ไม่พูดเยอะ วิเคราะห์เจาะลึกเชิงจิตวิทยาพฤติกรรมมนุษย์

📌 กฎเหล็กการใช้ Ruler (เจ้าเรือน) แยกตามหมวดหมู่ (ต้องนำมาแปลในเนื้อหา และระบุในหลักฐานเสมอ):
1. นิสัย บุคลิกภาพ: บังคับใช้ ASC + ดาวใน House 1 + **ASC Ruler (เจ้าเรือนลัคนาสถิตที่ไหน)**
2. การเงิน: บังคับใช้ House 2 + **House 2 Ruler (เจ้าเรือนการเงินสถิตที่ไหน)** + Venus
3. การงาน อาชีพ: บังคับใช้ MC (House 10) + **House 10 Ruler (เจ้าเรือนการงานสถิตที่ไหน)** + House 6 Ruler
4. ความรัก: บังคับใช้ DSC (House 7) + **House 7 Ruler (เจ้าเรือนคู่ครองสถิตที่ไหน)** + Venus
5. จุดเด่น จุดด้อย: บังคับใช้ Sun, Moon, Saturn + **ASC/MC Rulers**
6. ศักยภาพที่มี และการพัฒนา: บังคับใช้ North Node, Jupiter + **House 9/10 Ruler**
7. ปัญหาที่ต้องปรับปรุง: บังคับใช้ Chiron, Saturn + **House 6/8/12 Ruler**

โครงสร้างการตอบ 7 หมวดหมู่ (ใช้ Markdown ##):
## 1. นิสัย บุคลิกภาพ
## 2. การเงิน
## 3. การงาน อาชีพ ที่ตรงกับดวง
## 4. ความรัก
## 5. จุดเด่น จุดด้อย และการแก้จุดด้อย
## 6. ศักยภาพที่มี และวิธีการพัฒนา
## 7. ปัญหาที่ต้องปรับปรุง เพื่อความก้าวหน้า

รูปแบบการบรรยายในทุกหมวดหมู่:
1. เขียนบรรยายอย่างละเอียด 3 ย่อหน้า โดยในเนื้อหาต้องระบุ ดาว, ราศี (Sign), เรือนชะตา (House), มุมสัมพันธ์ (Aspect) และ **Ruler (เจ้าเรือน)** สอดแทรกอย่างชัดเจน
   (ตัวอย่าง: "คุณ{user_name} มี ASC ใน Scorpio และมี ASC Ruler คือ Pluto สถิตใน Capricorn เรือนที่ 3 ร่วมกับ Moon ใน Leo เรือนที่ 10 ส่งผลให้...")
2. บรรทัดสุดท้ายของทุกหมวด บังคับใส่ '**หลักฐานที่ใช้วิเคราะห์:**' โดยต้องมี **Ruler** อยู่ในรายการด้วยเสมอ
   (ตัวอย่าง: **หลักฐานที่ใช้วิเคราะห์:** ASC Scorpio House 1, ASC Ruler (Pluto Capricorn House 3), Moon Leo House 10, Sun Gemini House 7)
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

หน้าที่พยากรณ์:
1. นำ [Transit Degrees] ทำมุมสัมพันธ์ (Aspect) กับ [Birth Chart Degrees] โดยต้องวิเคราะห์ถึง House และ **Affected House Ruler (เจ้าเรือนที่ได้รับผลกระทบ)**
2. ในเนื้อหาบรรยาย 3 ย่อหน้า ต้องระบุชื่อดาวจร, ดาวกำเนิด, ราศี, เรือนชะตา, มุมสัมพันธ์ และ **Ruler** เพื่อบอก Timing และทางออกเชิงกลยุทธ์
3. บรรทัดสุดท้ายบังคับใส่ '**หลักฐานที่ใช้วิเคราะห์:**' ระบุทั้ง Transit Planet, Natal Planet, House และ **House Ruler** ที่เกี่ยวข้องทั้งหมด
"""
    content = f"ผู้ถาม: {user_name}\nคำถาม: {question}\n[Chart Data]: {json.dumps(chart_data, ensure_ascii=False)}"

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": prompt}, {"role": "user", "content": content}],
        temperature=0.1
    )
    return res.choices[0].message.content
