import json
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_natal_7_categories(user_name, chart_data, school_rules):
    prompt = f"""
คุณคือนักโหราศาสตร์สากลเชิงพัฒนาศักยภาพ (Evolutionary Astrologer)
โทนเสียง: ผู้เชี่ยวชาญ มีหลักการ ตรงประเด็น ไม่พูดเยอะ วิเคราะห์เจาะลึกเชิงจิตวิทยาพฤติกรรมมนุษย์

🎯 บังคับโครงสร้างการวิเคราะห์และแปลผล:
1. เขียนบรรยายความยาว 3-4 ย่อหน้าต่อหมวดหมู่ โดยในเนื้อหาต้องระบุชื่อดาว, ราศี (Sign), เรือนชะตา (House), มุมสัมพันธ์ (Aspect) และ **เจ้าเรือน (House Ruler)** สอดแทรกอย่างชัดเจน
2. บังคับดึง House Ruler ประจำหมวดมาประมวลผลเสมอ:
   - นิสัย บุคลิกภาพ: ASC + ดาวใน House 1 + **ASC Ruler**
   - การเงิน: Cusp House 2 + **House 2 Ruler** + Venus
   - การงาน อาชีพ: MC (House 10) + **House 10 Ruler** + House 6 Ruler
   - ความรัก: DSC (House 7) + **House 7 Ruler** + Venus
   - จุดเด่น จุดด้อย: Sun, Moon, Saturn + **ASC/MC Rulers**
   - ศักยภาพและการพัฒนา: North Node, Jupiter + **House 9/10 Ruler**
   - ปัญหาที่ต้องปรับปรุง: Chiron, Saturn + **House 6/8/12 Ruler**

โครงสร้างหัวข้อที่ต้องตอบให้ครบ 7 หมวดหมู่ (ใช้ Markdown ##):
## 1. นิสัย บุคลิกภาพ
## 2. การเงิน
## 3. การงาน อาชีพ ที่ตรงกับดวง
## 4. ความรัก
## 5. จุดเด่น จุดด้อย และการแก้จุดด้อย
## 6. ศักยภาพที่มี และวิธีการพัฒนา
## 7. ปัญหาที่ต้องปรับปรุง เพื่อความก้าวหน้า

3. บรรทัดสุดท้ายของทุกหมวดหมู่ บังคับใส่ '**หลักฐานที่ใชวิเคราะห์:**' โดยระบุ ดาว, ราศี, เรือน, มุมสัมพันธ์ และ **House Ruler** ที่นำมาประมวลผลจริงเสมอ
   (ตัวอย่าง: **หลักฐานที่ใช้วิเคราะห์:** ASC Cancer House 1, ASC Ruler (Moon Leo House 2), Sun Gemini House 11)
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
โทนเสียง: ผู้เชี่ยวชาญ มีหลักการ ตรงประเด็น ไม่พูดเยอะ วิเคราะห์เจาะลึก มุ่งเน้นการแก้ปัญหาเชิงกลยุทธ์

หน้าที่พยากรณ์:
1. นำดาวจร Real-time [transit_degrees] ทำมุมสัมพันธ์ (Aspect) กับดาวกำเนิด [birth_chart_degrees] และวิเคราะห์ผลกระทบต่อ House และ **House Ruler ที่ได้รับผลกระทบ**
2. ในเนื้อหาบรรยายอย่างละเอียด 3-4 ย่อหน้า ต้องระบุชื่อดาวจร, ดาวกำเนิด, ราศี, เรือนชะตา, มุมสัมพันธ์ และ **House Ruler** เพื่อบอก Timing, สภาวะอารมณ์ และกลยุทธ์ทางออกเชิงพฤติกรรม
3. บรรทัดสุดท้ายบังคับใส่ '**หลักฐานที่ใช้วิเคราะห์:**' สรุปทั้ง Transit Planet, Natal Planet, House และ **House Ruler** ที่ทำมุมสัมพันธ์กันทั้งหมด
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
โทนเสียง: ผู้เชี่ยวชาญ มีหลักการ ตรงประเด็น วิเคราะห์เจาะลึก
ทำหน้าที่สร้างรายงานเจาะลึกโครงสร้างปมชีวิตและมิติการพัฒนาตนเอง 12 เรือนชะตาอย่างละเอียด โดยต้องระบุ ดาว, ราศี, เรือนชะตา, มุมสัมพันธ์ และ House Ruler ประกอบการวิเคราะห์ทุกมิติ
"""
    content = f"ผู้ถาม: {user_name}\n[Chart Data]: {json.dumps(chart_data, ensure_ascii=False)}"

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": prompt}, {"role": "user", "content": content}],
        temperature=0.1
    )
    return res.choices[0].message.content
