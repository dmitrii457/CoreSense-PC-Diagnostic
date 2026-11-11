
from pathlib import Path
import joblib
import re
import pandas as pd
from modules.frames import FrameSystem
from modules.semantic_network import SemanticNetwork

from modules.production import ProductionSystem

BASE_DIR = Path(__file__).resolve().parent.parent

FEATURES = [
    "no_power",
    "no_display",
    "slow_pc",
    "high_cpu",
    "no_internet",
    "no_sound",
    "overheating",
    "random_restart"
]

KEYWORDS = {
    "no_power": [
        "не включается", "нет питания", "не запускается"
    ],
    "no_display": [
        "нет изображения", "черный экран", "чёрный экран",
        "нет картинки"
    ],
    "slow_pc": [
        "тормозит", "лагает", "медленно работает"
    ],
    "high_cpu": [
        "загрузка процессора", "процессор загружен"
    ],
    "no_internet": [
        "нет интернета", "интернет не работает",
        "не работает интернет"
    ],
    "no_sound": [
        "нет звука", "звук не работает"
    ],
    "overheating": [
        "перегревается", "перегрев", "сильно греется"
    ],
    "random_restart": [
        "перезагружается", "сам перезапускается"
    ]
}

DIAGNOSES = {
    "power_problem": "Возможная проблема с питанием",
    "video_problem": "Возможная проблема с видеосистемой",
    "performance_problem": "Возможная проблема с производительностью",
    "network_problem": "Возможная проблема с сетью",
    "audio_problem": "Возможная проблема со звуком",
    "cooling_problem": "Возможная проблема с охлаждением"
}

RECOMMENDATIONS = {
    "power_problem": "Проверьте розетку и кабель питания.",
    "video_problem": "Проверьте монитор и видеокабель.",
    "performance_problem": "Проверьте загрузку процессора и памяти.",
    "network_problem": "Проверьте сетевое подключение.",
    "audio_problem": "Проверьте устройство вывода звука.",
    "cooling_problem": "Проверьте вентиляцию и температуру ПК."
}


