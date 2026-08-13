from .base import BaseInterpreter

class LoveInterpreter(BaseInterpreter):
    def analyze(self, planets: dict, houses: dict) -> dict:
        category = "love"
        
        h7_sign = houses['House_7']['sign']
        h5_sign = houses['House_5']['sign']
        venus_key = f"Venus_{planets['Venus']['sign']}"
        mars_key = f"Mars_{planets['Mars']['sign']}"

        return {
            "partner_attraction_h7": self.get_content(category, f"H7_{h7_sign}"),
            "romance_joy_h5": self.get_content(category, f"H5_{h5_sign}"),
            "love_language_venus": self.get_content(category, venus_key),
            "emotional_drive_mars": self.get_content(category, mars_key)
        }
