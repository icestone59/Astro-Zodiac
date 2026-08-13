from .base import BaseInterpreter

class PotentialInterpreter(BaseInterpreter):
    def analyze(self, planets: dict) -> dict:
        category = "potential"
        
        north_node_key = f"NorthNode_{planets['North_Node']['sign']}"
        south_node_key = f"SouthNode_{planets['South_Node']['sign']}"
        jupiter_key = f"Jupiter_{planets['Jupiter']['sign']}_H{planets['Jupiter']['house']}"

        return {
            "past_comfort_zone_south_node": self.get_content(category, south_node_key),
            "evolutionary_direction_north_node": self.get_content(category, north_node_key),
            "expansion_opportunity_jupiter": self.get_content(category, jupiter_key)
        }
