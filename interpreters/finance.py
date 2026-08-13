from .base import BaseInterpreter

class FinanceInterpreter(BaseInterpreter):
    def analyze(self, planets: dict, houses: dict) -> dict:
        category = "finance"
        h2_sign = houses['House_2']['sign']
        h8_sign = houses['House_8']['sign']
        venus_sign = planets['Venus']['sign']

        return {
            "income_structure": self.fetch_text(category, f"H2_{h2_sign}"),
            "shared_resources": self.fetch_text(category, f"H8_{h8_sign}"),
            "attraction_style": self.fetch_text(category, f"Venus_{venus_sign}")
        }
