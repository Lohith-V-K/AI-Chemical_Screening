import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, classification_report
from imblearn.over_sampling import SMOTE
import pickle

print("Loading data...")
df = pd.read_csv("preprocessed_chemicals.csv")
fingerprints = np.load("fingerprints.npy")

# Loophole 2 fix — combine fingerprints + descriptors
descriptor_cols = [
    'MolecularWeight', 'XLogP', 'TPSA',
    'HBondDonorCount', 'HBondAcceptorCount',
    'RotatableBondCount', 'HeavyAtomCount',
    'Complexity', 'Charge'
]
descriptors = df[descriptor_cols].values[:len(fingerprints)]
descriptors = np.nan_to_num(descriptors, nan=0.0)
X = np.hstack([fingerprints, descriptors])
y = df['Toxicity_Encoded'].values[:len(fingerprints)]

# Remove Unknown
known_mask = y != 0
X_known = X[known_mask]
y_known = y[known_mask]
y_known_adj = y_known - 1  # XGBoost needs 0-based

# Loophole 5 fix — split BEFORE SMOTE
print("Splitting first then applying SMOTE...")
X_train, X_test, y_train, y_test = train_test_split(
    X_known, y_known_adj,
    test_size=0.2,
    random_state=42,
    stratify=y_known_adj
)

# SMOTE only on training
smote = SMOTE(random_state=42)
X_train_bal, y_train_bal = smote.fit_resample(X_train, y_train)
print(f"Training after SMOTE: {len(X_train_bal)}")
print(f"Testing unchanged   : {len(X_test)}")

# Loophole 4 fix — XGBoost
print("\nTraining XGBoost...")
clf = XGBClassifier(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    use_label_encoder=False,
    eval_metric='mlogloss',
    random_state=42,
    n_jobs=-1
)
clf.fit(X_train_bal, y_train_bal)

y_pred = clf.predict(X_test)
f1 = f1_score(y_test, y_pred, average='weighted')

print(f"\n=== RESULTS ===")
print(f"F1 Score: {f1:.3f}")

labels_map = {0:'Low', 1:'Moderate', 2:'High'}
unique_classes = sorted(np.unique(y_test))
target_names = [labels_map[c] for c in unique_classes]
print(classification_report(y_test, y_pred, target_names=target_names))

with open('final_model.pkl', 'wb') as f:
    pickle.dump(clf, f)
print("Model saved!")