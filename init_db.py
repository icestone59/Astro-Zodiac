import sqlite3

def init_database():
    conn = sqlite3.connect("astro_rules.db")
    cursor = conn.cursor()

    # 1. ตารางเก็บคำพยากรณ์พื้นดวง 7 หัวข้อ
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS natal_rules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,       -- personality, finance, career, love, strengths_weaknesses, potentials, growth
        lookup_key TEXT UNIQUE NOT NULL, -- เช่น Sun_Gemini_H10, ASC_Leo, Moon_Leo_H1
        content TEXT NOT NULL
    )
    """)

    # 2. ตารางเก็บคำพยากรณ์ Transit & Q&A
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transit_rules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question_type TEXT NOT NULL,  -- career_timing, problem_solving
        aspect_key TEXT UNIQUE NOT NULL, -- เช่น Jupiter_Trine_MC, Saturn_Square_Mercury
        timing_info TEXT,             -- ช่วงเวลาที่ควรดำเนินการ
        solution_text TEXT NOT NULL   -- ทางออกเชิงพฤติกรรม
    )
    """)

    conn.commit()
    conn.close()
    print("[Success] สร้างฐานข้อมูล astro_rules.db เรียบร้อยแล้ว")

if __name__ == "__main__":
    init_database()
