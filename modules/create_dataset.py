
import csv
import random
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "pc_problems.csv"

def create_dataset():
    random.seed(42)

    features = [
        "no_power",
        "no_display",
        "slow_pc",
        "high_cpu",
        "no_internet",
        "no_sound",
        "overheating",
        "random_restart"
    ]

    # Прототипы симптомов для учебного датасета
    prototypes = {
        "power_problem": [1, 0, 0, 0, 0, 0, 0, 0],
        "video_problem": [0, 1, 0, 0, 0, 0, 0, 0],
        "performance_problem": [0, 0, 1, 1, 0, 0, 0, 0],
        "network_problem": [0, 0, 0, 0, 1, 0, 0, 0],
        "audio_problem": [0, 0, 0, 0, 0, 1, 0, 0],
        "cooling_problem": [0, 0, 0, 1, 0, 0, 1, 1]
    }

    rows = []

    for label, prototype in prototypes.items():
        for _ in range(100):
            sample = prototype.copy()

            # Добавляем небольшие случайные изменения
            # для разнообразия учебных примеров
            for i in range(len(sample)):
                if random.random() < 0.08:
                    sample[i] = 1 - sample[i]

            rows.append(sample + [label])

    random.shuffle(rows)

    DATA_FILE.parent.mkdir(exist_ok=True)

    with open(DATA_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(features + ["diagnosis"])
        writer.writerows(rows)

    print("Датасет успешно создан!")
    print("Количество записей:", len(rows))
    print("Количество классов:", len(prototypes))
    print("Файл:", DATA_FILE)


if __name__ == "__main__":
    create_dataset()
