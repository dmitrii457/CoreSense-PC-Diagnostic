import tempfile
import unittest
from pathlib import Path
from modules.local_store import LocalStore
from modules.diagnostic_session import DiagnosticSession
from modules.ai_assistant import AIAssistant
from modules.pdf_report import export_session_pdf


class FeatureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.assistant = AIAssistant()

    def test_followup_changes_inference_and_unknown_is_not_repeated(self):
        session = DiagnosticSession("Компьютер не включается", {"computer_not_starting": True})
        self.assertEqual(session.next_question()["fact"], "no_power_indicator")
        session.respond(True)
        self.assertIn("R5:", self.assistant.ask(session.question, session.facts))
        self.assertEqual(session.next_question()["fact"], "fans_not_spinning")
        session.respond(None)
        self.assertIsNone(session.next_question())
        self.assertIsNone(session.facts["fans_not_spinning"])

    def test_inverse_question_and_false_answers(self):
        session = DiagnosticSession("Нет интернета", {"internet_not_working": True})
        session.respond(True)  # Computer starts => computer_not_starting=False.
        self.assertIs(session.facts["computer_not_starting"], False)
        self.assertIn("R4:", self.assistant.ask(session.question, session.facts))
        self.assertNotIn("R1:", self.assistant.ask("Компьютер не включается, индикатор не горит", {"no_power_indicator": False}))

    def test_step_transitions_and_roundtrip(self):
        session = DiagnosticSession("Нет звука", {"no_sound": True})
        session.set_plan("audio_problem")
        session.record_step("not_helped")
        session.set_plan("audio_problem")
        self.assertEqual(session.current_step(), 1)
        restored = DiagnosticSession.from_dict(session.to_dict())
        restored.record_step("helped")
        self.assertEqual(restored.status, "resolved")
        self.assertIsNone(restored.current_step())
        with self.assertRaises(ValueError):
            restored.record_step("not_helped")
        self.assertEqual(session.status, "active")

    def test_exhausted_plan_and_category_change(self):
        session = DiagnosticSession("Нет звука", {})
        session.set_plan("audio_problem")
        for _ in range(len(session.steps)):
            session.record_step("skipped")
        self.assertEqual(session.status, "exhausted")
        session.set_plan("network_problem")
        self.assertEqual(session.status, "active")
        self.assertEqual(session.current_step(), 0)

    def test_history_and_settings_survive_new_store(self):
        with tempfile.TemporaryDirectory() as folder:
            store = LocalStore(folder)
            session = DiagnosticSession("Нет звука 100%", {"no_sound": True})
            session.set_plan("audio_problem")
            session.record_step("not_helped")
            store.save_session(session)
            session.answer = "Проверка <текст> & кириллица"
            store.save_session(session)
            store.save_settings({"theme": "light", "animations": False})
            reopened = LocalStore(folder)
            self.assertEqual(len(reopened.list_sessions()), 1)
            self.assertEqual(len(reopened.list_sessions("100%")), 1)
            self.assertEqual(len(reopened.list_sessions("100_")), 0)
            self.assertEqual(reopened.settings(), {"theme": "light", "animations": False})
            restored = DiagnosticSession.from_dict(reopened.load_session(session.id))
            self.assertEqual(restored.current_step(), 1)
            self.assertEqual(restored.answer, session.answer)

    def test_unknown_symptom_has_no_arbitrary_plan(self):
        self.assertIsNone(self.assistant.plan_category("Привет"))

    def test_pdf_unicode_and_special_characters(self):
        with tempfile.TemporaryDirectory() as folder:
            session = DiagnosticSession("Нет звука <проверка> & настройки", {"no_sound": True})
            session.answer = self.assistant.ask(session.question)
            session.set_plan("audio_problem")
            path = export_session_pdf(session, Path(folder) / "report.pdf")
            self.assertTrue(path.read_bytes().startswith(b"%PDF-"))
            self.assertGreater(path.stat().st_size, 5000)


if __name__ == "__main__":
    unittest.main()
