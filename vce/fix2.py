import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, classification_report
from imblearn.over_sampling import SMOTE
import pickle

print('Loading data...')
df = pd.read_csv('preprocessed_chemicals.csv')
fingerprints = np.load('fingerprints.npy')
print(f'Fingerprint shape: {fingerprints.shape}')

# ---- FIX: ADD MOLECULAR DESCRIPTORS ----
descriptor_cols = [
    'MolecularWeight', 'XLogP', 'TPSA',
    'HBondDonorCount', 'HBondAcceptorCount',
    'RotatableBondCount', 'HeavyAtomCount',
    'Complexity', 'Charge'
]

# Get descriptor values aligned with fingerprints
descriptors = df[descriptor_cols].values[:len(fingerprints)]

# Fill any missing values with 0
descriptors = np.nan_to_num(descriptors, nan=0.0)
print(f'Descriptor shape: {descriptors.shape}')

# Combine fingerprints + descriptors side by side
X_combined = np.hstack([fingerprints, descriptors])
print(f'Old feature size: {fingerprints.shape[1]}')
print(f'New feature size: {X_combined.shape[1]}')
print(f'Extra features added: {descriptors.shape[1]}')

# Save combined features for reuse
np.save('combined_features.npy', X_combined)
print('Combined features saved!')

y = df['Toxicity_Encoded'].values[:len(fingerprints)]

# Remove Unknown
known_mask = y != 0
X_known = X_combined[known_mask]
y_known = y[known_mask]

# Split FIRST
X_train, X_test, y_train, y_test = train_test_split(
    X_known, y_known,
    test_size=0.2, random_state=42,
    stratify=y_known
)

# SMOTE on training only
smote = SMOTE(random_state=42)
X_train_bal, y_train_bal = smote.fit_resample(X_train, y_train)

# Train
print('Training with combined features...')
clf = RandomForestClassifier(
    n_estimators=200,
    max_depth=10,
    min_samples_split=20,
    min_samples_leaf=10,
    max_features='sqrt',
    max_samples=0.8,
    class_weight='balanced',
    random_state=42,
    n_jobs=-1
)
clf.fit(X_train_bal, y_train_bal)

y_pred = clf.predict(X_test)
f1 = f1_score(y_test, y_pred, average='weighted')
print(f'\nF1 Score with combined features: {f1:.3f}')

labels_map = {1:'Low', 2:'Moderate', 3:'High'}
unique_classes = sorted(np.unique(y_test))
target_names = [labels_map[c] for c in unique_classes]
print(classification_report(y_test, y_pred, target_names=target_names))

with open('model_fix2.pkl', 'wb') as f:
    pickle.dump(clf, f)
print('Model saved as model_fix2.pkl')

