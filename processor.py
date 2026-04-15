import json
import joblib
import pandas as pd
from kafka import KafkaConsumer, KafkaProducer
from datetime import datetime
import time

# --- 1. LOAD MODEL ---
model = joblib.load('rf_model.pkl')
model_features = list(model.feature_names_in_)

# --- 2. KAFKA CONFIG ---
INPUT_TOPIC = 'traffic-final'
OUTPUT_TOPIC = 'alerts-final'

consumer = KafkaConsumer(
    INPUT_TOPIC,
    bootstrap_servers='localhost:9092',
    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
    auto_offset_reset='earliest',
    group_id=f'final-proc-{time.time()}'
)

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

print(f"🧠 Processor: High-Sensitivity Mode Active...")

for message in consumer:
    packet = message.value
    input_df = pd.DataFrame(0, index=[0], columns=model_features)
    
    for col in model_features:
        if col in packet:
            input_df[col] = packet[col]

    try:
        # Get Probability instead of just 0 or 1
        # This helps if the model is 'uncertain'
        probabilities = model.predict_proba(input_df)[0]
        # index 1 is usually the 'Attack' class
        attack_prob = probabilities[1] 
        
        # Sensitivity Threshold: 0.3 (30%)
        # Normal models use 0.5, but let's make it catch the DoS!
        prediction = 1 if attack_prob > 0.3 else 0
        
        status = "🚨 ALERT" if prediction == 1 else "✅ PASS"
        print(f"[{status}] Prob: {attack_prob:.2f} | Data: {packet.get('attack_cat')}")

        if prediction == 1:
            alert_msg = {
                "source_ip": packet.get('source_ip'),
                "status": "🚨 INTRUSION",
                "attack_type": "DoS",
                "confidence": f"{attack_prob:.2%}",
                "timestamp": datetime.now().strftime("%H:%M:%S")
            }
            producer.send(OUTPUT_TOPIC, value=alert_msg)
    except Exception as e:
        # Fallback if predict_proba isn't supported by your specific pkl
        prediction = model.predict(input_df)[0]
        if prediction == 1:
            print("🚨 ALERT (Standard Prediction)")
            # ... (send producer alert here)