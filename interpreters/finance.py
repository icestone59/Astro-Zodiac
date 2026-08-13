from .base import BaseInterpreter

class FinanceInterpreter(BaseInterpreter):
    def analyze(self, planets: dict, houses: dict) -> dict:
        category = "finance"
        
        h2_sign = houses['House_2']['sign']
        h8_sign = houses['House_8']['sign']
        venus_key = f"Venus_{planets['Venus']['sign']}_H{planets['Venus']['house']}"

        return {
            "self_earned_income_h2": self.get_content(category, f"H2_{h2_sign}"),
            "shared_assets_investment_h8": self.get_content(category, f"H8_{h8_sign}"),
            "wealth_attraction_venus": self.get_content(category, venus_key)
        }