class AIAssistant:
    def __init__(self):
        self.production = ProductionSystem()

        model_dir = BASE_DIR / "models"

        self.classifier = self._load_model(model_dir / "classifier.pkl")
        self.neural_network = self._load_model(model_dir / "neural_network.pkl")
        self.frames = FrameSystem()
        self.network = SemanticNetwork()

    @staticmethod
    def _load_model(path):
        try:
            return joblib.load(path)
        except (FileNotFoundError, ValueError, ImportError, EOFError):
            return None

    def analyze_text(self, text):
        text = text.lower().strip()
        facts = self.extract_facts(text)
        return [int(feature in facts) for feature in FEATURES]

    def extract_facts(self, text):
        text = text.lower().replace("ё", "е")
        found = {}
        for feature, keywords in KEYWORDS.items():
            for keyword in keywords:
                keyword = keyword.replace("ё", "е")
                for match in re.finditer(r"(?<!\w)" + re.escape(keyword) + r"(?!\w)", text):
                    prefix = text[max(0, match.start() - 30):match.start()]
                    if not re.search(r"(?:не|нет|без|перестал|перестала)\s+$", prefix):
                        found[feature] = True
        return found

    def collect_facts(self, question):
        mapping = dict(zip(FEATURES, ["computer_not_starting", "no_display",
            "computer_slow", "high_cpu_usage", "internet_not_working",
            "no_sound", "overheating", "random_restart"]))
        facts = {mapping[name]: True for name in self.extract_facts(question)}
        normalized = question.lower().replace("ё", "е")
        for phrase, name, value in [
            ("индикатор не горит", "no_power_indicator", True),
            ("индикатор питания не горит", "no_power_indicator", True),
            ("вентиляторы не вращаются", "fans_not_spinning", True),
            ("монитор включен", "monitor_power_on", True),
            ("компьютер включается", "computer_not_starting", False),
            ("индикатор горит", "no_power_indicator", False),
            ("индикатор питания горит", "no_power_indicator", False),
            ("вентиляторы вращаются", "fans_not_spinning", False),
            ("монитор выключен", "monitor_power_on", False),
        ]:
            if phrase in normalized:
                facts[name] = value
        return facts

    def ask(self, question, confirmed_facts=None):
        if not question.strip():
            return "Введите описание проблемы."
        facts = self.collect_facts(question)
        if confirmed_facts:
            facts.update(confirmed_facts)
        mapping = ["computer_not_starting", "no_display", "computer_slow", "high_cpu_usage",
                   "internet_not_working", "no_sound", "overheating", "random_restart"]
        features = [int(facts.get(name) is True) for name in mapping]
        if not any(features):
            return "Не удалось определить симптомы.\nПопробуйте описать проблему подробнее."
        _, history = self.production.forward_chain(facts)
        sample = pd.DataFrame([features], columns=FEATURES)
        result = "АНАЛИЗ FIXAI\n\nРаспознанные симптомы:\n"
        result += "\n".join("• " + KEYWORDS[name][0] for name, value in zip(FEATURES, features) if value)
        result += "\n\nПРОГНОЗЫ МОДЕЛЕЙ\n"
        predictions = []
        for title, model in [("Random Forest", self.classifier), ("Нейросеть", self.neural_network)]:
            if model is None:
                result += f"{title}: модель отсутствует. Выполните обучение.\n"
                continue
            prediction = model.predict(sample)[0]
            predictions.append(prediction)
            result += f"{title}: {DIAGNOSES[prediction]}\n"
        if len(predictions) == 2 and predictions[0] != predictions[1]:
            result += "Модели расходятся. Нужны дополнительные симптомы.\n"

        if history:
            result += "\nОБЪЯСНЕНИЕ ПО ПРАВИЛАМ\n"

            for step in history:
                result += (
                    f"{step['rule']}: "
                    f"{step['explanation']}\n"
                )

        diagnoses = {step['conclusion'].removeprefix('possible_') for step in history
                     if step['conclusion'].startswith('possible_')}
        if not diagnoses:
            diagnoses = set(predictions)
        result += "\nЧТО ПРОВЕРИТЬ\n"
        for diagnosis in sorted(diagnoses):
            if diagnosis in RECOMMENDATIONS:
                result += "• " + RECOMMENDATIONS[diagnosis] + "\n"
        if not history:
            result += "Правила пока не подтвердили причину. Уточните состояние индикатора питания и монитора.\n"
        component_map = {"power_problem": "Блок питания", "video_problem": "Видеокарта",
                         "performance_problem": "Жёсткий диск", "cooling_problem": "Процессор"}
        components = sorted({component_map[d] for d in diagnoses if d in component_map})
        if components:
            result += "\nСВЯЗИ В БАЗЕ ЗНАНИЙ\n"
        for component in components:
            links = self.network.find_related(component)
            for link in links:
                result += f"{component} → {link['relation']} → {link['object']}\n"
            if component in self.frames.frames:
                props = self.frames.get_properties(component)
                result += f"Назначение: {props.get('назначение', 'не указано')}\n"

        result += (
            "\nРезультат предварительный и не является "
            "подтверждённой диагностикой."
        )

        return result

    def plan_category(self, question, confirmed_facts=None):
        facts = self.collect_facts(question)
        facts.update(confirmed_facts or {})
        _, history = self.production.forward_chain(facts)
        known = {step["conclusion"].removeprefix("possible_") for step in history
                 if step["conclusion"].startswith("possible_")}
        for category in ["cooling_problem", "power_problem", "video_problem", "network_problem", "audio_problem", "performance_problem"]:
            if category in known:
                return category
        # A plan starts from reported symptoms, never from an unsupported model guess.
        for fact, category in [("overheating", "cooling_problem"), ("computer_not_starting", "power_problem"),
                               ("no_display", "video_problem"), ("internet_not_working", "network_problem"),
                               ("no_sound", "audio_problem"), ("computer_slow", "performance_problem"),
                               ("high_cpu_usage", "performance_problem")]:
            if facts.get(fact) is True:
                return category
        return None


if __name__ == "__main__":
    assistant = AIAssistant()

    print(assistant.ask(
        "Компьютер тормозит и процессор загружен"
    ))
