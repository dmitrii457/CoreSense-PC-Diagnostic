"""Dialog, history, troubleshooting, component map and personal preferences."""
import queue
import threading
import sqlite3
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox
import customtkinter as ctk
from modules.local_store import LocalStore
from modules.diagnostic_session import DiagnosticSession, FACT_LABELS
from modules.ai_assistant import DIAGNOSES
from modules.frames import FrameSystem
from modules.semantic_network import SemanticNetwork

SURFACE = ("#FFFFFF", "#151D2E")
TEXT = ("#17233B", "#F3F5FC")
MUTED = ("#53627B", "#99A8C2")
PRIMARY = "#7952E8"
SOFT = ("#EBE5FB", "#27213E")


class FeatureUI:
    def setup_features(self):
        self.store = LocalStore()
        self.preferences = self.store.settings()
        ctk.set_appearance_mode(self.preferences["theme"])
        self._busy = False
        self.current_session = None
        records = self.store.list_sessions()
        if records:
            self.current_session = DiagnosticSession.from_dict(self.store.load_session(records[0][0]))

    def ai_page(self):
        self.clear_page()
        self._active_page = "assistant"
        self.heading("ИИ-помощник", "Уточните симптомы и пройдите проверки. Ответы и прогресс сохраняются автоматически.")
        examples = ctk.CTkFrame(self.content, fg_color="transparent")
        examples.pack(fill="x", padx=32, pady=(0, 6))
        for label, prompt in [("Нет питания", "Компьютер не включается"), ("Нет изображения", "Нет изображения на мониторе"),
                              ("Нет интернета", "Нет интернета"), ("Перегрев", "Компьютер перегревается")]:
            ctk.CTkButton(examples, text=label, width=135, height=28, fg_color=SOFT,
                          text_color=TEXT, hover_color=("#DBD1F4", "#35304E"),
                          command=lambda text=prompt: self._set_prompt(text)).pack(side="left", padx=(0, 7))
        self.ai_input = ctk.CTkTextbox(self.content, height=70, fg_color=SURFACE, text_color=TEXT,
                                       border_width=1, border_color=("#C8D1E1", "#33415E"),
                                       corner_radius=12, font=("Segoe UI", 14), wrap="word")
        self.ai_input.pack(fill="x", padx=32, pady=6)
        if self.current_session:
            self.ai_input.insert("1.0", self.current_session.question)
        self.ai_input.bind("<Control-Return>", lambda event: self.run_ai())
        bar = ctk.CTkFrame(self.content, fg_color="transparent")
        bar.pack(fill="x", padx=32, pady=6)
        self.ai_button = ctk.CTkButton(bar, text="Новая диагностика →", height=38, width=185,
                                       fg_color=PRIMARY, command=self.run_ai,
                                       state="disabled" if self._busy else "normal")
        self.ai_button.pack(side="left")
        self.ai_status = ctk.CTkLabel(bar, text="Анализирую…" if self._busy else "Ctrl + Enter для нового запроса", text_color=MUTED)
        self.ai_status.pack(side="left", padx=12)
        self.ai_progress = ctk.CTkProgressBar(self.content, height=3, progress_color=PRIMARY, mode="determinate")
        self.ai_progress.pack(fill="x", padx=32, pady=(4, 8))
        self.ai_progress.set(0)
        if self._busy and self.preferences["animations"]:
            self.ai_progress.configure(mode="indeterminate")
            self.ai_progress.start()
        # Reserve the action row before the expanding result area.
        actions = ctk.CTkFrame(self.content, fg_color="transparent")
        actions.pack(side="bottom", fill="x", padx=32, pady=(6, 15))
        ctk.CTkButton(actions, text="Скопировать", width=125, fg_color=SOFT, text_color=TEXT,
                      command=self._copy_result).pack(side="left")
        ctk.CTkButton(actions, text="Сохранить PDF", width=145, fg_color=PRIMARY,
                      command=self.export_current_pdf).pack(side="left", padx=8)
        ctk.CTkButton(actions, text="История", width=100, fg_color=SOFT, text_color=TEXT,
                      command=lambda: self.navigate("История", self.history_page)).pack(side="right")
        body = ctk.CTkFrame(self.content, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=32, pady=2)
        body.grid_columnconfigure(0, weight=3)
        body.grid_columnconfigure(1, weight=2, minsize=300)
        body.grid_rowconfigure(0, weight=1)
        self.ai_result = ctk.CTkTextbox(body, fg_color=SURFACE, text_color=TEXT,
                                        font=("Segoe UI", 13), wrap="word", corner_radius=14)
        self.ai_result.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        self.dialog_panel = ctk.CTkScrollableFrame(body, fg_color=SURFACE, corner_radius=14)
        self.dialog_panel.grid(row=0, column=1, sticky="nsew")
        self._render_session()

    def _set_prompt(self, text):
        if self._busy:
            return
        self.ai_input.configure(state="normal")
        self.ai_input.delete("1.0", "end")
        self.ai_input.insert("1.0", text)
        self.ai_input.focus_set()

    def _copy_result(self):
        if not self.current_session or not self.current_session.answer:
            self.ai_status.configure(text="Сначала выполните диагностику")
            return
        self.clipboard_clear()
        self.clipboard_append(self.current_session.report_text())
        self.ai_status.configure(text="Полный отчёт скопирован")

    def run_ai(self):
        if self._busy:
            return
        question = self.ai_input.get("1.0", "end-1c").strip()
        if not question:
            self.ai_status.configure(text="Сначала опишите проблему")
            return
        session = DiagnosticSession(question, self.ai_assistant.collect_facts(question))
        self.current_session = session
        self._analyze_session(session)

    def _analyze_session(self, session):
        self._answer_generation = getattr(self, "_answer_generation", 0) + 1
        self._busy = True
        self._persist_session(session)
        self.ai_button.configure(state="disabled")
        self.ai_input.configure(state="disabled")
        self.ai_status.configure(text="Проверяю факты и правила…")
        self._render_dialog()
        token = self._page_token
        if self.preferences["animations"]:
            self.ai_progress.configure(mode="indeterminate")
            self.ai_progress.start()
        output = queue.Queue()
        facts = session.facts.copy()

        def worker():
            try:
                output.put((self.ai_assistant.ask(session.question, facts),
                            self.ai_assistant.plan_category(session.question, facts), None))
            except Exception as error:
                output.put((None, None, str(error)))

        threading.Thread(target=worker, daemon=True).start()

        def poll():
            try:
                answer, category, error = output.get_nowait()
            except queue.Empty:
                self.after(60, poll)
                return
            if not error:
                session.answer = answer
                session.set_plan(category)
                self._persist_session(session)
            self._busy = False
            # Finish the record even after navigation, but never touch destroyed widgets.
            if getattr(self, "_active_page", None) != "assistant" or not self.current_session or self.current_session.id != session.id:
                return
            self.ai_progress.stop()
            self.ai_progress.configure(mode="determinate")
            self.ai_progress.set(1 if not error else 0)
            self.ai_button.configure(state="normal")
            self.ai_input.configure(state="normal")
            self.ai_status.configure(text="Ошибка: " + error if error else "Сохранено в историю")
            self._render_session(animate=token == self._page_token and self.preferences["animations"])

        self.after(60, poll)

    def _persist_session(self, session):
        try:
            self.store.save_session(session)
        except (OSError, sqlite3.Error) as error:
            messagebox.showerror("История CoreSense", f"Не удалось сохранить диагностику: {error}", parent=self)

    def _render_session(self, animate=False):
        self._answer_generation = getattr(self, "_answer_generation", 0) + 1
        generation = self._answer_generation
        session = self.current_session
        text = session.answer if session and session.answer else "Опишите проблему или выберите пример.\n\nЗдесь появятся прогнозы, объяснения правил и сведения о компонентах."
        self.ai_result.configure(state="normal")
        self.ai_result.delete("1.0", "end")
        token = self._page_token
        def reveal(offset=0):
            if generation != self._answer_generation or token != self._page_token or getattr(self, "_active_page", None) != "assistant":
                return
            length = 130 if animate and self.preferences["animations"] else len(text)
            self.ai_result.configure(state="normal")
            self.ai_result.insert("end", text[offset:offset + length])
            self.ai_result.configure(state="disabled")
            if offset + length < len(text):
                self.after(12, lambda: reveal(offset + length))
        reveal()
        self._render_dialog()

    def _render_dialog(self):
        for child in self.dialog_panel.winfo_children():
            child.destroy()
        panel = self.dialog_panel
        session = self.current_session
        def label(text, bold=False, color=TEXT):
            ctk.CTkLabel(panel, text=text, justify="left", anchor="w", wraplength=290,
                         font=("Segoe UI", 14 if bold else 12, "bold" if bold else "normal"),
                         text_color=color).pack(fill="x", padx=10, pady=(8, 5))
        label("Уточняющие вопросы", True)
        if not session:
            label("После анализа здесь появятся вопросы и план проверки.", color=MUTED)
            return
        question = session.next_question()
        if question:
            label(question["prompt"])
            row = ctk.CTkFrame(panel, fg_color="transparent")
            row.pack(fill="x", padx=10, pady=6)
            for title, value in [("Да", True), ("Нет", False), ("Не знаю", None)]:
                ctk.CTkButton(row, text=title, width=80, height=30, fg_color=PRIMARY if value is True else SOFT,
                              text_color="white" if value is True else TEXT,
                              state="disabled" if self._busy else "normal",
                              command=lambda v=value: self.answer_followup(v)).pack(side="left", padx=(0, 5))
        else:
            label("Все доступные уточнения пройдены." if session.facts else "Симптомы не распознаны. Измените описание.", color=MUTED)
        if session.asked:
            label("Ответов сохранено: " + str(len(session.asked)), color=MUTED)
            answers = {True: "Да", False: "Нет", None: "Не знаю"}
            for fact in session.asked:
                label(f"{FACT_LABELS.get(fact, fact)}: {answers[session.facts.get(fact)]}", color=MUTED)
        label("Пошаговая проверка", True)
        if not session.steps:
            label("План появится после распознавания симптомов.", color=MUTED)
            return
        label(DIAGNOSES.get(session.category, ""), color=MUTED)
        index = session.current_step()
        if session.status == "resolved":
            label("Вы отметили, что проверка помогла. Диагностика завершена.", color=("#24734F", "#76D7B0"))
        elif index is None:
            label("План закончился. Если проблема сохраняется, передайте отчёт специалисту.")
        else:
            label(f"Шаг {index + 1} из {len(session.steps)}", True)
            label(session.steps[index]["text"])
            for title, value in [("Проверил — не помогло", "not_helped"), ("Помогло", "helped"), ("Пропустить шаг", "skipped")]:
                ctk.CTkButton(panel, text=title, height=32, fg_color=PRIMARY if value == "helped" else SOFT,
                              text_color="white" if value == "helped" else TEXT,
                              state="disabled" if self._busy else "normal",
                              command=lambda v=value: self.advance_plan(v)).pack(fill="x", padx=10, pady=4)
        outcomes = {"not_helped": "Не помогло", "helped": "Помогло", "skipped": "Пропущено"}
        for i, step in enumerate(session.steps):
            if step["outcome"] != "pending":
                label(f"{i + 1}. {outcomes[step['outcome']]} — {step['text']}", color=MUTED)

    def answer_followup(self, value):
        if self._busy or not self.current_session:
            return
        self.current_session.respond(value)
        self._analyze_session(self.current_session)

    def advance_plan(self, value):
        if self._busy or not self.current_session:
            return
        self.current_session.record_step(value)
        self._persist_session(self.current_session)
        self._render_dialog()
        self.ai_status.configure(text="Результат проверки сохранён")

    def export_current_pdf(self):
        if self._busy:
            messagebox.showinfo("CoreSense", "Дождитесь завершения анализа.", parent=self)
            return
        if not self.current_session or not self.current_session.answer:
            messagebox.showinfo("CoreSense", "Сначала выполните диагностику или откройте её из истории.", parent=self)
            return
        path = filedialog.asksaveasfilename(parent=self, title="Сохранить отчёт CoreSense", defaultextension=".pdf",
                                           filetypes=[("PDF", "*.pdf")], initialfile="CoreSense-report.pdf")
        if not path:
            return
        try:
            from modules.pdf_report import export_session_pdf
            export_session_pdf(self.current_session, path)
        except Exception as error:
            messagebox.showerror("Экспорт CoreSense", str(error), parent=self)
        else:
            messagebox.showinfo("CoreSense", "PDF-отчёт сохранён.", parent=self)

    def history_page(self):
        self.clear_page()
        self._active_page = "history"
        self.heading("История диагностик", "Локальные записи сохраняют ответы, объяснения и прогресс проверок.")
        search = ctk.CTkFrame(self.content, fg_color="transparent")
        search.pack(fill="x", padx=32, pady=(0, 12))
        self.history_query = ctk.CTkEntry(search, placeholder_text="Поиск по описанию проблемы", width=450)
        self.history_query.pack(side="left")
        self.history_query.bind("<Return>", lambda event: self._refresh_history())
        ctk.CTkButton(search, text="Найти", width=100, command=self._refresh_history).pack(side="left", padx=8)
        self.history_list = ctk.CTkScrollableFrame(self.content, fg_color=SURFACE, corner_radius=14)
        self.history_list.pack(fill="both", expand=True, padx=32, pady=(0, 24))
        self._refresh_history()

    def _refresh_history(self):
        for widget in self.history_list.winfo_children():
            widget.destroy()
        records = self.store.list_sessions(self.history_query.get().strip())
        if not records:
            ctk.CTkLabel(self.history_list, text="Диагностик пока нет или по запросу ничего не найдено.", text_color=MUTED).pack(pady=30)
        for session_id, updated, question in records:
            row = ctk.CTkFrame(self.history_list, fg_color=SOFT, corner_radius=12)
            row.pack(fill="x", padx=8, pady=6)
            stamp = datetime.fromisoformat(updated).astimezone().strftime("%d.%m.%Y %H:%M")
            ctk.CTkLabel(row, text=stamp, text_color=MUTED, font=("Segoe UI", 11)).pack(anchor="w", padx=16, pady=(10, 2))
            ctk.CTkLabel(row, text=question[:160], text_color=TEXT, wraplength=650,
                         justify="left", font=("Segoe UI", 14)).pack(anchor="w", padx=16)
            ctk.CTkButton(row, text="Открыть и продолжить", width=190,
                          command=lambda sid=session_id: self.open_history_session(sid)).pack(anchor="w", padx=16, pady=10)

    def open_history_session(self, session_id):
        if self._busy:
            messagebox.showinfo("CoreSense", "Дождитесь завершения текущего анализа.", parent=self)
            return
        payload = self.store.load_session(session_id)
        if payload:
            self.current_session = DiagnosticSession.from_dict(payload)
            self.navigate("ИИ-помощник", self.ai_page)

    def settings_page(self):
        self.clear_page()
        self._active_page = "settings"
        self.heading("Настройки", "Оформление и анимации сохраняются между запусками.")
        card = ctk.CTkFrame(self.content, fg_color=SURFACE, corner_radius=16)
        card.pack(fill="x", padx=32, pady=8)
        ctk.CTkLabel(card, text="Тема приложения", text_color=TEXT, font=("Segoe UI", 18, "bold")).pack(anchor="w", padx=24, pady=(22, 12))
        themes = {"Тёмная": "dark", "Светлая": "light", "Как в системе": "system"}
        self.theme_choice = ctk.CTkSegmentedButton(card, values=list(themes),
                                                  selected_color=PRIMARY,
                                                  command=lambda label: self.change_theme(themes[label]))
        self.theme_choice.set(next(label for label, key in themes.items() if key == self.preferences["theme"]))
        self.theme_choice.pack(anchor="w", padx=24, pady=(0, 22))
        self.animation_value = ctk.BooleanVar(value=self.preferences["animations"])
        ctk.CTkSwitch(card, text="Анимации интерфейса", variable=self.animation_value,
                      command=self.change_animations, text_color=TEXT, progress_color=PRIMARY).pack(anchor="w", padx=24, pady=(0, 12))
        ctk.CTkLabel(card, text="При отключении ответ появляется сразу, а индикатор показывает только состояние работы.",
                     text_color=MUTED, wraplength=650, justify="left").pack(anchor="w", padx=24, pady=(0, 22))
        ctk.CTkLabel(self.content, text="Хранилище на этом компьютере:\n" + str(self.store.directory),
                     text_color=MUTED, justify="left", wraplength=700).pack(anchor="w", padx=36, pady=20)

    def change_theme(self, value):
        self.preferences["theme"] = value
        self.store.save_settings(self.preferences)
        ctk.set_appearance_mode(value)
        if hasattr(self, "theme_choice") and self.theme_choice.winfo_exists():
            self.theme_choice.set({"dark": "Тёмная", "light": "Светлая", "system": "Как в системе"}[value])

    def change_animations(self):
        self.preferences["animations"] = bool(self.animation_value.get())
        self.store.save_settings(self.preferences)

    def component_page(self):
        self.clear_page()
        self._active_page = "components"
        self.heading("Интерактивная схема ПК", "Выберите компонент на схеме или из списка. Справа появятся его свойства и связи.")
        body = ctk.CTkFrame(self.content, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=32, pady=(0, 24))
        body.grid_columnconfigure(0, weight=3)
        body.grid_columnconfigure(1, weight=2)
        body.grid_rowconfigure(0, weight=1)
        visual = ctk.CTkFrame(body, fg_color=SURFACE, corner_radius=14)
        visual.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        self.component_canvas = tk.Canvas(visual, highlightthickness=0, height=350, background="#151D2E")
        self.component_canvas.pack(fill="both", expand=True, padx=12, pady=12)
        self.component_selector = ctk.CTkOptionMenu(visual, values=["Процессор", "Оперативная память", "Видеокарта", "Жёсткий диск", "Блок питания", "Монитор"], command=self.select_component)
        self.component_selector.pack(fill="x", padx=12, pady=(0, 12))
        self.component_details = ctk.CTkTextbox(body, fg_color=SURFACE, text_color=TEXT, font=("Segoe UI", 14), wrap="word")
        self.component_details.grid(row=0, column=1, sticky="nsew")
        self._component_frames = FrameSystem()
        self._component_network = SemanticNetwork()
        self._selected_component = "Процессор"
        self._component_nodes = {
            "Процессор": (0.10, 0.13, 0.43, 0.31), "Оперативная память": (0.56, 0.13, 0.92, 0.31),
            "Видеокарта": (0.10, 0.43, 0.53, 0.60), "Жёсткий диск": (0.63, 0.43, 0.92, 0.60),
            "Блок питания": (0.10, 0.73, 0.53, 0.91), "Монитор": (0.63, 0.73, 0.92, 0.91),
        }
        self.component_canvas.bind("<Configure>", lambda event: self._draw_components())
        self.component_canvas.bind("<Motion>", self._hover_component)
        self.component_canvas.bind("<Leave>", lambda event: self.component_canvas.configure(cursor=""))
        self.select_component("Процессор")

    def _draw_components(self):
        canvas = self.component_canvas
        canvas.delete("all")
        light = ctk.get_appearance_mode() == "Light"
        canvas.configure(background="#FFFFFF" if light else "#151D2E")
        width, height = max(320, canvas.winfo_width()), max(280, canvas.winfo_height())
        canvas.create_rectangle(4, 4, width - 4, height - 4, outline="#8B79B5", width=2)
        for name, (x1, y1, x2, y2) in self._component_nodes.items():
            selected = name == self._selected_component
            tag = "node:" + name
            canvas.create_rectangle(x1*width, y1*height, x2*width, y2*height,
                                     fill="#7952E8" if selected else ("#ECE7F8" if light else "#29334C"),
                                     outline="#BCA5FF" if selected else "#7C8BA5", width=2, tags=(tag,))
            canvas.create_text((x1+x2)/2*width, (y1+y2)/2*height, text=name,
                                width=(x2-x1)*width-10, fill="white" if selected else ("#17233B" if light else "#E5ECF8"),
                                font=("Segoe UI", 11), tags=(tag,))
            canvas.tag_bind(tag, "<Button-1>", lambda event, component=name: self.select_component(component))
        canvas.create_text(width/2, height*0.365, text="Компоненты компьютера", fill="#7787A4", font=("Segoe UI", 10))

    def _hover_component(self, event):
        items = self.component_canvas.find_withtag("current")
        self.component_canvas.configure(cursor="hand2" if items and any(tag.startswith("node:") for tag in self.component_canvas.gettags(items[0])) else "")

    def select_component(self, name):
        self._selected_component = name
        self.component_selector.set(name)
        properties = self._component_frames.get_properties(name) if name in self._component_frames.frames else {}
        relations = self._component_network.find_related(name)
        text = name.upper() + "\n\nСВОЙСТВА\n"
        text += "\n".join(f"{key}: {value}" for key, value in properties.items()) or "Отдельный фрейм пока не задан."
        text += "\n\nСВЯЗИ\n"
        text += "\n".join(f"{name} → {item['relation']} → {item['object']}" for item in relations) or "Исходящих связей пока нет."
        self.component_details.configure(state="normal")
        self.component_details.delete("1.0", "end")
        self.component_details.insert("1.0", text)
        self.component_details.configure(state="disabled")
        self._draw_components()
