"""Reproducible holdout: identical symptom vectors never cross the split."""
import hashlib
import json
from pathlib import Path
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

BASE_DIR = Path(__file__).resolve().parent.parent


def split_dataset(data):
    X = data.drop(columns=["diagnosis"])
    y = data["diagnosis"]
    groups = X.astype(str).agg("".join, axis=1)
    splitter = GroupShuffleSplit(n_splits=1, test_size=0.25, random_state=42)
    train, test = next(splitter.split(X, y, groups))
    return X.iloc[train], X.iloc[test], y.iloc[train], y.iloc[test]


def save_report(name, model, X_train, X_test, y_train, y_test):
    prediction = model.predict(X_test)
    labels = sorted(set(y_train) | set(y_test))
    report = {
        "model": name,
        "dataset_sha256": hashlib.sha256((BASE_DIR / "data/pc_problems.csv").read_bytes()).hexdigest(),
        "split": "GroupShuffleSplit by symptom vector, seed=42, test_size=0.25",
        "train_rows": len(X_train), "test_rows": len(X_test),
        "overlapping_feature_vectors": len(set(map(tuple, X_train.values)) & set(map(tuple, X_test.values))),
        "accuracy": accuracy_score(y_test, prediction),
        "classification_report": classification_report(y_test, prediction, labels=labels, output_dict=True, zero_division=0),
        "confusion_matrix_labels": labels,
        "confusion_matrix": confusion_matrix(y_test, prediction, labels=labels).tolist(),
        "limitation": "Synthetic classroom data. Does not establish real-world diagnostic accuracy."
    }
    folder = BASE_DIR / "reports"
    folder.mkdir(exist_ok=True)
    (folder / f"{name}.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report
