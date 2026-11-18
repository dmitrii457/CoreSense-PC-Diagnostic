
from modules.logic_engine import LogicEngine


class ProductionSystem:
    def __init__(self):
        self.engine = LogicEngine()

    def forward_chain(self, initial_facts):
        facts = initial_facts.copy()
        history = []
        fired_rules = set()

        changed = True

        while changed:
            changed = False

            for rule in self.engine.rules:
                if rule["id"] in fired_rules:
                    continue

                if self.engine.evaluate(rule["conditions"], facts):
                    conclusion = rule["conclusion"]

                    if facts.get(conclusion) is False:
                        continue

                    fired_rules.add(rule["id"])

                    history.append({
                        "rule": rule["id"],
                        "conclusion": conclusion,
                        "explanation": rule["explanation"]
                    })

                    if facts.get(conclusion) is not True:
                        facts[conclusion] = True
                        changed = True

        return facts, history


if __name__ == "__main__":
    system = ProductionSystem()

    initial_facts = {
        "computer_not_starting": True,
        "no_power_indicator": True
    }

    facts, history = system.forward_chain(initial_facts)

    print("ПРОДУКЦИОННАЯ СИСТЕМА CoreSense\n")

    for step in history:
        print(
            f"{step['rule']} → {step['conclusion']}\n"
            f"Объяснение: {step['explanation']}\n"
        )

    print("Полученные факты:")
    for fact, value in facts.items():
        print(f"{fact}: {value}")
