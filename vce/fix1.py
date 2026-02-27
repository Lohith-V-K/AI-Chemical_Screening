
# Remove Unknown
known_mask = y != 0
X_known = X_all[known_mask]
y_known = y[known_mask]
y_known_adj = y_known - 1   # XGBoost needs 0-based
print(f'\nRecords for training: {len(X_known)}')

# Fix 1: Split FIRST
print('Splitting data first...')
X_train, X_test, y_train, y_test = train_test_split(
    X_known, y_known_adj,
    test_size=0.2, random_state=42,
    stratify=y_known_adj
)

# Fix 1: SMOTE on training only
print('Applying SMOTE to training set only...')
smote = SMOTE(random_state=42)
X_train_bal, y_train_bal = smote.fit_resample(X_train, y_train)
print(f'Training after SMOTE: {len(X_train_bal)}')
print(f'Test set unchanged  : {len(X_test)}')

# Fix 3: XGBoost
print('\nTraining XGBoost...')
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
clf.fit(X_train_bal, y_train_bal,
        eval_set=[(X_test, y_test)], verbose=100)

y_pred = clf.predict(X_test)
f1 = f1_score(y_test, y_pred, average='weighted')

print('\n' + '='*50)
print('FINAL RESULTS')
print('='*50)
print(f'F1 Score: {f1:.3f}')

lm = {0:'Low', 1:'Moderate', 2:'High'}
uc = sorted(np.unique(y_test))
tn = [lm[c] for c in uc]
print(classification_report(y_test, y_pred, target_names=tn))

train_pred = clf.predict(X_train_bal)
train_f1 = f1_score(y_train_bal, train_pred, average='weighted')
gap = train_f1 - f1



