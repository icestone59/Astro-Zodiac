import sqlite3

class BaseInterpreter:
    def __init__(self, db_path: str = "astro_rules.db"):
        self.db_path = db_path

    def get_content(self, category: str, lookup_key: str) -> str:
        """ดึงบทวิเคราะห์จาก DB ตาม Category และ Lookup Key"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT content FROM natal_interpretations WHERE category = ? AND lookup_key = ?",
                (category, lookup_key)
            )
            row = cursor.fetchone()
            conn.close()
            return row[0] if row else f"[{lookup_key}] รอการเพิ่มบทวิเคราะห์ในฐานข้อมูล"
        except Exception as e:
            return f"Error fetching [{lookup_key}]: {str(e)}"
