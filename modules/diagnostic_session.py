"""Stateful follow-up questions and user-controlled troubleshooting steps."""
from datetime import datetime, timezone
from uuid import uuid4

FOLLOWUPS = [
    ("computer_not_starting", "no_power_indicator", "Индикатор питания не горит?", False),
    ("computer_not_starting", "fans_not_spinning", "Вентиляторы не вращаются?", False),
    ("no_display", "monitor_power_on", "Монитор включён?", False),
    ("internet_not_working", "computer_not_starting", "Компьютер включается?", True),
    ("computer_slow", "high_cpu_usage", "В диспетчере задач видна высокая загрузка процессора?", False),
    ("overheating", "random_restart", "Компьютер самопроизвольно перезагружается?", False),
]

PLANS = {
    "power_problem": [
        "Проверьте питание розетки, подключив заведомо исправное устройство.",
        "Проверьте подключение кабеля питания и внешний переключатель блока питания, если он есть.",
        "Отсоедините внешние USB-устройства и повторите попытку включения.",
        "Если питания всё ещё нет, обратитесь в сервис. Не вскрывайте блок питания самостоятельно.",
    ],
    "video_problem": [
        "Проверьте питание монитора и выбранный на нём вход HDMI или DisplayPort.",
        "Проверьте подключение видеокабеля с обеих сторон.",
        "Если доступен исправный кабель или другой монитор, проверьте изображение с ним.",
        "Если изображения нет с исправным монитором и кабелем, обратитесь в сервис.",
    ],
    "performance_problem": [
        "Откройте диспетчер задач и посмотрите, какой процесс нагружает CPU, память или диск.",
        "Сохраните работу, закройте ненужные программы и проверьте скорость снова.",
        "Проверьте свободное место на системном диске и список автозагрузки.",
        "Если замедление сохраняется, передайте в сервис список процессов и описание проблемы.",
    ],
    "network_problem": [
        "Проверьте Wi-Fi или Ethernet и убедитесь, что режим полёта выключен.",
        "Проверьте доступ к интернету на другом устройстве в той же сети.",
        "Сохраните работу, перезапустите компьютер и повторно подключитесь к сети.",
        "Если сеть не работает на всех устройствах, проверьте состояние услуг у провайдера.",
    ],
    "audio_problem": [
        "Проверьте громкость и отключение звука в системе и приложении.",
        "Выберите нужное устройство вывода в настройках звука.",
        "Проверьте подключение наушников или колонок, попробуйте другое устройство.",
        "Если проблема сохраняется, проверьте состояние аудиоустройства и драйвера.",
    ],
    "cooling_problem": [
        "При сильном перегреве сохраните работу, выключите компьютер и дайте ему остыть.",
        "Убедитесь, что вентиляционные отверстия снаружи не перекрыты.",
        "После остывания проверьте температуру и нагрузку с помощью установленной утилиты.",
        "Если перегрев повторяется, обратитесь в сервис для проверки охлаждения.",
    ],
}

FACT_LABELS = {
    "computer_not_starting": "Компьютер не включается", "no_power_indicator": "Индикатор питания не горит",
    "fans_not_spinning": "Вентиляторы не вращаются", "no_display": "Нет изображения",
    "monitor_power_on": "Монитор включён", "computer_slow": "Компьютер тормозит",
    "high_cpu_usage": "Высокая загрузка CPU", "internet_not_working": "Не работает интернет",
    "no_sound": "Нет звука", "overheating": "Перегрев", "random_restart": "Самопроизвольная перезагрузка",
}


class DiagnosticSession:
    def __init__(self, question, facts):
        self.id = str(uuid4())
        self.created = datetime.now(timezone.utc).isoformat()
        self.question = question
        self.facts = dict(facts)
        self.asked = []
        self.answer = ""
        self.category = None
        self.steps = []
        self.status = "active"

    def next_question(self):
        for trigger, fact, prompt, inverse in FOLLOWUPS:
            if self.facts.get(trigger) is True and fact not in self.asked and self.facts.get(fact) is None:
                return {"fact": fact, "prompt": prompt, "inverse": inverse}
        return None

    def respond(self, value):
        question = self.next_question()
        if question is None:
            raise ValueError("Нет текущего уточняющего вопроса")
        if value is not None and not isinstance(value, bool):
            raise ValueError("Ответ должен быть Да, Нет или Не знаю")
        self.facts[question["fact"]] = (not value if question["inverse"] else value) if value is not None else None
        self.asked.append(question["fact"])

    def set_plan(self, category):
        if category == self.category and self.steps:
            return
        self.category = category
        self.steps = [{"text": text, "outcome": "pending"} for text in PLANS.get(category, [])]
        self.status = "active"

    def current_step(self):
        if self.status != "active":
            return None
        return next((i for i, step in enumerate(self.steps) if step["outcome"] == "pending"), None)

    def record_step(self, outcome):
        if outcome not in {"helped", "not_helped", "skipped"}:
            raise ValueError("Неизвестный результат проверки")
        index = self.current_step()
        if index is None:
            raise ValueError("Нет активного шага")
        self.steps[index]["outcome"] = outcome
        if outcome == "helped":
            self.status = "resolved"
        elif self.current_step() is None:
            self.status = "exhausted"

    def report_text(self):
        labels = {True: "Да", False: "Нет", None: "Неизвестно"}
        text = f"ЗАПРОС\n{self.question}\n\nУТОЧНЁННЫЕ ФАКТЫ\n"
        text += "\n".join(f"{FACT_LABELS.get(k, k)}: {labels[v]}" for k, v in self.facts.items())
        text += f"\n\n{self.answer}\n\nПЛАН ПРОВЕРКИ\n"
        outcomes = {"pending": "Не выполнено", "helped": "Помогло", "not_helped": "Не помогло", "skipped": "Пропущено"}
        text += "\n".join(f"{i + 1}. {step['text']} [{outcomes[step['outcome']]}]" for i, step in enumerate(self.steps))
        text += "\n\nСтатус: " + {"active": "В процессе", "resolved": "Пользователь сообщил, что проблема устранена", "exhausted": "План завершён, проблема не устранена"}[self.status]
        return text

    def to_dict(self):
        return {key: getattr(self, key) for key in ("id", "created", "question", "facts", "asked", "answer", "category", "steps", "status")}

    @classmethod
    def from_dict(cls, payload):
        session = cls(payload["question"], payload["facts"])
        for key in session.to_dict():
            if key in payload:
                setattr(session, key, payload[key])
        return session
