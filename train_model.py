import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib

df = pd.read_parquet('Dataset/UNSW_NB15_training-set.parquet')
df = df[df['attack_cat'].isin(['Normal', 'DoS'])]

X = df.drop(['attack_cat', 'label'], axis=1)
y = df['label']

encoders = {}

for col in X.columns:
    if not pd.api.types.is_numeric_dtype(X[col]):
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
        encoders[col] = le

model = RandomForestClassifier()
model.fit(X, y)

joblib.dump(model, 'rf_model.pkl')
joblib.dump(encoders, 'encoders.pkl')

print("Model and encoders saved successfully.")