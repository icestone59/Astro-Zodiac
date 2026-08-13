from .base import BaseInterpreter

class CareerInterpreter(BaseInterpreter):
    def analyze(self, planets: dict) -> dict:
        category = "career"
        
        mc_key = f"MC_{planets['MC']['sign']}"
        sun_key = f"Sun_{planets['Sun']['sign']}_H{planets['Sun']['house']}"
        saturn_key = f"Saturn_H{planets['Saturn']['house']}"

        return {
            "career_target_mc": self.get_content(category, mc_key),
            "work_identity_sun": self.get_content(category, sun_key),
            "discipline_structure_saturn": self.get_content(category, saturn_key)
        }
