"""Desktop presentation layer. All Tk updates stay on the main thread."""
import math
import queue
import threading
import customtkinter as ctk

BG = "#0C101B"
CARD = "#151D2E"
ACCENT = "#9A7BFF"
MUTED = "#99A8C2"


class ModernUI:
    def clear_page(self):
        self._page_token = getattr(self, "_page_token", 0) + 1
        for widget in self.content.winfo_children():
            widget.destroy()

    def navigate(self, name, callback):
        for label, button in self.nav_buttons.items():
            button.configure(fg_color="#2A2444" if label == name else "transparent",
                             text_color="#D6C9FF" if label == name else MUTED)
        callback()

    def heading(self, title, subtitle):
        top = ctk.CTkFrame(self.content, fg_color="transparent")
        top.pack(fill="x", padx=32, pady=(28, 16))
        ctk.CTkLabel(top, text="РАБОЧЕЕ ПРОСТРАНСТВО  /  FIXAI", text_color=MUTED,
                     font=("Segoe UI", 11, "bold")).pack(anchor="w")
        ctk.CTkLabel(top, text=title, font=("Segoe UI", 29, "bold"),
                     text_color="#F3F5FC").pack(anchor="w", pady=(8, 4))
        ctk.CTkLabel(top, text=subtitle, text_color=MUTED, font=("Segoe UI", 14),
                     wraplength=620, justify="left").pack(anchor="w")

    def home_page(self):
        self.clear_page()
        self.heading("Разберёмся, что с компьютером", "Опишите симптомы. FixAI сопоставит их с правилами и прогнозами моделей.")
        hero = ctk.CTkFrame(self.content, fg_color="#211C39", corner_radius=22,
                           border_width=1, border_color="#40345E")
        hero.pack(fill="x", padx=32, pady=(8, 18))
        left = ctk.CTkFrame(hero, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True, padx=26, pady=26)
        ctk.CTkLabel(left, text="ВАШ ПОМОЩНИК ПО ДИАГНОСТИКЕ", text_color=ACCENT,
                     font=("Segoe UI", 11, "bold")).pack(anchor="w")
        ctk.CTkLabel(left, text="Меньше догадок.\nБольше ясности.", justify="left",
                     font=("Segoe UI", 30, "bold")).pack(anchor="w", pady=12)
        ctk.CTkLabel(left, text="Рекомендации с объяснением каждого шага.",
                     text_color="#B9B1D1", font=("Segoe UI", 13)).pack(anchor="w")
        ctk.CTkButton(left, text="Открыть помощника   →", height=44, corner_radius=12,
                      fg_color="#7952E8", hover_color="#916DF4",
                      command=lambda: self.navigate("ИИ-помощник", self.ai_page)).pack(anchor="w", pady=(20, 0))
        orb = ctk.CTkLabel(hero, text="✦", width=140, font=("Segoe UI", 94), text_color=ACCENT)
        orb.pack(side="right", padx=28)
        token = self._page_token
        def breathe(step=0):
            if token != self._page_token:
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
            card = ctk.CTkFrame(row, fg_color=CARD, corner_radius=16, border_width=1, border_color="#263147")
            card.grid(row=0, column=index, sticky="nsew", padx=(0 if index == 0 else 6, 0 if index == 2 else 6), pady=8)
            ctk.CTkLabel(card, text=number, text_color=ACCENT, font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=18, pady=(16, 6))
            ctk.CTkLabel(card, text=title, font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=18)
            ctk.CTkLabel(card, text=desc, justify="left", text_color=MUTED, font=("Segoe UI", 12)).pack(anchor="w", padx=18, pady=8)
            ctk.CTkButton(card, text="Открыть →", fg_color="transparent", hover_color="#25304A",
                          anchor="w", command=lambda n=name, cb=callback: self.navigate(n, cb)).pack(fill="x", padx=12, pady=(0, 12))
        ctk.CTkLabel(self.content, text="Локальная работа  •  Без отправки запросов в облако",
                     text_color=MUTED, font=("Segoe UI", 12)).pack(anchor="w", padx=36, pady=18)

    def ai_page(self):
        self.clear_page()
        self.heading("ИИ-помощник", "Расскажите, что происходит. Добавьте детали: когда возникла проблема и что уже проверили.")
        examples = ctk.CTkFrame(self.content, fg_color="transparent")
        examples.pack(fill="x", padx=32, pady=(0, 8))
        for title, text in [("Нет питания", "Компьютер не включается, индикатор питания не горит"),
                            ("Тормозит", "Компьютер тормозит и процессор загружен"),
                            ("Перегрев", "Компьютер перегревается и сам перезагружается")]:
            ctk.CTkButton(examples, text=title, width=130, height=30, corner_radius=15,
                          fg_color="#202A40", hover_color="#303D59",
                          command=lambda t=text: self._set_prompt(t)).pack(side="left", padx=(0, 8))
        self.ai_input = ctk.CTkTextbox(self.content, height=96, fg_color=CARD,
                                       border_width=1, border_color="#33415E", corner_radius=14,
                                       font=("Segoe UI", 15), wrap="word")
        self.ai_input.pack(fill="x", padx=32, pady=8)
        self.ai_input.bind("<Control-Return>", lambda event: self.run_ai())
        bar = ctk.CTkFrame(self.content, fg_color="transparent")
        bar.pack(fill="x", padx=32, pady=8)
        self.ai_button = ctk.CTkButton(bar, text="Анализировать   →", height=42, width=200,
                                       corner_radius=12, fg_color="#7952E8", hover_color="#916DF4", command=self.run_ai)
        self.ai_button.pack(side="left")
        self.ai_status = ctk.CTkLabel(bar, text="Готов к запросу  ·  Ctrl + Enter", text_color=MUTED,
                                     font=("Segoe UI", 12))
        self.ai_status.pack(side="left", padx=16)
        self.ai_progress = ctk.CTkProgressBar(self.content, height=3, progress_color=ACCENT, mode="determinate")
        self.ai_progress.pack(fill="x", padx=32, pady=(6, 8))
        self.ai_progress.set(0)
        self.ai_result = ctk.CTkTextbox(self.content, fg_color=CARD, corner_radius=16,
                                        font=("Segoe UI", 14), wrap="word", spacing3=5)
        self.ai_result.pack(fill="both", expand=True, padx=32, pady=(4, 12))
        self.ai_result.insert("1.0", "Здесь появится разбор проблемы.\n\nВыберите пример выше или опишите симптомы своими словами.")
        self.ai_result.configure(state="disabled")
        ctk.CTkButton(self.content, text="Скопировать результат", width=180, height=28,
                      fg_color="transparent", hover_color="#202A40", text_color=MUTED,
                      command=self._copy_result).pack(anchor="e", padx=32, pady=(0, 16))
        self._busy = False

    def _set_prompt(self, text):
        if self._busy:
            return
        self.ai_input.delete("1.0", "end")
        self.ai_input.insert("1.0", text)
        self.ai_input.focus_set()

    def _copy_result(self):
        self.clipboard_clear()
        self.clipboard_append(self.ai_result.get("1.0", "end-1c"))
        self.ai_status.configure(text="Результат скопирован")

    def run_ai(self):
        if self._busy:
            return
        question = self.ai_input.get("1.0", "end-1c").strip()
        if not question:
            self.ai_status.configure(text="Сначала опишите проблему")
            self.ai_input.focus_set()
            return
        self._busy = True
        token = self._page_token
        self.ai_button.configure(state="disabled", text="Анализирую…")
        self.ai_input.configure(state="disabled")
        self.ai_progress.configure(mode="indeterminate")
        self.ai_progress.start()
        self.ai_status.configure(text="Проверяю симптомы и правила…")
        output = queue.Queue()
        def worker():
            try:
                output.put(self.ai_assistant.ask(question))
            except Exception as error:
                output.put(f"Не удалось завершить анализ: {error}")
        threading.Thread(target=worker, daemon=True).start()
        def poll():
            if token != self._page_token:
                return
            try:
                answer = output.get_nowait()
            except queue.Empty:
                self.after(70, poll)
                return
            self.ai_progress.stop()
            self.ai_progress.configure(mode="determinate")
            self.ai_progress.set(1)
            self.ai_result.configure(state="normal")
            self.ai_result.delete("1.0", "end")
            def reveal(offset=0):
                if token != self._page_token:
                    return
                self.ai_result.insert("end", answer[offset:offset + 100])
                if offset + 100 < len(answer):
                    self.after(12, lambda: reveal(offset + 100))
                else:
                    self.ai_result.configure(state="disabled")
                    self.ai_input.configure(state="normal")
                    self.ai_button.configure(state="normal", text="Анализировать   →")
                    self.ai_status.configure(text="Анализ завершён")
                    self._busy = False
            reveal()
        self.after(70, poll)

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
                   "Модели обучены на синтетических данных. Результат предварительный.\n"
                   "Программа не измеряет состояние оборудования автоматически.")
        box.configure(state="disabled")
