# intrusion_detection_system
A real-time hybrid NIDS using Machine Learning (Random Forest) and Heuristic analysis, powered by Apache Kafka and a Streamlit SOC dashboard.
# Real-Time Network Intrusion Detection System (NIDS)
### Hybrid Machine Learning & Heuristic Analysis Engine

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Kafka](https://img.shields.io/badge/Apache%20Kafka-Distributed-orange.svg)](https://kafka.apache.org/)
[![Streamlit](https://img.shields.io/badge/Dashboard-Streamlit-red.svg)](https://streamlit.io/)

## 📌 Project Overview
This project is a real-time Network Intrusion Detection System (NIDS) designed to identify and mitigate volumetric attacks (like DoS/Flood attacks) using a hybrid detection approach. It combines the predictive power of a **Random Forest Classifier** with **Heuristic Feature Analysis** to ensure high accuracy and low false-positive rates in live network environments.

## 🏗️ System Architecture
The system operates as a distributed pipeline:
1.  **Sniffer Node:** Utilizes `Scapy` to perform Deep Packet Inspection (DPI) and extracts flow features.
2.  **Message Broker:** `Apache Kafka` handles the high-velocity data stream between the sniffer and the processor.
3.  **Inference Engine:** A Python-based processor that runs real-time inference using a model trained on the **UNSW-NB15** dataset.
4.  **SOC Dashboard:** A futuristic `Streamlit` interface providing live telemetry, system integrity metrics, and forensic export tools.

## 🛠️ Tech Stack
* **Language:** Python 3.9+
* **Traffic Capture:** Scapy
* **Data Streaming:** Apache Kafka & Zookeeper
* **Machine Learning:** Scikit-Learn (Random Forest), Joblib, Pandas
* **Visualization:** Streamlit (Custom CSS Glassmorphism UI)

## 📁 Project Structure
```text
├── live_sniffer.py      # Real-time packet capture and Kafka producer
├── flink_processor.py   # ML Inference engine and threat classifier
├── dashboard.py         # Streamlit SOC Command Center
├── rf_model.pkl         # Pre-trained Random Forest model
├── requirements.txt     # Project dependencies
└── README.md            # Project documentation
