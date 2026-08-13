from .base import BaseInterpreter

class CareerInterpreter(BaseInterpreter):
    def analyze(self, planets: dict) -> dict:
        category = "career"
        mc_sign = planets['MC']['sign']
        sun_sign = planets['Sun']['sign']
        sun_house = planets['Sun']['house']
        saturn_house = planets['Saturn']['house']

        keys = {
            "mc_target": f"MC_{mc_sign}",
            "sun_focus": f"Sun_{sun_sign}_H{sun_house}",
            "saturn_discipline": f"Saturn_H{saturn_house}"
        }

        return {
            "target_career": self.fetch_text(category, keys["mc_target"]),
            "core_identity_work": self.fetch_text(category, keys["sun_focus"]),
            "discipline_and_structure": self.fetch_text(category, keys["saturn_discipline"])
        }
