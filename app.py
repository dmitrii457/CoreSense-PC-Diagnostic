from extra_pages import ExtraPages
from modern_ui import ModernUI
from feature_ui import FeatureUI
from modules.ai_assistant import AIAssistant
import customtkinter as ctk
from pathlib import Path
import json

from modules.logic_engine import LogicEngine

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

BASE_DIR = Path(__file__).resolve().parent

PURPLE = "#7952E8"
BACKGROUND = ('#F3F5FA', '#0C101B')
PANEL = ('#FFFFFF', '#151D2E')

KNOWLEDGE_BASE = {
    "Компьютер не включается": {
        "cause": "Возможная проблема с питанием",
        "solution": "Проверьте розетку, кабель и подключение блока питания."
    },
    "Нет изображения на мониторе": {
        "cause": "Возможная проблема с видеосистемой",
        "solution": "Проверьте питание монитора, видеокабель и выбранный вход."
    },
    "Компьютер сильно тормозит": {
        "cause": "Возможная высокая нагрузка на систему",
        "solution": "Проверьте загрузку процессора, памяти и диска."
    },
    "Нет звука": {
        "cause": "Возможная проблема с настройками аудио",
        "solution": "Проверьте громкость и устройство вывода."
    },
    "Не работает интернет": {
        "cause": "Возможная проблема с сетью",
        "solution": "Проверьте Wi-Fi, Ethernet и состояние роутера."
    }
}


