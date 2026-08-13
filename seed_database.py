import os
import sqlite3
import openai

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

def transform_and_save(category: str, lookup_key: str, raw_text: str):
    if not client:
        raise ValueError("ตั้งค่า OPENAI_API_KEY ใน Environment Variable ก่อนรัน")

    system_prompt = """
คุณคือนักบรรณาธิการโหราศาสตร์สากลเชิงพัฒนาศักยภาพ (Evolutionary Astrology)
หน้าที่: เรียบเรียงเนื้อหาดิบใหม่ทั้งหมด
ข้อกำหนด:
1. ผู้เชี่ยวชาญ มีหลักการ ตรงประเด็น กระชับ ไม่อ้อมค้อม ตัดคำทักทายและคำอารัมภบททิ้งทั้งหมด
2. แปลงคำทายดวงชะตาเชิงลบ ให้เป็น "ทางออกเชิงพฤติกรรมและการพัฒนาตนเอง"
3. ความยาวไม่เกิน 2-3 ประโยค
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"หมวดหมู่: {category}\nเนื้อหาดิบ: {raw_text}"}
        ],
        temperature=0.2
    )
    
    transformed_text = response.choices[0].message.content.strip()

    conn = sqlite3.connect("astro_rules.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO natal_interpretations (category, lookup_key, content)
        VALUES (?, ?, ?)
    """, (category, lookup_key, transformed_text))
    conn.commit()
    conn.close()
    print(f"[Imported] Category: {category} | Key: {lookup_key}")

# ตัวอย่างการสั่งอิมพอร์ต Batch Data
if __name__ == "__main__":
    sample_data = [
        {"category": "personality", "key": "ASC_Leo", "text": "ลัคนารศีสิงห์ วางตัวโดดเด่น มีออร่า มั่นใจ ชอบเป็นผู้นำ แต่ต้องระวังเรื่องการยึดตนเองเป็นศูนย์กลาง"},
        {"category": "career", "key": "Sun_Gemini_H10", "text": "อาทิตย์เมถุนเรือน 10 ทำงานเกี่ยวกับการสื่อสาร มัลติมีเดีย ความท้าทายคือการสร้างผลงานระยะยาวโดยไม่เปลี่ยนเป้าหมายบ่อย"},
        {"category": "finance", "key": "H2_Taurus", "text": "เรือนที่ 2 ราศีพฤษภ โครงสร้างการสร้างรายได้เน้นความมั่นคง สินทรัพย์จับต้องได้ และค่านิยมการออมสะสม"}
    ]
    for item in sample_data:
        transform_and_save(item["category"], item["key"], item["text"])
