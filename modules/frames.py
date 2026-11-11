
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
FRAMES_FILE = BASE_DIR / "knowledge" / "frames.json"


class FrameSystem:
    def __init__(self):
        self.load()

    def load(self):
        with open(FRAMES_FILE, "r", encoding="utf-8") as file:
            self.frames = json.load(file)

    def save(self):
        with open(FRAMES_FILE, "w", encoding="utf-8") as file:
            json.dump(
                self.frames,
                file,
                ensure_ascii=False,
                indent=4
            )

    def list_frames(self):
        return list(self.frames.keys())

    def get_properties(self, name, visited=None):
        if name not in self.frames:
            raise KeyError(f"Фрейм не найден: {name}")

        if visited is None:
            visited = set()

        if name in visited:
            raise ValueError("Обнаружен цикл наследования")

        visited.add(name)

        frame = self.frames[name]
        properties = {}

        parent = frame.get("parent")

        if parent:
            properties.update(
                self.get_properties(parent, visited)
            )

        properties.update(frame.get("properties", {}))
        visited.remove(name)

        return properties

    def search(self, text):
        text = text.lower()
        return [
            name for name in self.frames
            if text in name.lower()
        ]

    def change_property(self, name, property_name, value):
        if name not in self.frames:
            raise KeyError("Фрейм не найден")

        self.frames[name]["properties"][property_name] = value
        self.save()

    def add_frame(self, name, parent=None):
        if name in self.frames:
            raise ValueError("Такой фрейм уже существует")

        if parent and parent not in self.frames:
            raise ValueError("Родительский фрейм не найден")

        self.frames[name] = {
            "parent": parent,
            "properties": {}
        }
        self.save()


if __name__ == "__main__":
    system = FrameSystem()

    print("ВСЕ ФРЕЙМЫ:")
    print(system.list_frames())

    print("\nПОИСК:")
    print(system.search("ПК"))

    print("\nСВОЙСТВА НОУТБУКА:")
    for key, value in system.get_properties("Ноутбук").items():
        print(f"{key}: {value}")

    print("\nДОБАВЛЕНИЕ НОВОГО ФРЕЙМА:")
    if "Игровой ПК" not in system.frames:
        system.add_frame("Игровой ПК", "Настольный ПК")

    system.change_property(
        "Игровой ПК",
        "назначение",
        "Игры и графика"
    )

    print(system.get_properties("Игровой ПК"))