class FixAI(FeatureUI, ModernUI, ctk.CTk, ExtraPages):

    def __init__(self):
        super().__init__()
        self.setup_features()

        self.title("FixAI — Интеллектуальная диагностика ПК")
        self.geometry("1220x820")
        self.minsize(1100, 760)
        self.configure(fg_color=BACKGROUND)

        self.logic_engine = LogicEngine()
        self.ai_assistant = AIAssistant()
        self.fact_variables = {}

        self.sidebar = ctk.CTkFrame(
            self,
            width=240,
            corner_radius=0,
            fg_color=('#E8EDF6', '#111725')
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.content = ctk.CTkFrame(
            self,
            fg_color=BACKGROUND,
            corner_radius=0
        )
        self.content.pack(side="right", fill="both", expand=True)

        ctk.CTkLabel(
            self.sidebar,
            text="✦  FixAI",
            font=("Segoe UI", 32, "bold"),
            text_color=('#6940C6', '#A78BFA')
        ).pack(pady=(35, 5))

        ctk.CTkLabel(
            self.sidebar,
            text="PC DIAGNOSTIC ASSISTANT",
            text_color=('#59667E', '#9999AD')
        ).pack(pady=(0, 35))

        pages = [
    ("Главная", self.home_page),
    ("Диагностика ПК", self.diagnostic_page),
    ("ИИ-помощник", self.ai_page),
    ("История", self.history_page),
    ("Схема ПК", self.component_page),
    ("Логический вывод", self.logic_page),
    ("Фреймовая модель", self.frames_page),
    ("Семантическая сеть", self.semantic_page),
    ("Машинное обучение", self.ml_page),
    ("База знаний", self.knowledge_page),
    ("О проекте", self.about_page),
    ("Настройки", self.settings_page)
]

        self.nav_buttons = {}
        navigation = ctk.CTkScrollableFrame(self.sidebar, fg_color="transparent", corner_radius=0)
        navigation.pack(fill="both", expand=True, padx=4, pady=0)
        for name, command in pages:
            button = ctk.CTkButton(
                navigation,
                text=name,
                command=lambda n=name, cb=command: self.navigate(n, cb),
                height=36,
                fg_color="transparent",
                hover_color=('#D9D1EA', '#34304D'),
                anchor="w",
                font=("Segoe UI", 14),
                corner_radius=12
            )
            button.pack(fill="x", padx=8, pady=3)
            self.nav_buttons[name] = button

        ctk.CTkLabel(self.sidebar, text="●  Локальная система\nPython  /  Expert System",
                     text_color=('#536B7A', '#7795A8'), font=("Segoe UI", 11), justify="left").pack(side="bottom", pady=24)

        self.navigate("Главная", self.home_page)




    def diagnostic_page(self):
        self.clear_page()

        self.heading(
            "Диагностика ПК",
            "Выберите проблему и получите рекомендации"
        )

        self.problem = ctk.CTkOptionMenu(
            self.content,
            values=list(KNOWLEDGE_BASE.keys()),
            width=430,
            height=45,
            fg_color=('#7656AE', '#453379'),
            button_color=PURPLE
        )
        self.problem.pack(anchor="w", padx=35, pady=15)

        ctk.CTkButton(
            self.content,
            text="Запустить диагностику",
            command=self.run_diagnostic,
            height=45,
            width=250,
            fg_color=PURPLE
        ).pack(anchor="w", padx=35, pady=10)

        self.result = ctk.CTkTextbox(
            self.content,
            font=("Segoe UI", 15),
            fg_color=PANEL,
            wrap="word"
        )
        self.result.pack(
            fill="both",
            expand=True,
            padx=35,
            pady=25
        )

    def run_diagnostic(self):
        problem = self.problem.get()
        data = KNOWLEDGE_BASE[problem]

        answer = (
            f"СИМПТОМ:\n{problem}\n\n"
            f"ВОЗМОЖНАЯ ПРИЧИНА:\n{data['cause']}\n\n"
            f"РЕКОМЕНДАЦИЯ:\n{data['solution']}\n\n"
            "Метод: поиск соответствия в базе знаний."
        )

        self.result.delete("1.0", "end")
        self.result.insert("1.0", answer)

    def logic_page(self):
        self.clear_page()

        self.heading(
            "Логический вывод",
            "Укажите Да или Нет для известных симптомов"
        )

        self.fact_variables = {}

        facts_path = BASE_DIR / "knowledge" / "facts.json"

        with open(facts_path, "r", encoding="utf-8") as file:
            descriptions = json.load(file)

        scroll = ctk.CTkScrollableFrame(
            self.content,
            height=260,
            fg_color=PANEL
        )
        scroll.pack(fill="x", padx=35, pady=10)

        for fact, data in descriptions.items():
            variable = ctk.StringVar(value="unknown")
            self.fact_variables[fact] = variable

            row = ctk.CTkFrame(
                scroll,
                fg_color="transparent"
            )
            row.pack(fill="x", padx=10, pady=7)

            ctk.CTkLabel(
                row,
                text=data["description"],
                width=290,
                anchor="w"
            ).pack(side="left", padx=5)

            for label, value in [
                ("Да", "true"),
                ("Нет", "false"),
                ("Не знаю", "unknown")
            ]:
                ctk.CTkRadioButton(
                    row,
                    text=label,
                    variable=variable,
                    value=value,
                    width=90,
                    fg_color=PURPLE
                ).pack(side="left", padx=5)

        ctk.CTkButton(
            self.content,
            text="Запустить логический вывод",
            command=self.run_logic,
            height=45,
            width=280,
            fg_color=PURPLE
        ).pack(anchor="w", padx=35, pady=15)

        self.logic_result = ctk.CTkTextbox(
            self.content,
            font=("Segoe UI", 14),
            fg_color=PANEL,
            wrap="word"
        )
        self.logic_result.pack(
            fill="both",
            expand=True,
            padx=35,
            pady=(5, 20)
        )

    def run_logic(self):
        facts = {}

        for name, variable in self.fact_variables.items():
            value = variable.get()

            if value == "true":
                facts[name] = True
            elif value == "false":
                facts[name] = False

        _, results = self.ai_assistant.production.forward_chain(facts)

        self.logic_result.delete("1.0", "end")

        if not results:
            self.logic_result.insert(
                "end",
                "Подходящих правил не найдено.\n"
                "Попробуйте указать дополнительные симптомы."
            )
            return

        for result in results:
            self.logic_result.insert(
                "end",
                f"ПРАВИЛО: {result['rule']}\n"
                f"ВЫВОД: {result['conclusion']}\n"
                f"ОБЪЯСНЕНИЕ: {result['explanation']}\n"
                "────────────────────────────\n\n"
            )

    def knowledge_page(self):
        self.clear_page()

        self.heading(
            "База знаний",
            "Факты и правила интеллектуальной системы"
        )

        box = ctk.CTkTextbox(
            self.content,
            font=("Segoe UI", 14),
            fg_color=PANEL,
            wrap="word"
        )
        box.pack(
            fill="both",
            expand=True,
            padx=35,
            pady=15
        )

        for rule in self.logic_engine.rules:
            box.insert(
                "end",
                f"Правило {rule['id']}\n"
                f"Условие: {json.dumps(rule['conditions'], ensure_ascii=False)}\n"
                f"Вывод: {rule['conclusion']}\n"
                f"Объяснение: {rule['explanation']}\n\n"
            )

        box.configure(state="disabled")







if __name__ == "__main__":
    app = FixAI()
    app.mainloop()
