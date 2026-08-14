import os
import sqlite3
import openai

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

def init_db():
    """สร้างโครงสร้างฐานข้อมูลรองรับทั้ง 7 หมวดหมู่พื้นดวง และ Transit Q&A"""
    conn = sqlite3.connect("astro_rules.db")
    cursor = conn.cursor()

    # 1. ตารางคำพยากรณ์พื้นดวง 7 หมวดหมู่
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS natal_interpretations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        lookup_key TEXT NOT NULL,
        content TEXT NOT NULL,
        CONSTRAINT unique_cat_key UNIQUE (category, lookup_key)
    );
    """)

    # 2. ตารางคำพยากรณ์ Transit Q&A
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transit_interpretations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question_type TEXT NOT NULL,
        aspect_key TEXT NOT NULL,
        timing_info TEXT,
        solution_text TEXT NOT NULL,
        CONSTRAINT unique_transit_key UNIQUE (question_type, aspect_key)
    );
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_natal_lookup ON natal_interpretations(category, lookup_key);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_transit_lookup ON transit_interpretations(question_type, aspect_key);")
    
    conn.commit()
    conn.close()

def generate_and_save_rule(category: str, lookup_key: str):
    """สร้างบทวิเคราะห์พื้นดวงด้วย AI และบันทึกลง natal_interpretations"""
    if not client:
        print(f"[Warning] ไม่พบ OPENAI_API_KEY ข้ามการสร้าง Key: {lookup_key}")
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

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"หมวดหมู่: {category}\nLookup Key: {lookup_key}"}
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
        print(f"[Success] Imported Natal: [{category}] -> {lookup_key}")
    except Exception as e:
        print(f"[Error] {lookup_key}: {e}")

def seed_transit_rules():
    """เพิ่มข้อมูลตัวอย่างสำหรับ Transit Q&A เข้าตาราง transit_interpretations"""
    conn = sqlite3.connect("astro_rules.db")
    cursor = conn.cursor()

    sample_transits = [
        ("career_timing", "T_Jupiter_Trine_N_MC", "1-3 เดือนนี้", "ดาว Jupiter ทำมุม Trine ถึง MC เป็นจังหวะเปิด ให้เตรียม Portfolio และยื่นสมัครงานล่วงหน้าทันที"),
        ("problem_solving", "T_Saturn_Square_N_Mercury", "ช่วงนี้ถึงเดือนหน้า", "แรงกดดันเรื่องการสื่อสารและสัญญา แก้ไขด้วยการทำข้อตกลงเป็นลายลักษณ์อักษรและตัดการใช้อารมณ์ตัดสิน")
    ]

    for q_type, key, timing, solution in sample_transits:
        cursor.execute("""
            INSERT OR REPLACE INTO transit_interpretations (question_type, aspect_key, timing_info, solution_text)
            VALUES (?, ?, ?, ?)
        """, (q_type, key, timing, solution))
        print(f"[Success] Imported Transit: [{q_type}] -> {key}")

    conn.commit()
    conn.close()

# รายการ Keys สำหรับสร้างพื้นดวง
TARGET_KEYS = [
    ("personality", "ASC_Leo"),
    ("personality", "Sun_Gemini_H10"),
    ("personality", "Moon_Leo_H1"),
    ("finance", "H2_Virgo"),
    ("finance", "H8_Pisces"),
    ("finance", "Venus_Aries_H9"),
    ("career", "MC_Taurus"),
    ("career", "Sun_Gemini_H10"),
    ("career", "Saturn_H12"),
    ("love", "H7_Aquarius"),
    ("love", "H5_Sagittarius"),
    ("love", "Venus_Aries"),
    ("love", "Mars_Aries"),
    ("strength_weakness", "Chiron_Aries_H9"),
    ("strength_weakness", "general_remedy"),
    ("potential", "NorthNode_Pisces"),
    ("potential", "SouthNode_Virgo"),
    ("potential", "Jupiter_Gemini_H10"),
    ("growth", "Saturn_Aries_H12"),
    ("growth", "H12_Cancer")
]

if __name__ == "__main__":
    print("กำลังเตรียมโครงสร้างตารางฐานข้อมูล...")
    init_db()

    print("กำลังบันทึกข้อมูล Transit Rules...")
    seed_transit_rules()

    print("กำลังสร้างและบันทึกข้อมูล Natal Rules...")
    for cat, key in TARGET_KEYS:
        generate_and_save_rule(cat, key)

    print("\n[เสร็จสิ้น] ฐานข้อมูล astro_rules.db พร้อมใช้งานสมบูรณ์")
