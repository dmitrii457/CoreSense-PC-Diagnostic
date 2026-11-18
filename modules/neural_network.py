
import pandas as pd
import joblib
from pathlib import Path

from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report
from modules.evaluation import split_dataset, save_report

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = BASE_DIR / "data" / "pc_problems.csv"
MODEL_FILE = BASE_DIR / "models" / "neural_network.pkl"


def train_neural_network():
    data = pd.read_csv(DATA_FILE)

    X = data.drop(columns=["diagnosis"])
    y = data["diagnosis"]

    X_train, X_test, y_train, y_test = split_dataset(data)

    model = Pipeline([
        ("scaler", StandardScaler()),
        ("neural_network", MLPClassifier(
            hidden_layer_sizes=(32, 16),
            activation="relu",
            solver="adam",
            max_iter=2000,
            random_state=42
        ))
    ])

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    accuracy = accuracy_score(y_test, predictions)

    print("НЕЙРОННАЯ СЕТЬ CORESENSE")
    print(f"Точность: {accuracy * 100:.2f}%")
    print("\nОтчёт классификации:")
    print(classification_report(y_test, predictions))
    save_report("neural_network", model, X_train, X_test, y_train, y_test)

    MODEL_FILE.parent.mkdir(exist_ok=True)
    joblib.dump(model, MODEL_FILE)

    print("\nНейросеть сохранена:", MODEL_FILE)


if __name__ == "__main__":
    train_neural_network()
