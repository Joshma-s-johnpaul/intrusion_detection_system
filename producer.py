import json
import time
import random
from kafka import KafkaProducer

TOPIC = 'traffic-input'
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

def get_traffic():
    mode = random.choice(["Normal", "Attack"])
    if mode == "Attack":
        return {
            "source_ip": f"10.0.0.{random.randint(100, 255)}",
            "sbytes": random.randint(3000, 5000), 
            "sttl": 252, "dttl": 252, "rate": 1000, "label": 1, "type": "DoS"
        }
    else:
        return {
            "source_ip": f"192.168.1.{random.randint(1, 50)}",
            "sbytes": random.randint(50, 200), 
            "sttl": 64, "dttl": 64, "rate": 10, "label": 0, "type": "Normal"
        }

print("🚀 Producer started. Sending Mixed Traffic...")
while True:
    data = get_traffic()
    producer.send(TOPIC, value=data)
    print(f"📡 Sent {data['type']} from {data['source_ip']}")
    time.sleep(1)