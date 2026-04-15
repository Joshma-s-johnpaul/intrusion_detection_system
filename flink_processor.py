import json, joblib, pandas as pd, time
from kafka import KafkaConsumer, KafkaProducer
from datetime import datetime

# --- 1. LOAD MODEL ---
model = joblib.load('rf_model.pkl')
features = list(model.feature_names_in_)

# --- 2. KAFKA CONFIG ---
IN_TOPIC = 'viva_PRESENTATION_FINAL'  
OUT_TOPIC = 'alerts_PRESENTATION_FINAL'

consumer = KafkaConsumer(
    IN_TOPIC, bootstrap_servers='localhost:9092',
    group_id=f'brain-{time.time()}', auto_offset_reset='latest',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

print(f"🧠 IDS BRAIN: HYBRID ANALYSIS ONLINE")

# --- 3. PROCESSING LOOP ---
for message in consumer:
    current_time_ms = int(time.time() * 1000)
    if (current_time_ms - message.timestamp) > 60000:
        continue 

    packet = message.value
    traffic_type = packet.get('label', 'IP TRAFFIC')
    
    df = pd.DataFrame(0, index=[0], columns=features)
    for col in features:
        if col in packet: df[col] = packet[col]

    try:
        prob = model.predict_proba(df)[0][1]
        
        # Heuristic boost for large packets (Demo sensitivity)
        if packet.get('sbytes', 0) > 150:
            prob += 0.25  

        if prob > 0.70: 
            ts = datetime.now().strftime("%H:%M:%S")
            producer.send(OUT_TOPIC, value={
                "source_ip": packet.get('source_ip', '127.0.0.1'), 
                "status": "🚨 THREAT", 
                "label": traffic_type,
                "timestamp": ts
            })
            print(f"🚨 ALERT: {traffic_type} from {packet.get('source_ip')} | Score: {min(prob, 1.0):.2f}")
        else:
            print(f"✅ PASS: {traffic_type} | SRC: {packet.get('source_ip')} | Score: {prob:.2f}")
            
    except:
        continue