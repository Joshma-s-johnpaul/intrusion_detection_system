import json
from scapy.all import sniff, IP, TCP, UDP, ICMP
from kafka import KafkaProducer
from datetime import datetime

KAFKA_TOPIC = 'viva_PRESENTATION_FINAL' 

producer = KafkaProducer(
    bootstrap_servers='localhost:9092', 
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

START_TIME = datetime.now()

print(f"🕵️ SOC SNIFFER: PROTOCOL AWARENESS ACTIVE")

def get_traffic_label(packet):
    """Identifies the type of traffic for the terminal and brain"""
    if packet.haslayer(ICMP):
        return "PING (ICMP)"
    if packet.haslayer(TCP):
        port = packet[TCP].dport
        if port == 80 or port == 443: return "WEB BROWSER (HTTP/S)"
        if port == 9092: return "KAFKA INTERNAL"
        return f"TCP (Port {port})"
    if packet.haslayer(UDP):
        port = packet[UDP].dport
        if port == 53: return "DNS QUERY"
        return f"UDP (Port {port})"
    return "IP TRAFFIC"

def process_packet(packet):
    if packet.haslayer(IP):
        pkt_time = datetime.fromtimestamp(float(packet.time))
        if pkt_time < START_TIME:
            return

        # Loop-Breaker: Ignore Kafka and Dashboard ports
        if packet.haslayer(TCP):
            if packet[TCP].sport in [9092, 8501, 2181] or packet[TCP].dport in [9092, 8501, 2181]:
                return
        
        label = get_traffic_label(packet)
        
        data = {
            "source_ip": packet[IP].src, 
            "sbytes": len(packet), 
            "label": label,
            "dbytes": 0, "rate": 500, "smean": len(packet), "dmean": 0
        }
        producer.send(KAFKA_TOPIC, value=data)
        print(f"📡 {label} | SRC: {packet[IP].src}")

sniff(iface="lo0", prn=process_packet, store=0, filter="not port 9092 and not port 2181 and not port 8501")