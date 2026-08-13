from .base import BaseInterpreter

class GrowthInterpreter(BaseInterpreter):
    def analyze(self, planets: dict, houses: dict) -> dict:
        category = "growth"
        
        saturn_key = f"Saturn_{planets['Saturn']['sign']}_H{planets['Saturn']['house']}"
        h12_sign = houses['House_12']['sign']

        return {
            "fear_limiting_beliefs_saturn": self.get_content(category, saturn_key),
            "blind_spot_shadow_self_h12": self.get_content(category, f"H12_{h12_sign}")
        }
