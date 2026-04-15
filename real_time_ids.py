import pandas as pd
import joblib
import time
import random

model = joblib.load('rf_model.pkl')
encoders = joblib.load('encoders.pkl')

df = pd.read_parquet('Dataset/UNSW_NB15_testing-set.parquet')
df = df[df['attack_cat'].isin(['Normal', 'DoS'])]

X = df.drop(['attack_cat', 'label'], axis=1)
y = df['label']

for col in X.columns:
    if col in encoders:
        le = encoders[col]
        X[col] = X[col].map(lambda s: s if s in le.classes_ else le.classes_[0])
        X[col] = le.transform(X[col].astype(str))

blacklist = set()

print("Starting Real-Time Intrusion Detection System...")
print("-" * 50)

for index, row in X.sample(n=25, random_state=42).iterrows():
    time.sleep(1.2)
    
    simulated_ip = f"192.168.1.{random.randint(10, 30)}"
    
    if simulated_ip in blacklist:
        print(f"[FIREWALL] Dropped connection from blacklisted IP: {simulated_ip}")
        continue
        
    row_df = pd.DataFrame([row])
    prediction = model.predict(row_df)[0]
    
    if prediction == 1:
        print(f"\n[ALERT] Intrusion Detected! DoS attack signature identified.")
        print(f"[ACTION] Adding {simulated_ip} to firewall blacklist.\n")
        blacklist.add(simulated_ip)
    else:
        print(f"[PASS] Normal traffic from {simulated_ip} allowed.")