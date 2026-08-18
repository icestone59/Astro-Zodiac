import json
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_natal_7_categories(user_name, chart_data, school_rules):
    """สังเคราะห์บทแปลโหราศาสตร์สากล 7 หมวดหมู่ ตรงตาม Master Rules"""
    natal_lib = school_rules.get("natal_categories", {})
    
    prompt = f"""
คุณคือนักโหราศาสตร์สากลเชิงพัฒนาศักยภาพ (Evolutionary Astrologer)
โทนเสียง: ผู้เชี่ยวชาญ มีหลักการ ตรงประเด็น ไม่พูดเยอะ เล่าเรื่องเชิงจิตวิทยาพฤติกรรมมนุษย์

โครงสร้างหัวข้อที่ต้องตอบให้ครบ 7 หมวดหมู่ (ใช้ Markdown ## และ ###):
## 1. นิสัย บุคลิกภาพ
## 2. การเงิน
## 3. การงาน อาชีพ ที่ตรงกับดวง
## 4. ความรัก
## 5. จุดเด่น จุดด้อย และการแก้จุดด้อย
## 6. ศักยภาพที่มี และวิธีการพัฒนา
## 7. ปัญหาที่ต้องปรับปรุง เพื่อความก้าวหน้า

กฎเหล็กบทบรรยายหลัก:
1. ห้ามพิมพ์ชื่อดาว, ราศี, เรือนชะตา (เช่น Sun, Moon, ASC, House 1) ลงในเนื้อหาบทพฤติกรรมมนุษย์เด็ดขาด
2. แปลความหมายเป็นภาษาคนเชิงจิตวิทยา 2-3 ย่อหน้าต่อหมวด
3. ท้ายทุกหมวด ให้ระบุบรรทัด '**หลักฐานที่ใช้วิเคราะห์:**' แสดงตำแหน่งองศาดาวจริง และ Ruler จากข้อมูลที่ให้มาเท่านั้น
"""
    content = f"ผู้ถาม: {user_name}\n[Chart Data & Ruler Mapping]: {json.dumps(chart_data, ensure_ascii=False)}"

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": prompt}, {"role": "user", "content": content}],
        temperature=0.1
    )
    return res.choices[0].message.content

def analyze_transit_qa(user_name, question, chart_data):
    """วิเคราะห์คำถามเจาะจงด้วย Transit Real-time vs Birth Chart"""
    prompt = f"""
คุณคือนักโหราศาสตร์สากลเชิงพัฒนาศักยภาพ (Evolutionary Astrologer)
โทนเสียง: ผู้เชี่ยวชาญ มีหลักการ ตรงประเด็น ไม่พูดเยอะ

หน้าที่:
1. นำข้อมูล [Transit Degrees Real-time] มาจับมุมสัมพันธ์กับ [Birth Chart Degrees]
2. ตอบคำถามผู้ใช้โดยตรง เช่น Timing สภาวะอารมณ์ และทางออกเชิงกลยุทธ์
3. ห้ามพิมพ์ชื่อดาวในบทวิเคราะห์หลัก ให้นำไปไว้ในบรรทัด '**หลักฐานที่ใช้วิเคราะห์:**' ท้ายสุดเท่านั้น
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
โทนเสียง: ผู้เชี่ยวชาญ มีหลักการ ตรงประเด็น ไม่พูดเยอะ
ทำรายงานเจาะลึก 12 มิติชีวิตภาษาคนเชิงจิตวิทยา ถอดบทเรียนพัฒนาตนเองจากพื้นดวง
"""
    content = f"ผู้ถาม: {user_name}\n[Chart Data]: {json.dumps(chart_data, ensure_ascii=False)}"

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": prompt}, {"role": "user", "content": content}],
        temperature=0.1
    )
    return res.choices[0].message.content
