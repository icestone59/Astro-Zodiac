import sqlite3
import os
import openai

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

def rewrite_to_evolutionary_tone(raw_text: str, category: str) -> str:
    """ส่งข้อความดิบไปให้ AI เรียบเรียงใหม่ตามโทนเสียงผู้เชี่ยวชาญ"""
    if not client:
        raise ValueError("กรุณาตั้งค่า OPENAI_API_KEY ใน Environment Variable")

    system_prompt = """
คุณคือนักบรรณาธิการโหราศาสตร์สากลเชิงพัฒนาศักยภาพ (Evolutionary Astrology)
หน้าที่: เรียบเรียงข้อความโหราศาสตร์ดิบใหม่ทั้งหมด

ข้อกำหนดโทนเสียงรัดกุม:
1. ผู้เชี่ยวชาญ มีหลักการ ตรงประเด็น กระชับ ไม่พูดเยอะ
2. ห้ามมีคำทักทาย อารัมภบท หรือคำอวยพรเด็ดขาด
3. แปลงคำพยากรณ์ดวงชะตาเชิงลบ ให้กลายเป็น "ทางออกเชิงพฤติกรรมและการพัฒนาตนเอง"
4. ความยาวไม่เกิน 2-3 ประโยค
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"หมวดหมู่: {category}\nข้อความดิบ: {raw_text}"}
        ],
        temperature=0.2
    )
    return response.choices[0].message.content.strip()

def insert_natal_rule(category: str, lookup_key: str, raw_text: str):
    """แปลงภาษาและบันทึกลง natal_rules"""
    transformed_text = rewrite_to_evolutionary_tone(raw_text, category)
    
    conn = sqlite3.connect("astro_rules.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO natal_rules (category, lookup_key, content) VALUES (?, ?, ?)",
        (category, lookup_key, transformed_text)
    )
    conn.commit()
    conn.close()
    print(f"[Imported] {lookup_key} -> Saved to DB")

# --- ตัวอย่างการสั่งรันสร้างคลังข้อมูล (Batch Execution) ---
if __name__ == "__main__":
    # ตัวอย่างข้อมูลดิบที่ดึงมาจากเว็บ
    sample_raw_data = [
        {
            "category": "personality",
            "lookup_key": "ASC_Leo",
            "raw_text": "คนเกิดลัคนาราศีสิงห์มักจะเป็นคนชอบโดดเด่น มีออร่า มั่นใจในตัวเองสูง ชอบเป็นผู้นำ แต่บางทีก็เอาแต่ใจและอยากให้คนอื่นสนใจตลอดเวลา"
        },
        {
            "category": "career",
            "lookup_key": "Sun_Gemini_H10",
            "raw_text": "อาทิตย์อยู่อยู่เมถุนในเรือนที่ 10 จะได้ทำงานเกี่ยวกับการใช้ปาก การพูด สื่อสาร หรือเขียนหนังสือ มีความคล่องตัวสูง เปลี่ยนงานบ่อย"
        }
    ]

    for item in sample_raw_data:
        insert_natal_rule(item["category"], item["lookup_key"], item["raw_text"])
