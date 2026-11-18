
import customtkinter as ctk
from ui_components import MotionButton, SurfaceFrame
import joblib
import pandas as pd
import json

from pathlib import Path
from tkinter import messagebox

from modules.frames import FrameSystem
from modules.semantic_network import SemanticNetwork
from modules.ai_assistant import FEATURES, DIAGNOSES

BASE_DIR = Path(__file__).resolve().parent

PURPLE = "#8057E6"
PANEL = ('#FFFFFF', '#131927')


class ExtraPages:

    def frames_page(self):
        self.clear_page()
        self.heading(
            "Фреймовая модель",
            "Просмотр, поиск и изменение свойств объектов"
        )

        self.frame_system = FrameSystem()

        search_row = SurfaceFrame(self.content, fg_color="transparent")
        search_row.pack(fill="x", padx=35, pady=(0, 6))
        self.frame_search = ctk.CTkEntry(search_row, placeholder_text="Поиск фрейма по названию", width=350)
        self.frame_search.pack(side="left")
        MotionButton(search_row, text="Найти", width=85, command=self.search_frames).pack(side="left", padx=8)

        self.frame_selector = ctk.CTkOptionMenu(
            self.content,
            values=self.frame_system.list_frames(),
            width=350,
            height=42
        )
        self.frame_selector.pack(
            anchor="w", padx=35, pady=10
        )

        MotionButton(
            self.content,
            text="Показать свойства",
            command=self.show_frame,
            fg_color=PURPLE
        ).pack(anchor="w", padx=35, pady=5)

        self.frame_result = ctk.CTkTextbox(
            self.content,
            height=180,
            fg_color=PANEL
        )
        self.frame_result.pack(
            fill="x", padx=35, pady=15
        )

        ctk.CTkLabel(
            self.content,
            text="Изменить или добавить свойство"
        ).pack(anchor="w", padx=35)

        self.property_name = ctk.CTkEntry(
            self.content,
            placeholder_text="Название свойства",
            width=350
        )
        self.property_name.pack(
            anchor="w", padx=35, pady=5
        )

        self.property_value = ctk.CTkEntry(
            self.content,
            placeholder_text="Новое значение",
            width=350
        )
        self.property_value.pack(
            anchor="w", padx=35, pady=5
        )

        MotionButton(
            self.content,
            text="Сохранить свойство",
            command=self.save_frame_property,
            fg_color=PURPLE
        ).pack(anchor="w", padx=35, pady=10)

        self.show_frame()

    def search_frames(self):
        matches = self.frame_system.search(self.frame_search.get().strip())
        if not matches:
            self.frame_result.delete("1.0", "end")
            self.frame_result.insert("end", "Фреймы не найдены.")
            return
        self.frame_selector.configure(values=matches)
        self.frame_selector.set(matches[0])
        self.show_frame()

    def show_frame(self):
        name = self.frame_selector.get()
        properties = self.frame_system.get_properties(name)

        self.frame_result.delete("1.0", "end")
        self.frame_result.insert(
            "end", f"ФРЕЙМ: {name}\n\n"
        )

        for key, value in properties.items():
            self.frame_result.insert(
                "end", f"{key}: {value}\n"
            )

    def save_frame_property(self):
        name = self.frame_selector.get()
        key = self.property_name.get().strip()
        value = self.property_value.get().strip()

        if not key or not value:
            messagebox.showwarning(
                "CoreSense", "Заполните оба поля"
            )
            return

        self.frame_system.change_property(
            name, key, value
        )

        self.show_frame()

        messagebox.showinfo(
            "CoreSense", "Свойство успешно сохранено"
        )

    def semantic_page(self):
        self.clear_page()
        self.heading(
            "Семантическая сеть",
            "Поиск связей между объектами компьютера"
        )

        self.semantic_network = SemanticNetwork()

        nodes = list(
            self.semantic_network.graph.nodes
        )

        self.node_selector = ctk.CTkOptionMenu(
            self.content,
            values=nodes,
            width=350,
            height=42
        )
        self.node_selector.pack(
            anchor="w", padx=35, pady=10
        )

        self.path_target = ctk.CTkOptionMenu(self.content, values=nodes, width=350, height=36)
        self.path_target.pack(anchor="w", padx=35, pady=4)
        MotionButton(self.content, text="Найти путь между выбранными узлами",
                      command=self.find_semantic_path, fg_color=('#7656AE', '#453379')).pack(anchor="w", padx=35, pady=4)

        MotionButton(
            self.content,
            text="Найти связанные объекты",
            command=self.find_connections,
            fg_color=PURPLE
        ).pack(anchor="w", padx=35, pady=10)

        MotionButton(
            self.content,
            text="Показать граф",
            command=self.show_graph,
            fg_color=('#7656AE', '#453379')
        ).pack(anchor="w", padx=35, pady=5)

        self.semantic_result = ctk.CTkTextbox(
            self.content,
            fg_color=PANEL
        )
        self.semantic_result.pack(
            fill="both",
            expand=True,
            padx=35,
            pady=20
        )

    def find_connections(self):
        node = self.node_selector.get()

        connections = (
            self.semantic_network.find_related(node)
        )

        self.semantic_result.delete("1.0", "end")

        if not connections:
            self.semantic_result.insert(
                "end", "Исходящие связи не найдены."
            )
            return

        for item in connections:
            self.semantic_result.insert(
                "end",
                f"{node} → {item['relation']} "
                f"→ {item['object']}\n\n"
            )

    def show_graph(self):
        self.semantic_network.show()

    def find_semantic_path(self):
        path = self.semantic_network.search_path(self.node_selector.get(), self.path_target.get())
        self.semantic_result.delete("1.0", "end")
        self.semantic_result.insert("end", " → ".join(path) if path else "Направленный путь не найден.")

    def ml_page(self):
        self.clear_page()
        self.heading(
            "Машинное обучение",
            "Сравнение классификатора и нейросети"
        )

        scores = []
        for name, title in [("classifier", "Random Forest"), ("neural_network", "MLP")]:
            report_path = BASE_DIR / "reports" / f"{name}.json"
            if report_path.exists():
                report = json.loads(report_path.read_text(encoding="utf-8"))
                scores.append(f"{title}: {report['accuracy']:.2%}")
        ctk.CTkLabel(self.content, text="  •  ".join(scores) + "\nТест на синтетических данных без общих векторов с обучением.",
                     text_color=('#53627B', '#99A6C1'), font=("Segoe UI", 12)).pack(anchor="w", padx=35, pady=(0, 6))

        self.classifier = self.ai_assistant.classifier
        self.neural_network = self.ai_assistant.neural_network

        self.ml_variables = {}

        descriptions = {
            "no_power": "Нет питания",
            "no_display": "Нет изображения",
            "slow_pc": "Компьютер тормозит",
            "high_cpu": "Высокая загрузка процессора",
            "no_internet": "Нет интернета",
            "no_sound": "Нет звука",
            "overheating": "Перегрев",
            "random_restart": "Самопроизвольная перезагрузка"
        }

        scroll = ctk.CTkScrollableFrame(
            self.content,
            height=230,
            fg_color=PANEL
        )
        scroll.pack(fill="x", padx=35, pady=10)

        for feature in FEATURES:
            variable = ctk.BooleanVar(value=False)
            self.ml_variables[feature] = variable

            ctk.CTkCheckBox(
                scroll,
                text=descriptions[feature],
                variable=variable,
                fg_color=PURPLE
            ).pack(anchor="w", padx=15, pady=8)

        MotionButton(
            self.content,
            text="Сравнить модели",
            command=self.compare_models,
            fg_color=PURPLE,
            height=45
        ).pack(anchor="w", padx=35, pady=10)

        self.ml_result = ctk.CTkTextbox(
            self.content,
            fg_color=PANEL,
            font=("Segoe UI", 15)
        )
        self.ml_result.pack(
            fill="both",
            expand=True,
            padx=35,
            pady=15
        )

    def compare_models(self):
        features = [
            int(self.ml_variables[name].get())
            for name in FEATURES
        ]

        self.ml_result.delete("1.0", "end")

        if not any(features):
            self.ml_result.insert(
                "end",
                "Выберите хотя бы один симптом."
            )
            return

        if self.classifier is None or self.neural_network is None:
            self.ml_result.insert("end", "Сначала обучите модели по инструкции в README.")
            return
        sample = pd.DataFrame([features], columns=FEATURES)
        forest = self.classifier.predict(sample)[0]

        neural = self.neural_network.predict(sample)[0]

        self.ml_result.insert(
            "end",
            "РЕЗУЛЬТАТЫ МОДЕЛЕЙ\n\n"
            f"Random Forest:\n{DIAGNOSES[forest]}\n\n"
            f"Нейронная сеть:\n{DIAGNOSES[neural]}\n\n"
            "Совпадение прогнозов: "
            + ("Да" if forest == neural else "Нет")
            + "\n\nРезультаты являются учебными прогнозами."
        )
