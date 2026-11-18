"""Interactive walkthrough using the live rule engine and session planner."""
import customtkinter as ctk

from modules.diagnostic_session import DiagnosticSession, FACT_LABELS
from ui_components import MotionButton, SurfaceFrame, SURFACE


EXAMPLES = {
    "Питание": "Компьютер не включается",
    "Интернет": "Нет интернета",
    "USB": "Не работает USB",
}


class DefenseUI:
    def defense_page(self):
        self.clear_page()
        self.heading("Режим защиты", "Выберите пример и ответьте на вопрос. Факты, правила и план обновятся сразу.")
        controls = SurfaceFrame(self.content, fg_color="transparent")
        controls.pack(fill="x", padx=32, pady=8)
        for label, prompt in EXAMPLES.items():
            MotionButton(controls, text=label, width=105,
                         command=lambda text=prompt: self.start_demo(text)).pack(side="left", padx=(0, 8))
        self.demo_question = ctk.CTkLabel(self.content, text="", wraplength=700)
        self.demo_question.pack(anchor="w", padx=32, pady=6)
        replies = SurfaceFrame(self.content, fg_color="transparent")
        replies.pack(fill="x", padx=32, pady=(0, 8))
        self.demo_buttons = []
        for label, value in [("Да", True), ("Нет", False), ("Не знаю", None)]:
            button = MotionButton(replies, text=label, width=90, command=lambda answer=value: self.answer_demo(answer))
            button.pack(side="left", padx=(0, 8))
            self.demo_buttons.append(button)
        body = SurfaceFrame(self.content, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=32, pady=(0, 22))
        body.grid_columnconfigure((0, 1, 2), weight=1, uniform="demo")
        body.grid_rowconfigure(0, weight=1)
        self.demo_panels = []
        for column, title in enumerate(("Факты", "Цепочка вывода", "План проверки")):
            panel = SurfaceFrame(body, fg_color=SURFACE)
            panel.grid(row=0, column=column, sticky="nsew", padx=4)
            ctk.CTkLabel(panel, text=title, font=("Segoe UI", 15, "bold")).pack(anchor="w", padx=12, pady=8)
            box = ctk.CTkTextbox(panel, wrap="word", width=100)
            box.pack(fill="both", expand=True, padx=10, pady=(0, 10))
            self.demo_panels.append(box)
        self.start_demo(EXAMPLES["Питание"])

    def start_demo(self, prompt):
        self.demo_session = DiagnosticSession(prompt, self.ai_assistant.collect_facts(prompt))
        self.refresh_demo()

    def answer_demo(self, value):
        if self.demo_session.next_question():
            self.demo_session.respond(value)
            self.refresh_demo()

    def refresh_demo(self):
        session = self.demo_session
        _, trace = self.ai_assistant.production.forward_chain(session.facts)
        session.set_plan(self.ai_assistant.plan_category(session.question, session.facts))
        question = session.next_question()
        self.demo_question.configure(text=session.question + "  /  " + (
            question["prompt"] if question else "Уточнения завершены"))
        for button in self.demo_buttons:
            button.configure(state="normal" if question else "disabled")
        labels = {True: "Да", False: "Нет", None: "Неизвестно"}
        facts = "\n\n".join(f"{FACT_LABELS.get(key, key)}\n{labels[value]}" for key, value in session.facts.items())
        rules = "\n\n".join(f"{step['rule']} → {step['conclusion']}\n{step['explanation']}" for step in trace)
        if session.category == "usb_problem":
            rules = "Сценарий USB использует ветвление по ответам.\n\n" + rules
        plan = "\n\n".join(f"{i}. {step['text']}" for i, step in enumerate(session.steps, 1))
        for box, value in zip(self.demo_panels, (facts, rules or "Пока нет сработавших правил.", plan or "План пока не выбран.")):
            self.animate_text(box, value, 250)
