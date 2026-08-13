from .base import BaseInterpreter

class PersonalityInterpreter(BaseInterpreter):
    def analyze(self, planets: dict) -> dict:
        category = "personality"
        
        asc_key = f"ASC_{planets['ASC']['sign']}"
        sun_key = f"Sun_{planets['Sun']['sign']}_H{planets['Sun']['house']}"
        moon_key = f"Moon_{planets['Moon']['sign']}_H{planets['Moon']['house']}"

        return {
            "outer_behavior_asc": self.get_content(category, asc_key),
            "core_ego_sun": self.get_content(category, sun_key),
            "inner_emotional_moon": self.get_content(category, moon_key)
        }
