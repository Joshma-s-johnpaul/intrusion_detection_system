import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

# 1. Load the actual data you have
print("📂 Loading Parquet data...")
df = pd.read_parquet('Dataset/UNSW_NB15_testing-set.parquet')

# 2. Select features that EXIST in your file
# These are strong predictors available in your current schema
features = ['sbytes', 'dbytes', 'rate', 'smean', 'dmean'] 

X = df[features]
y = df['label']

# 3. Split and Train
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print(f"🧠 Training Random Forest on {features}...")
rf = RandomForestClassifier(n_estimators=100, max_depth=15, random_state=42)
rf.fit(X_train, y_train)

# 4. Overwrite the old model with the new working one
joblib.dump(rf, 'rf_model.pkl')
print("✅ New 'rf_model.pkl' saved successfully!")

# 5. Verify the results
y_pred = rf.predict(X_test)
print("\n📊 NEW PERFORMANCE METRICS:")
print(classification_report(y_test, y_pred))