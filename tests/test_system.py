import unittest
from modules.logic_engine import LogicEngine
from modules.production import ProductionSystem
from modules.ai_assistant import AIAssistant, FEATURES
from modules.frames import FrameSystem
from modules.semantic_network import SemanticNetwork
from modules.evaluation import split_dataset, BASE_DIR
import pandas as pd


class SystemTests(unittest.TestCase):
    def test_unknown_under_nested_not(self):
        engine = LogicEngine()
        self.assertIsNone(engine.evaluate_value({"NOT": {"AND": ["missing"]}}, {}))
        self.assertFalse(engine.evaluate({"NOT": {"AND": ["missing"]}}, {}))
        self.assertTrue(engine.evaluate({"NOT": {"AND": ["a"]}}, {"a": False}))

    def test_boolean_operators(self):
        engine = LogicEngine()
        self.assertIs(engine.evaluate_value({"AND": ["a", "b"]}, {"a": False}), False)
        self.assertIs(engine.evaluate_value({"OR": ["a", "b"]}, {"a": True}), True)
        self.assertIsNone(engine.evaluate_value({"OR": ["a", "b"]}, {"a": False}))

    def test_forward_chain_and_no_input_mutation(self):
        initial = {"computer_not_starting": True, "no_power_indicator": True}
        facts, history = ProductionSystem().forward_chain(initial)
        self.assertTrue(facts["check_power_supply"])
        self.assertEqual([step["rule"] for step in history], ["R1", "R5"])
        self.assertNotIn("possible_power_problem", initial)

    def test_assistant_negation_and_unknown(self):
        assistant = AIAssistant()
        self.assertFalse(any(assistant.analyze_text("Компьютер не тормозит и не перегревается")))
        self.assertIn("R5", assistant.ask("Компьютер не включается, индикатор питания не горит"))
        self.assertNotIn("R4:", assistant.ask("Нет интернета"))
        self.assertIn("R4:", assistant.ask("Компьютер включается, но нет интернета"))
        self.assertIn("Введите", assistant.ask("  "))
        self.assertIn("подробнее", assistant.ask("Привет"))

    def test_inheritance(self):
        frames = FrameSystem()
        self.assertEqual(frames.get_properties("Ноутбук")["питание"], "Электрическое")
        self.assertEqual(frames.get_properties("Игровой ПК")["назначение"], "Игры и графика")

    def test_semantic_path(self):
        self.assertEqual(SemanticNetwork().search_path("Компьютер", "Нет питания"),
                         ["Компьютер", "Блок питания", "Нет питания"])

    def test_no_dataset_leakage(self):
        train, test, _, _ = split_dataset(pd.read_csv(BASE_DIR / "data/pc_problems.csv"))
        self.assertFalse(set(map(tuple, train.values)) & set(map(tuple, test.values)))


if __name__ == "__main__":
    unittest.main()
