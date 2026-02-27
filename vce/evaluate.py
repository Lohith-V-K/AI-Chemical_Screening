import pandas as pd
import numpy as np

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    f1_score,
    classification_report,
    confusion_matrix
)

import pickle

# -----------------------------
# Load data
# -----------------------------
df = pd.read_csv("preprocessed_chemicals.csv")
fingerprints = np.load("fingerprints.npy")

# Features and target
X = fingerprints
y = df["Toxicity_Encoded"].values[:len(fingerprints)]

# -----------------------------
# Train–test split
# -----------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y  # ensures class balance in train/test
)

print(f"Training samples: {len(X_train)}")
print(f"Testing samples: {len(X_test)}")

# -----------------------------
# Train Random Forest classifier
# -----------------------------
print("\nTraining model...")
clf = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
    n_jobs=-1,
    class_weight="balanced"
)

clf.fit(X_train, y_train)

# -----------------------------
# Evaluation
# -----------------------------
y_pred = clf.predict(X_test)

print("\n=== MODEL EVALUATION ===")
print(f"F1 Score (weighted): {f1_score(y_test, y_pred, average='weighted'):.3f}")

print("\nDetailed Classification Report:")
print(
    classification_report(
        y_test,
        y_pred,
        labels=[0, 1, 2, 3],
        target_names=["Unknown", "Low", "Moderate", "High"],
        zero_division=0
    )
)

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred, labels=[0, 1, 2, 3]))

# -----------------------------
# Save trained model
# -----------------------------
with open("toxicity_classifier.pkl", "wb") as f:
    pickle.dump(clf, f)

print("\nClassifier saved successfully!")
