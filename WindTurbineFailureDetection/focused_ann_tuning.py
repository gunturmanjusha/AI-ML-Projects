"""Focused, reproducible ANN validation search for the canonical turbine split.

This script deliberately does not touch the test partition.  It evaluates five
pre-specified architectures on the existing timestamp-grouped chronological
train/validation split, writes every attempted configuration and its actual
validation metrics, and records the validation-only winner.
"""
import json
import os
import random

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score
from sklearn.preprocessing import StandardScaler
from tensorflow.keras import Sequential
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.layers import BatchNormalization, Dense, Dropout, Input
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.regularizers import l2

SEED = 42


CONFIGURATIONS = [
    {
        "id": "baseline_reproduction",
        "description": "Recorded baseline architecture reproduced under the focused fixed-seed protocol.",
        "layers": [48, 16], "dropout": [0.20], "batch_normalization": False,
        "learning_rate": 0.001, "l2": 0.0, "epochs": 15, "patience": 2,
    },
    {
        "id": "previous_regularized",
        "description": "Previously selected regularized ANN configuration.",
        "layers": [64, 24], "dropout": [0.30, 0.15], "batch_normalization": True,
        "learning_rate": 0.001, "l2": 0.0, "epochs": 20, "patience": 3,
    },
    {
        "id": "wider_l2",
        "description": "Wider network with L2 regularization and a lower learning rate.",
        "layers": [96, 32], "dropout": [0.30, 0.15], "batch_normalization": True,
        "learning_rate": 0.0007, "l2": 0.0001, "epochs": 20, "patience": 3,
    },
    {
        "id": "higher_dropout_l2",
        "description": "Previous width with stronger dropout and L2 regularization.",
        "layers": [64, 24], "dropout": [0.40, 0.20], "batch_normalization": True,
        "learning_rate": 0.001, "l2": 0.0001, "epochs": 20, "patience": 3,
    },
    {
        "id": "compact_regularized",
        "description": "Smaller regularized network to test a lower-capacity alternative.",
        "layers": [48, 16], "dropout": [0.25, 0.10], "batch_normalization": True,
        "learning_rate": 0.0007, "l2": 0.0001, "epochs": 20, "patience": 3,
    },
]


def seed_everything():
    random.seed(SEED)
    np.random.seed(SEED)
    tf.keras.utils.set_random_seed(SEED)


def score(model, x, y):
    probability = model.predict(x, verbose=0).ravel()
    prediction = (probability >= 0.5).astype(int)
    matrix = confusion_matrix(y, prediction, labels=[0, 1])
    return {
        "accuracy": float(accuracy_score(y, prediction)),
        "precision": float(precision_score(y, prediction, zero_division=0)),
        "recall": float(recall_score(y, prediction, zero_division=0)),
        "f1": float(f1_score(y, prediction, zero_division=0)),
        "tn": int(matrix[0, 0]), "fp": int(matrix[0, 1]),
        "fn": int(matrix[1, 0]), "tp": int(matrix[1, 1]),
    }


def make_model(config, n_features):
    penalty = l2(config["l2"]) if config["l2"] else None
    model = Sequential([Input(shape=(n_features,))])
    for index, width in enumerate(config["layers"]):
        model.add(Dense(width, activation="relu", kernel_regularizer=penalty))
        if index == 0 and config["batch_normalization"]:
            model.add(BatchNormalization())
        if index < len(config["dropout"]):
            model.add(Dropout(config["dropout"][index]))
    model.add(Dense(1, activation="sigmoid"))
    model.compile(optimizer=Adam(learning_rate=config["learning_rate"]), loss="binary_crossentropy")
    return model


