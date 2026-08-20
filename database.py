import sqlite3
import json

DB_NAME = "astro_cache.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 1. ตารางเก็บผลคำนวณดวงชะตา (Birth Chart Cache)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS natal_charts (
            user_id TEXT PRIMARY KEY,
            birth_data JSON,
            chart_degrees JSON,
            ruler_mapping JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 2. ตารางเก็บ Evidence Matrix ที่สกัดแล้ว (Evidence Cache)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS evidence_store (
            user_id TEXT,
            category TEXT,
            evidence_json JSON,
            PRIMARY KEY (user_id, category)
        )
    ''')

    # 3. ตารางเก็บผลวิเคราะห์ AI สำเร็จรูป (Analysis Cache)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analysis_cache (
            user_id TEXT,
            report_type TEXT,
            content TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, report_type)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_cached_chart(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT chart_degrees, ruler_mapping FROM natal_charts WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"birth_chart_degrees": json.loads(row[0]), "ruler_mapping": json.loads(row[1])}
    return None

def save_chart_cache(user_id, birth_data, chart_degrees, ruler_mapping):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO natal_charts (user_id, birth_data, chart_degrees, ruler_mapping)
        VALUES (?, ?, ?, ?)
    ''', (user_id, json.dumps(birth_data), json.dumps(chart_degrees), json.dumps(ruler_mapping)))
    conn.commit()
    conn.close()
