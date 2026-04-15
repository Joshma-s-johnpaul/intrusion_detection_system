import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score

# 1. Load Data
MODEL_PATH = 'rf_model.pkl'
TEST_DATA_PATH = 'Dataset/UNSW_NB15_testing-set.parquet'

print("🚀 Loading Model...")
model = joblib.load(MODEL_PATH)
test_df = pd.read_parquet(TEST_DATA_PATH)

# Get the EXACT list of features the model wants
expected_features = list(model.feature_names_in_) 
print(f"🧠 Model expects: {expected_features}")

# 2. STRICT FEATURE ALIGNMENT
X_test = pd.DataFrame()

# We map and inject into the new dataframe
# We use a loop based on 'expected_features' to ensure the ORDER is correct
for feature in expected_features:
    if feature in test_df.columns:
        X_test[feature] = test_df[feature]
    elif feature == 'sttl' and 'smean' in test_df.columns:
        X_test['sttl'] = test_df['smean']
        print("🔗 Mapping 'sttl' -> 'smean'")
    elif feature == 'dttl' and 'dmean' in test_df.columns:
        X_test['dttl'] = test_df['dmean']
        print("🔗 Mapping 'dttl' -> 'dmean'")
    else:
        print(f"⚠️ Warning: {feature} missing, filling with 0.")
        X_test[feature] = 0

# IMPORTANT: This line ensures the order is exactly what the model wants
X_test = X_test[expected_features]

y_test = test_df['label']

# 3. Prediction
print("🧠 Running Inference...")
y_pred = model.predict(X_test)

# --- VISUALIZATION: CONFUSION MATRIX ---
plt.figure(figsize=(8, 6))
cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=['Normal', 'Attack'], 
            yticklabels=['Normal', 'Attack'])
plt.title('Confusion Matrix: Honours IDS Project')
plt.savefig('confusion_matrix_final.png')

# --- TEXT REPORT ---
print("\n" + "="*30)
print("📊 FINAL PERFORMANCE METRICS")
print("="*30)
print(classification_report(y_test, y_pred))