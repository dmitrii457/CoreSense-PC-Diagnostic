
import pandas as pd
import joblib
from pathlib import Path

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from modules.evaluation import split_dataset, save_report

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = BASE_DIR / "data" / "pc_problems.csv"
MODEL_FILE = BASE_DIR / "models" / "classifier.pkl"


def train_classifier():
    data = pd.read_csv(DATA_FILE)

    X = data.drop(columns=["diagnosis"])
    y = data["diagnosis"]

    X_train, X_test, y_train, y_test = split_dataset(data)

    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42
    )

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    accuracy = accuracy_score(y_test, predictions)

    print("КЛАССИФИКАТОР FIXAI")
    print(f"Точность: {accuracy * 100:.2f}%")
    print("\nОтчёт классификации:")
    print(classification_report(y_test, predictions))
    save_report("classifier", model, X_train, X_test, y_train, y_test)

    MODEL_FILE.parent.mkdir(exist_ok=True)
    joblib.dump(model, MODEL_FILE)

    print("\nМодель сохранена:", MODEL_FILE)


if __name__ == "__main__":
    train_classifier()
