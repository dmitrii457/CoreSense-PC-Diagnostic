"""Desktop presentation layer. All Tk updates stay on the main thread."""
import math
import customtkinter as ctk

BG = ('#F3F5FA', '#0C101B')
CARD = ('#FFFFFF', '#151D2E')
ACCENT = ('#6940C6', '#9A7BFF')
MUTED = ('#53627B', '#99A8C2')


class ModernUI:
    def clear_page(self):
        self._page_token = getattr(self, "_page_token", 0) + 1
        self._active_page = None
        for widget in self.content.winfo_children():
            widget.destroy()

    def navigate(self, name, callback):
        for label, button in self.nav_buttons.items():
            button.configure(fg_color=('#DDD4F5', '#2A2444') if label == name else "transparent",
                             text_color=('#55329E', '#D6C9FF') if label == name else MUTED)
        callback()

    def heading(self, title, subtitle):
        top = ctk.CTkFrame(self.content, fg_color="transparent")
        top.pack(fill="x", padx=32, pady=(28, 16))
        ctk.CTkLabel(top, text="РАБОЧЕЕ ПРОСТРАНСТВО  /  FIXAI", text_color=MUTED,
                     font=("Segoe UI", 11, "bold")).pack(anchor="w")
        ctk.CTkLabel(top, text=title, font=("Segoe UI", 29, "bold"),
                     text_color=('#17233B', '#F3F5FC')).pack(anchor="w", pady=(8, 4))
        ctk.CTkLabel(top, text=subtitle, text_color=MUTED, font=("Segoe UI", 14),
                     wraplength=620, justify="left").pack(anchor="w")

    def home_page(self):
        self.clear_page()
        self.heading("Разберёмся, что с компьютером", "Опишите симптомы. FixAI сопоставит их с правилами и прогнозами моделей.")
        hero = ctk.CTkFrame(self.content, fg_color=('#EEE8FC', '#211C39'), corner_radius=22,
                           border_width=1, border_color=('#D2C4EE', '#40345E'))
        hero.pack(fill="x", padx=32, pady=(8, 18))
        left = ctk.CTkFrame(hero, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True, padx=26, pady=26)
        ctk.CTkLabel(left, text="ВАШ ПОМОЩНИК ПО ДИАГНОСТИКЕ", text_color=ACCENT,
                     font=("Segoe UI", 11, "bold")).pack(anchor="w")
        ctk.CTkLabel(left, text="Меньше догадок.\nБольше ясности.", justify="left",
                     font=("Segoe UI", 30, "bold")).pack(anchor="w", pady=12)
        ctk.CTkLabel(left, text="Рекомендации с объяснением каждого шага.",
                     text_color=('#635378', '#B9B1D1'), font=("Segoe UI", 13)).pack(anchor="w")
        ctk.CTkButton(left, text="Открыть помощника   →", height=44, corner_radius=12,
                      fg_color="#7952E8", hover_color="#916DF4",
                      command=lambda: self.navigate("ИИ-помощник", self.ai_page)).pack(anchor="w", pady=(20, 0))
        orb = ctk.CTkLabel(hero, text="✦", width=140, font=("Segoe UI", 94), text_color=ACCENT)
        orb.pack(side="right", padx=28)
        token = self._page_token
        def breathe(step=0):
            if token != self._page_token or not self.preferences["animations"]:
                return
            v = (math.sin(step / 12) + 1) / 2
            orb.configure(text_color=f"#{int(135 + 35*v):02x}{int(101 + 37*v):02x}ff")
            self.after(55, lambda: breathe(step + 1))
        breathe()
        row = ctk.CTkFrame(self.content, fg_color="transparent")
        row.pack(fill="x", padx=32)
        row.grid_columnconfigure((0, 1, 2), weight=1, uniform="cards")
        cards = [("01", "Объяснимый вывод", "Факты, AND / OR / NOT\nи цепочки правил", self.logic_page, "Логический вывод"),
                 ("02", "Связанные знания", "Фреймы, наследование\nи семантическая сеть", self.frames_page, "Фреймовая модель"),
                 ("03", "Две модели", "Random Forest\nи нейронная сеть", self.ml_page, "Машинное обучение")]
        for index, (number, title, desc, callback, name) in enumerate(cards):
            card = ctk.CTkFrame(row, fg_color=CARD, corner_radius=16, border_width=1, border_color=('#D5DCE9', '#263147'))
            card.grid(row=0, column=index, sticky="nsew", padx=(0 if index == 0 else 6, 0 if index == 2 else 6), pady=8)
            ctk.CTkLabel(card, text=number, text_color=ACCENT, font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=18, pady=(16, 6))
            ctk.CTkLabel(card, text=title, font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=18)
            ctk.CTkLabel(card, text=desc, justify="left", text_color=MUTED, font=("Segoe UI", 12)).pack(anchor="w", padx=18, pady=8)
            ctk.CTkButton(card, text="Открыть →", fg_color="transparent", hover_color=('#DFE5F2', '#25304A'),
                          anchor="w", command=lambda n=name, cb=callback: self.navigate(n, cb)).pack(fill="x", padx=12, pady=(0, 12))
        ctk.CTkLabel(self.content, text="Локальная работа  •  Без отправки запросов в облако",
                     text_color=MUTED, font=("Segoe UI", 12)).pack(anchor="w", padx=36, pady=18)





    def about_page(self):
        self.clear_page()
        self.heading("О FixAI", "Учебная экспертная система для предварительной диагностики ПК")
        box = ctk.CTkTextbox(self.content, fg_color=CARD, corner_radius=16, font=("Segoe UI", 16), wrap="word")
        box.pack(fill="both", expand=True, padx=32, pady=(8, 28))
        box.insert("1.0", "FIXAI  /  DESKTOP\n\nPython · CustomTkinter · scikit-learn\n\n"
                   "База знаний: факты и продукционные правила в JSON.\n"
                   "Логика: AND, OR, NOT с неизвестными значениями.\n"
                   "Прямой вывод: цепочки правил с объяснением.\n"
                   "Фреймы: наследование, поиск и изменение свойств.\n"
                   "Семантическая сеть: компоненты, симптомы и связи.\n"
                   "Обучение: Random Forest и MLPClassifier.\n\n"
                   "Помощник объединяет правила, прогнозы и сведения о компонентах.\n"
                   "Текстовые запросы обрабатываются локально по словарю симптомов.\n\n"
                   "Диалог: уточняющие вопросы и план проверки.\n"
                   "История: локальная SQLite, восстановление прогресса.\n"
                   "Отчёты: экспорт в PDF с кириллицей.\n"
                   "Оформление: светлая/тёмная тема, отключение анимаций.\n\n"
                   "Модели обучены на синтетических данных. Результат предварительный.\n"
                   "Программа не измеряет состояние оборудования автоматически.")
        box.configure(state="disabled")
