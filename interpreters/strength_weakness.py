from .base import BaseInterpreter

class StrengthWeaknessInterpreter(BaseInterpreter):
    def analyze(self, planets: dict) -> dict:
        category = "strength_weakness"
        
        chiron_key = f"Chiron_{planets['Chiron']['sign']}_H{planets['Chiron']['house']}"

        # ดึงบทวิเคราะห์แผลใจ/จุดเปราะบาง (Chiron) ร่วมกับแนวทางแก้ไข
        return {
            "healing_wound_chiron": self.get_content(category, chiron_key),
            "remedy_framework": self.get_content(category, "general_aspect_remedy")
        }
