import sqlite3

def init_db():
    conn = sqlite3.connect("astro_rules.db")
    cursor = conn.cursor()

    # 1. ตารางเก็บคำพยากรณ์พื้นดวง แยก 7 หมวดหมู่
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS natal_interpretations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,      -- personality, finance, career, love, strength_weakness, potential, growth
        lookup_key TEXT NOT NULL,    -- เช่น ASC_Leo, Sun_Gemini_H10, MC_Gemini
        content TEXT NOT NULL,
        CONSTRAINT unique_cat_key UNIQUE (category, lookup_key)
    );
    """)

    # 2. ตารางเก็บคำพยากรณ์ Transit Q&A
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transit_interpretations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question_type TEXT NOT NULL,  -- career_timing, problem_solving
        aspect_key TEXT NOT NULL,     -- เช่น T_Jupiter_Trine_N_MC, T_Saturn_Square_N_Mercury
        timing_info TEXT,             -- ช่วงเวลาดำเนินการ
        solution_text TEXT NOT NULL,   -- ทางออกเชิงพฤติกรรม
        CONSTRAINT unique_transit_key UNIQUE (question_type, aspect_key)
    );
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_natal_lookup ON natal_interpretations(category, lookup_key);")
    conn.commit()
    conn.close()
    print("[Step 1 Success] สร้างฐานข้อมูล astro_rules.db เรียบร้อย")

if __name__ == "__main__":
    init_db()