def main():
    selected_ids = set(filter(None, os.environ.get("ANN_CONFIG_IDS", "").split(",")))
    configurations = [c for c in CONFIGURATIONS if not selected_ids or c["id"] in selected_ids]
    data = pd.read_csv("wind_turbine_detection.csv")
    data["timestamp"] = pd.to_datetime(data["timestamp"], format="%m/%d/%Y %H:%M")
    data = data.sort_values(["timestamp", "turbine_id"]).reset_index(drop=True)
    data["hour_sin"] = np.sin(2 * np.pi * data.timestamp.dt.hour / 24)
    data["hour_cos"] = np.cos(2 * np.pi * data.timestamp.dt.hour / 24)
    data["dow_sin"] = np.sin(2 * np.pi * data.timestamp.dt.dayofweek / 7)
    data["dow_cos"] = np.cos(2 * np.pi * data.timestamp.dt.dayofweek / 7)
    data["power_utilisation"] = data.power_output_kW / data.rated_power_kW
    data["gearbox_temp_rise_C"] = data.gearbox_bearing_temp_C - data.ambient_temp_C
    data["generator_temp_rise_C"] = data.generator_bearing_temp_C - data.ambient_temp_C

    timestamps = data.timestamp.drop_duplicates().sort_values().to_numpy()
    train_end, validation_end = int(0.70 * len(timestamps)), int(0.85 * len(timestamps))
    train = data[data.timestamp.isin(timestamps[:train_end])].copy()
    validation = data[data.timestamp.isin(timestamps[train_end:validation_end])].copy()
    features = [column for column in data.columns if column not in ["failure", "timestamp", "turbine_id"]]

    imputer = SimpleImputer(strategy="median")
    train_x = imputer.fit_transform(train[features])
    validation_x = imputer.transform(validation[features])
    scaler = StandardScaler()
    train_x = scaler.fit_transform(train_x)
    validation_x = scaler.transform(validation_x)
    class_weight = {0: 1.0, 1: float((train.failure == 0).sum() / (train.failure == 1).sum())}

    runs = []
    for config in configurations:
        seed_everything()
        tf.keras.backend.clear_session()
        model = make_model(config, train_x.shape[1])
        history = model.fit(
            train_x, train.failure,
            validation_data=(validation_x, validation.failure),
            epochs=config["epochs"], batch_size=256, class_weight=class_weight,
            callbacks=[EarlyStopping(monitor="val_loss", patience=config["patience"], restore_best_weights=True)],
            verbose=0,
        )
        result = {"id": config["id"], "description": config["description"],
                  "status": "completed", "parameters": config.copy(),
                  "epochs_completed": len(history.history["loss"])}
        result.update(score(model, validation_x, validation.failure))
        runs.append(result)
        print(json.dumps({key: result[key] for key in ["id", "accuracy", "precision", "recall", "f1", "epochs_completed"]}))

        # Persist each completed run so a short-lived terminal cannot discard
        # already-computed validation evidence.
        partial = {
            "method": "Five pre-specified ANN configurations evaluated on the fixed timestamp-grouped chronological validation partition.",
            "selection_rule": "Highest validation recall; F1 then precision only if recall ties. Test partition excluded.",
            "preprocessing": "Median imputation and StandardScaler fitted on training split only; class weighting from training labels; early stopping monitors validation loss.",
            "seed": SEED, "class_weight": class_weight,
            "attempted_configurations": runs,
        }
        with open("outputs/ann_tuning_partial.json", "w") as handle:
            json.dump(partial, handle, indent=2, allow_nan=False)

    winner = max(runs, key=lambda row: (row["recall"], row["f1"], row["precision"]))
    output = {
        "method": "Five pre-specified ANN configurations evaluated on the fixed timestamp-grouped chronological validation partition.",
        "selection_rule": "Highest validation recall; F1 then precision only if recall ties. Test partition excluded.",
        "preprocessing": "Median imputation and StandardScaler fitted on training split only; class weighting from training labels; early stopping monitors validation loss.",
        "seed": SEED,
        "class_weight": class_weight,
        "attempted_configurations": runs,
        "validation_winner": winner,
    }
    with open("outputs/ann_tuning.json", "w") as handle:
        json.dump(output, handle, indent=2, allow_nan=False)
    pd.DataFrame(runs).drop(columns=["parameters"], errors="ignore").to_csv("outputs/ann_tuning_validation_metrics.csv", index=False)


if __name__ == "__main__":
    main()
