import sqlite3

class BaseInterpreter:
    def __init__(self, db_path: str = "astro_rules.db"):
        self.db_path = db_path

    def fetch_text(self, category: str, lookup_key: str) -> str:
        """ดึงบทวิเคราะห์จาก DB ตาม Category และ Lookup Key"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT content FROM natal_interpretations WHERE category = ? AND lookup_key = ?",
            (category, lookup_key)
        )
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else f"[{lookup_key}] รอการเพิ่มบทวิเคราะห์"
