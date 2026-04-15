import pandas as pd
import joblib
from kafka import KafkaConsumer, KafkaProducer
import json
import random

# Load ML components
model = joblib.load('rf_model.pkl')
encoders = joblib.load('encoders.pkl')

# Consumer: Reads raw data
consumer = KafkaConsumer(
    'network_traffic',
    bootstrap_servers=['localhost:9092'],
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

# Producer: Sends results to Dashboard
result_producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda x: x.encode('utf-8')
)

print("🧠 ML Engine is running...")

for message in consumer:
    payload = message.value
    simulated_ip = f"192.168.1.{random.randint(10, 20)}"
    
    row_df = pd.DataFrame([payload])
    row_df = row_df.drop(['attack_cat', 'label'], axis=1, errors='ignore')
    
    # Preprocessing
    for col in row_df.columns:
        if col in encoders:
            le = encoders[col]
            row_df[col] = le.transform(row_df[col].astype(str))
            
    prediction = model.predict(row_df)[0]
    
    # Send result to Kafka 'alerts' topic for the Dashboard
    if prediction == 1:
        alert_msg = f"[ALERT] Intrusion from {simulated_ip}!"
    else:
        alert_msg = f"[PASS] Normal from {simulated_ip}"
    
    result_producer.send('alerts', value=alert_msg)
    print(alert_msg)