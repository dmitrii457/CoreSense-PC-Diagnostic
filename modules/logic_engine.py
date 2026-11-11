
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class LogicEngine:
    def __init__(self):
        rules_path = BASE_DIR / "knowledge" / "rules.json"

        with open(rules_path, "r", encoding="utf-8") as file:
            self.rules = json.load(file)

    def evaluate(self, condition, facts):
        return self.evaluate_value(condition, facts) is True

    def evaluate_value(self, condition, facts):
        """Three-valued logic: missing facts remain unknown, including under NOT."""
        if isinstance(condition, str):
            value = facts.get(condition)
            return value if isinstance(value, bool) else None

        if "AND" in condition:
            values = [self.evaluate_value(item, facts) for item in condition["AND"]]
            return False if False in values else (None if None in values else True)

        if "OR" in condition:
            values = [self.evaluate_value(item, facts) for item in condition["OR"]]
            return True if True in values else (None if None in values else False)

        if "NOT" in condition:
            value = self.evaluate_value(condition["NOT"], facts)
            return None if value is None else not value

        return False

    def infer(self, facts):
        results = []

        for rule in self.rules:
            if self.evaluate(rule["conditions"], facts):
                results.append({
                    "rule": rule["id"],
                    "conclusion": rule["conclusion"],
                    "explanation": rule["explanation"]
                })

        return results


if __name__ == "__main__":
    engine = LogicEngine()

    user_facts = {
        "computer_not_starting": True,
        "no_power_indicator": True,
        "fans_not_spinning": True,
        "no_display": False,
        "monitor_power_on": False,
        "computer_slow": False,
        "high_cpu_usage": False,
        "internet_not_working": False
    }

    results = engine.infer(user_facts)

    print("РЕЗУЛЬТАТ ДИАГНОСТИКИ")

    if results:
        for result in results:
            print("Правило:", result["rule"])
            print("Вывод:", result["conclusion"])
            print("Объяснение:", result["explanation"])
    else:
        print("Подходящих правил не найдено.")
