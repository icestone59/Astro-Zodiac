import os
import sqlite3
import openai

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

def init_db():
    """สร้างโครงสร้างตาราง DB หากยังไม่มี"""
    conn = sqlite3.connect("astro_rules.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS natal_interpretations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        lookup_key TEXT NOT NULL,
        content TEXT NOT NULL,
        CONSTRAINT unique_cat_key UNIQUE (category, lookup_key)
    );
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_natal_lookup ON natal_interpretations(category, lookup_key);")
    conn.commit()
    conn.close()

def generate_and_save_rule(category: str, lookup_key: str):
    """สร้างบทพยากรณ์ด้วย AI และบันทึกลง astro_rules.db"""
    if not client:
        print("[Error] ไม่พบ OPENAI_API_KEY ใน Environment")
        return

    system_prompt = """
คุณคือนักโหราศาสตร์สากลเชิงพัฒนาศักยภาพ (Evolutionary & Psychological Astrologer)
หน้าที่: เขียนบทวิเคราะห์จาก Lookup Key ของตำแหน่งดาว/เรือนชะตา

ข้อกำหนดการเขียน:
1. โทนเสียง: ผู้เชี่ยวชาญ มีหลักการ ตรงประเด็น กระชับ ไม่พูดเยอะ ไม่อ้อมค้อม
2. ห้ามใช้คำอารัมภบท หรือคำทักทายใดๆ ให้ใส่เนื้อหาทันที
3. โฟกัสที่ "กลไกพฤติกรรม" และ "แนวทางการพัฒนาศักยภาพตนเอง"
4. ความยาว: 1-2 ประโยคสั้นๆ ชัดเจน
"""

    user_content = f"หมวดหมู่: {category}\nLookup Key: {lookup_key}"

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            temperature=0.2
        )
        content = response.choices[0].message.content.strip()

        conn = sqlite3.connect("astro_rules.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO natal_interpretations (category, lookup_key, content)
            VALUES (?, ?, ?)
        """, (category, lookup_key, content))
        conn.commit()
        conn.close()
        print(f"[Success] Imported: [{category}] -> {lookup_key}")
    except Exception as e:
        print(f"[Error] {lookup_key}: {e}")

# รายการ Keys จากหน้าเว็บตามดวงตัวอย่างของคุณ
TARGET_KEYS = [
    # 1. Personality
    ("personality", "ASC_Leo"),
    ("personality", "Sun_Gemini_H10"),
    ("personality", "Moon_Leo_H1"),
    
    # 2. Finance
    ("finance", "H2_Virgo"),
    ("finance", "H8_Pisces"),
    ("finance", "Venus_Aries_H9"),
    
    # 3. Career
    ("career", "MC_Taurus"),
    ("career", "Sun_Gemini_H10"),
    ("career", "Saturn_H12"),
    
    # 4. Love
    ("love", "H7_Aquarius"),
    ("love", "H5_Sagittarius"),
    ("love", "Venus_Aries"),
    ("love", "Mars_Aries"),
    
    # 5. Strengths & Weaknesses
    ("strength_weakness", "Chiron_Aries_H9"),
    ("strength_weakness", "general_remedy"),
    
    # 6. Potentials
    ("potential", "NorthNode_Pisces"),
    ("potential", "SouthNode_Virgo"),
    ("potential", "Jupiter_Gemini_H10"),
    
    # 7. Growth
    ("growth", "Saturn_Aries_H12"),
    ("growth", "H12_Cancer")
]

if __name__ == "__main__":
    print("กำลังเตรียมฐานข้อมูล...")
    init_db()
    
    print("กำลังสร้างบทวิเคราะห์เข้าฐานข้อมูล astro_rules.db...")
    for cat, key in TARGET_KEYS:
        generate_and_save_rule(cat, key)
        
    print("\n[เสร็จสิ้น] ฐานข้อมูลพร้อมใช้งานแล้ว")
