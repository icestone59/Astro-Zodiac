import sqlite3
import json
import hashlib
from datetime import datetime

DB_NAME = "astro_cache.db"

def init_db():
    """สร้างตารางที่จำเป็นทั้งหมดให้สอดคล้องกับระบบ"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 1. ตารางเก็บผลคำนวณดวงชะตา (Birth Chart Cache)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS natal_charts (
            user_key TEXT PRIMARY KEY,
            birth_chart_degrees TEXT,
            ruler_mapping TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 2. ตารางเก็บผลวิเคราะห์ AI (AI Reports Cache)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ai_reports (
            user_key TEXT,
            report_type TEXT,
            content TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_key, report_type)
        )
    ''')
    
    conn.commit()
    conn.close()

# บังคับรันสร้างตารางทันทีที่ไฟล์นี้ถูกโหลด ป้องกัน Error "no such table"
init_db()

def generate_chart_hash(chart_data):
    """สร้าง Hash แบบไม่ซ้ำจากข้อมูลองศาดาวกำเนิด เพื่อใช้เป็น Cache Key"""
    birth_data = chart_data.get("birth_chart_degrees", {})
    # เรียง key ก่อนแปลงเป็น string เพื่อให้ hash ตรงกันเสมอ
    data_str = json.dumps(birth_data, sort_keys=True)
    return hashlib.md5(data_str.encode()).hexdigest()

def get_cached_ai_report(user_key, report_type):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT content FROM ai_reports WHERE user_key = ? AND report_type = ?", (user_key, report_type))
    row = cursor.fetchone()
    conn.close()
    if row:
        return json.loads(row[0])
    return None

def save_cached_ai_report(user_key, report_type, content_dict):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO ai_reports (user_key, report_type, content, updated_at)
        VALUES (?, ?, ?, ?)
    ''', (user_key, report_type, json.dumps(content_dict), datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_cached_chart(user_key):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT birth_chart_degrees, ruler_mapping FROM natal_charts WHERE user_key = ?", (user_key,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "birth_chart_degrees": json.loads(row[0]),
            "ruler_mapping": json.loads(row[1])
        }
    return None

def save_chart_cache(user_key, birth_chart_degrees, ruler_mapping):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO natal_charts (user_key, birth_chart_degrees, ruler_mapping)
        VALUES (?, ?, ?)
    ''', (user_key, json.dumps(birth_chart_degrees), json.dumps(ruler_mapping)))
    conn.commit()
    conn.close()
