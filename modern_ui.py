"""Desktop layout and shared page transitions."""
import customtkinter as ctk
from ui_components import MotionButton, SurfaceFrame, CoreOrbit, BG, SURFACE, TEXT, MUTED, ACCENT, BORDER, PRIMARY, SOFT
from ui_motion import color_value, mix_color


class ModernUI:
    def clear_page(self):
        self._page_token = getattr(self, "_page_token", 0) + 1
        self._active_page = None
        self.motion.cancel_tree(self.content)
        for widget in self.content.winfo_children():
            widget.destroy()
        token = self._page_token
        animated = self.preferences["animations"]
        self.content.place_configure(x=18 if animated else 0, y=7 if animated else 0)

        def enter():
            if token != self._page_token:
                return
            self.motion.animate(self.content, "page-slide",
                lambda p: self.content.place_configure(x=round(18*(1-p)), y=round(7*(1-p))), 240)
            self._enhance_page(self.content)

        self.motion.defer(self.content, "page-enter", enter)

    def _enhance_page(self, parent):
        for widget in parent.winfo_children():
            if isinstance(widget, (ctk.CTkEntry, ctk.CTkTextbox)) and not getattr(widget, "_motion_focus", False):
                widget._motion_focus = True
                def focus_color(target, active):
                    start = color_value(target, target.cget("border_color"))
                    end = color_value(target, ACCENT if active else BORDER)
                    self.motion.animate(target, "focus-border",
                        lambda p: target.configure(border_color=mix_color(start, end, p)), 170)
                widget.bind("<FocusIn>", lambda event, target=widget: focus_color(target, True), add="+")
                widget.bind("<FocusOut>", lambda event, target=widget: focus_color(target, False), add="+")
            self._enhance_page(widget)

    def navigate(self, name, callback):
        self._active_nav = name
        for label, button in self.nav_buttons.items():
            button.configure(fg_color=SOFT if label == name else "transparent",
                             text_color=ACCENT if label == name else MUTED)
        callback()

    def heading(self, title, subtitle):
        top = SurfaceFrame(self.content, fg_color="transparent")
        top.pack(fill="x", padx=32, pady=(25, 14))
        ctk.CTkLabel(top, text=title, font=("Segoe UI", 29, "bold"), text_color=TEXT,
                     anchor="w").pack(fill="x", pady=(0, 4))
        ctk.CTkLabel(top, text=subtitle, text_color=MUTED, font=("Segoe UI", 13),
                     wraplength=740, justify="left", anchor="w").pack(fill="x")

    def home_page(self):
        self.clear_page()
        hero = SurfaceFrame(self.content, fg_color=("#EEE9FA", "#211A35"), corner_radius=24,
                            border_color=("#D9CDF4", "#45365E"))
        hero.pack(fill="x", padx=32, pady=(30, 24))
        orbit_host = SurfaceFrame(hero, fg_color="transparent")
        orbit_host.pack(side="right", padx=(10, 28), pady=28)
        CoreOrbit(orbit_host, size=180).pack()
        left = SurfaceFrame(hero, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True, padx=(28, 0), pady=25)
        ctk.CTkLabel(left, text="Диагностика ПК", justify="left", text_color=TEXT,
                     font=("Segoe UI", 38, "bold")).pack(anchor="w", pady=(12, 8))
        ctk.CTkLabel(left, text="Опиши симптомы, чтобы получить объяснение и план проверки.",
                     text_color=MUTED, font=("Segoe UI", 14), wraplength=420,
                     justify="left").pack(anchor="w")
        actions = SurfaceFrame(left, fg_color="transparent")
        actions.pack(anchor="w", pady=(20, 0))
        MotionButton(actions, text="Начать диагностику  →", width=190, height=42, fg_color=PRIMARY,
                      command=lambda: self.navigate("ИИ-помощник", self.ai_page)).pack(side="left")
        MotionButton(actions, text="Схема ПК", width=105, height=42, fg_color=("#E5DCF7", "#2C2546"),
                      text_color=ACCENT, hover_color=("#D6C9EE", "#42365D"),
                      command=lambda: self.navigate("Схема ПК", self.component_page)).pack(side="left", padx=10)
        title_row = SurfaceFrame(self.content, fg_color="transparent")
        title_row.pack(fill="x", padx=34, pady=(0, 10))
        ctk.CTkLabel(title_row, text="Инструменты системы", text_color=TEXT,
                     font=("Segoe UI", 18, "bold")).pack(side="left")
        row = SurfaceFrame(self.content, fg_color="transparent")
        row.pack(fill="x", padx=32)
        row.grid_columnconfigure((0, 1, 2), weight=1, uniform="tools")
        cards = [
            (len(self.logic_engine.rules), "Правила вывода", "Факты, условия и понятные объяснения", self.logic_page, "Логический вывод"),
            (len(self.ai_assistant.frames.frames), "Фреймы объектов", "Свойства компонентов и наследование", self.frames_page, "Фреймовая модель"),
            (sum(model is not None for model in (self.ai_assistant.classifier, self.ai_assistant.neural_network)),
             "Модели обучения", "Random Forest и нейронная сеть", self.ml_page, "Машинное обучение"),
        ]
        for index, (number, title, description, callback, name) in enumerate(cards):
            card = SurfaceFrame(row, fg_color=SURFACE, corner_radius=18)
            card.grid(row=0, column=index, sticky="nsew", padx=(0 if index == 0 else 6, 0 if index == 2 else 6))
            value = ctk.CTkLabel(card, text=str(number), text_color=ACCENT, font=("Segoe UI", 28, "bold"))
            value.pack(anchor="w", padx=20, pady=(16, 2))
            ctk.CTkLabel(card, text=title, text_color=TEXT, font=("Segoe UI", 15, "bold")).pack(anchor="w", padx=20)
            ctk.CTkLabel(card, text=description, text_color=MUTED, font=("Segoe UI", 11),
                         wraplength=215, justify="left").pack(anchor="w", padx=20, pady=(6, 10))
            MotionButton(card, text="Открыть раздел   →", fg_color="transparent", text_color=ACCENT,
                          hover_color=SOFT, anchor="w", height=30,
                          command=lambda n=name, cb=callback: self.navigate(n, cb)).pack(fill="x", padx=12, pady=(0, 12))
            self.motion.animate(value, "counter", lambda p, target=value, total=number: target.configure(text=str(round(total*p))),
                                500, delay=index*60)
        quick = SurfaceFrame(self.content, fg_color="transparent")
        quick.pack(fill="x", padx=32, pady=18)
        for label, page, callback in (
            ("История диагностик", "История", self.history_page),
            ("Режим защиты", "Режим защиты", self.defense_page),
        ):
            MotionButton(quick, text=label, width=165, fg_color=SOFT, text_color=TEXT,
                         hover_color=("#E0D7F4", "#35304B"),
                         command=lambda name=page, cb=callback: self.navigate(name, cb)).pack(side="left", padx=(0, 10))

    def result_card(self, parent, title):
        panel = SurfaceFrame(parent, fg_color=SURFACE)
        ctk.CTkLabel(panel, text=title, text_color=TEXT, font=("Segoe UI", 15, "bold")).pack(
            anchor="w", padx=16, pady=(12, 8)
        )
        return panel

    def animate_text(self, widget, text, duration=700):
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        shown = min(45, len(text))
        widget.insert("1.0", text[:shown])
        widget.configure(state="disabled")

        def reveal(progress):
            nonlocal shown
            count = min(len(text), max(shown, round(len(text)*progress)))
            widget.configure(state="normal")
            widget.insert("end", text[shown:count])
            widget.configure(state="disabled")
            shown = count

        def decorate():
            widget.tag_config("report_heading", foreground=color_value(widget, ACCENT), spacing1=10, spacing3=6)
            for index, line in enumerate(text.splitlines(), 1):
                if line.isupper() and len(line) < 80:
                    widget.tag_add("report_heading", f"{index}.0", f"{index}.end")

        self.motion.animate(widget, "report-text", reveal, duration, done=decorate)

    def about_page(self):
        self.clear_page()
        self.heading("О CoreSense", "Экспертная система для предварительной диагностики компьютера")
        box = ctk.CTkTextbox(self.content, fg_color=SURFACE, corner_radius=18, font=("Segoe UI", 14), wrap="word")
        box.pack(fill="both", expand=True, padx=32, pady=(6, 25))
        self.animate_text(box,
            "CORESENSE\nЧувствовать систему\n\n"
            "Ваш помощник по диагностике ПК. Задаёт уточняющие вопросы, объясняет выводы и предлагает проверки по шагам.\n\n"
            "ЗНАНИЯ И ВЫВОД\nJSON-база фактов, продукционные правила и прямой вывод.\n"
            "AND, OR, NOT с неизвестными значениями.\nФреймы с наследованием и семантическая сеть.\n\n"
            "ОБУЧЕННЫЕ МОДЕЛИ\nRandom Forest и MLPClassifier сравнивают категории неисправностей.\n\n"
            "РАБОТА С ПРИЛОЖЕНИЕМ\nЛокальная история, восстановление прогресса и отчёты в PDF.\n"
            "Светлая и тёмная темы. Все анимации можно отключить в настройках.\n\n"
            "Модели обучены на синтетических данных. Результат предварительный.\n"
            "Программа не измеряет состояние оборудования автоматически.")
