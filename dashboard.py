import streamlit as st, json, pandas as pd, time
from kafka import KafkaConsumer
from datetime import datetime

# --- 1. Page Config & Cyber-Industrial Styling ---
st.set_page_config(page_title="IDS Command Center", layout="wide", page_icon="🛡️")

st.markdown("""
    <style>
    /* Professional Dark Slate Background */
    .main { 
        background-color: #0d1117; 
        background-image: radial-gradient(circle at 2px 2px, #161b22 1px, transparent 0);
        background-size: 30px 30px;
        color: #c9d1d9; 
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
    }
    
    /* Metric Cards with depth */
    div[data-testid="stMetricValue"] { 
        font-size: 48px !important; 
        font-weight: 800 !important; 
        color: #58a6ff !important;
        background: rgba(22, 27, 34, 0.5);
        padding: 10px 20px;
        border-radius: 10px;
        border: 1px solid #30363d;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] { 
        background-color: #010409 !important; 
        border-right: 1px solid #30363d !important;
    }

    /* Section Headers */
    h1, h2, h3 { 
        color: #f0f6fc !important;
        border-bottom: 1px solid #21262d;
        padding-bottom: 10px;
        font-weight: 700;
    }

    /* Table styling */
    .stTable { 
        background-color: #161b22; 
        border-radius: 12px;
        border: 1px solid #30363d;
    }

    /* Progress bar color */
    .stProgress > div > div > div > div {
        background-image: linear-gradient(to right, #1f6feb, #58a6ff);
    }

    /* Alert and Code blocks */
    .stAlert { border-radius: 8px; border: 1px solid #30363d; }
    code { color: #79c0ff !important; background-color: #0d1117 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. State Management ---
if 'total_packets' not in st.session_state:
    st.session_state.update({
        'total_packets': 0, 
        'all_alerts': [], 
        'blocked_ips': set(),
        'start_time': datetime.now().strftime("%H:%M:%S")
    })

# --- 3. Kafka Consumers ---
if 'traffic_consumer' not in st.session_state:
    uid = time.time()
    st.session_state.traffic_consumer = KafkaConsumer('viva_PRESENTATION_FINAL', bootstrap_servers='localhost:9092', auto_offset_reset='latest', group_id=f't-{uid}', value_deserializer=lambda x: json.loads(x.decode('utf-8')), consumer_timeout_ms=1000)
    st.session_state.alert_consumer = KafkaConsumer('alerts_PRESENTATION_FINAL', bootstrap_servers='localhost:9092', auto_offset_reset='latest', group_id=f'a-{uid}', value_deserializer=lambda x: json.loads(x.decode('utf-8')), consumer_timeout_ms=1000)

# --- 4. Populated Sidebar with Exports ---
with st.sidebar:
    st.markdown("## 🛡️ CORE CONTROL")
    st.markdown("---")
    
    # System Status Indicators
    st.write("📡 **Engine Status:** `ACTIVE`")
    st.write("🧠 **ML Model:** `RF_HYBRID_v3.4`")
    st.write("🔗 **Kafka Stream:** `CONNECTED`")
    
    st.markdown("---")
    st.subheader("📊 FORENSIC TOOLS")
    
    if st.session_state.all_alerts:
        # Export 1: Detailed CSV
        df_export = pd.DataFrame(st.session_state.all_alerts)
        csv = df_export.to_csv(index=False).encode('utf-8')
        st.download_button("📥 EXPORT ALERT CSV", data=csv, file_name="incident_report.csv", use_container_width=True)
        
        # Export 2: Mitigation Log TXT
        mitigation_content = [f"Time: {a['Time']} | Source: {a['Source']} | Action: {a['Status']}" for a in st.session_state.all_alerts]
        mitigation_text = "\n".join(mitigation_content)
        st.download_button("📂 EXPORT MITIGATION LOG", data=mitigation_text, file_name="mitigation_actions.txt", use_container_width=True)
    else:
        st.button("📥 EXPORT ALERT CSV", disabled=True, use_container_width=True)
        st.button("📂 EXPORT MITIGATION LOG", disabled=True, use_container_width=True)
    
    st.markdown("---")
    if st.button("🔄 EMERGENCY RESET", use_container_width=True):
        st.session_state.clear(); st.rerun()
    
    st.markdown("---")
    st.caption("© 2026 Cybersecurity Honours Project")

# --- 5. Main Dashboard Header ---
st.markdown("<h1 style='color: #58a6ff !important;'>REAL-TIME CYBER THREAT INTELLIGENCE</h1>", unsafe_allow_html=True)
st.caption(f"🛡️ SECURE SESSION ESTABLISHED | SESSION START: {st.session_state.start_time}")

# Metrics
m1, m2, m3, m4 = st.columns(4)
met1, met2, met3, met4 = m1.empty(), m2.empty(), m3.empty(), m4.empty()

st.markdown("<br>", unsafe_allow_html=True)

# Dashboard Body
col_left, col_right = st.columns([1, 2])

with col_left:
    st.markdown("### 🛑 MITIGATION ACTIONS")
    log_area = st.empty()
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🧬 SYSTEM INTEGRITY")
    gauge_bar = st.empty()
    gauge_text = st.empty()
    status_msg = st.empty()

with col_right:
    st.markdown("### 🚨 LIVE INCIDENT FEED")
    table_area = st.empty()

# --- 6. The Engine ---
while True:
    now_ms = int(time.time() * 1000)
    
    t_recs = st.session_state.traffic_consumer.poll(timeout_ms=100)
    for tp, msgs in t_recs.items():
        for m in msgs:
            if (now_ms - m.timestamp) < 60000:
                st.session_state.total_packets += 1

    a_recs = st.session_state.alert_consumer.poll(timeout_ms=100)
    for tp, msgs in a_recs.items():
        for m in msgs:
            if (now_ms - m.timestamp) < 60000:
                data = m.value
                st.session_state.all_alerts.insert(0, {
                    "Time": datetime.now().strftime("%H:%M:%S"), 
                    "Source": data['source_ip'], 
                    "Vector": data.get('label', 'Anomalous Traffic'),
                    "Status": "BLOCKED"
                })
                st.session_state.blocked_ips.add(data['source_ip'])

    # UI Calcs
    total, intr = st.session_state.total_packets, len(st.session_state.all_alerts)
    health = max(0, 100 - (intr * 2))
    
    # Update Metrics
    met1.metric("TRAFFIC ANALYSED", f"{total:,}")
    met2.metric("THREATS DETECTED", intr, delta_color="inverse")
    met3.metric("NODAL HEALTH", f"{health}%")
    met4.metric("IPs BLACKLISTED", len(st.session_state.blocked_ips))

    # Update Logs
    logs = [f"▸ {a['Time']} | REJECTED: {a['Source']}" for a in st.session_state.all_alerts[:6]]
    log_area.code("\n".join(logs) if logs else "Awaiting traffic for analysis...")

    # Update Gauge
    gauge_bar.progress(health / 100)
    gauge_text.markdown(f"**Integrity Level:** `{health}%` | Status: `{'SECURE' if health > 85 else 'COMPROMISED'}`")
    
    if health < 50: status_msg.error("🚨 CRITICAL: MULTIPLE INJECTIONS DETECTED")
    elif health < 90: status_msg.warning("⚠️ WARNING: UNUSUAL PACKET SIZE")
    else: status_msg.success("✅ SYSTEM OPERATING WITHIN NORMAL PARAMETERS")

    if st.session_state.all_alerts:
        table_area.table(pd.DataFrame(st.session_state.all_alerts[:12]))
    else:
        table_area.info("System initialized. Monitoring network interfaces...")

    time.sleep(0.5)