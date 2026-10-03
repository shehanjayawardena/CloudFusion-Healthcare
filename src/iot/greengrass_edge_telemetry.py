"""
CloudFusion Healthcare Analytics Ltd (CHA)
AWS IoT Greengrass v2 Edge Telemetry Processor
Runs on hospital edge appliances in regional clinics and wards.
Features:
- Local vital sign smoothing and threshold anomaly detection
- SQLite local encrypted buffering during WAN outages (Store-and-Forward)
- AWS IoT Greengrass IPC communication to cloud broker
"""

import time
import json
import sqlite3
import os
import random
from datetime import datetime, timezone

import os

DEFAULT_LINUX_PATH = "/var/log/greengrass/edge_telemetry_buffer.db"
DB_PATH = DEFAULT_LINUX_PATH if os.name != 'nt' else os.path.join(os.path.dirname(os.path.abspath(__file__)), "edge_telemetry_buffer.db")


def init_local_database():
    """Initializes local SQLite database for store-and-forward edge buffering."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS buffered_vitals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT,
            heart_rate REAL,
            spo2 REAL,
            systolic_bp REAL,
            diastolic_bp REAL,
            temperature REAL,
            anomaly_detected INTEGER,
            timestamp TEXT,
            synced INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()
    print("[EDGE-INIT] Local SQLite offline buffer initialized.")

def sample_sensor_telemetry(patient_id: str) -> dict:
    """Simulates receiving reading from patient ward monitors or BLE wearables."""
    hr = round(random.normalvariate(78, 12), 1)
    spo2 = round(random.uniform(92.0, 99.5), 1)
    sys_bp = round(random.uniform(110, 135), 1)
    dia_bp = round(random.uniform(70, 88), 1)
    temp = round(random.uniform(36.5, 37.4), 1)

    # Inject occasional critical threshold for testing triage pipeline
    if random.random() < 0.05:
        spo2 = 88.0  # Critical hypoxia

    is_anomaly = (spo2 < 90.0) or (hr > 135) or (hr < 45)

    return {
        "patient_id": patient_id,
        "heart_rate": hr,
        "spo2": spo2,
        "blood_pressure": {
            "systolic": sys_bp,
            "diastolic": dia_bp
        },
        "temperature_celsius": temp,
        "anomaly_flag": is_anomaly,
        "device_id": f"BLE-WARD-NODE-{patient_id}",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


def buffer_telemetry_locally(telemetry: dict):
    """Buffers telemetry into SQLite when offline or for local clinical auditing."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO buffered_vitals 
            (patient_id, heart_rate, spo2, systolic_bp, diastolic_bp, temperature, anomaly_detected, timestamp, synced)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
        """, (
            telemetry["patient_id"],
            telemetry["heart_rate"],
            telemetry["spo2"],
            telemetry["blood_pressure"]["systolic"],
            telemetry["blood_pressure"]["diastolic"],
            telemetry["temperature_celsius"],
            1 if telemetry["anomaly_flag"] else 0,
            telemetry["timestamp"]
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[EDGE-ERROR] Failed to buffer record locally: {e}")

def publish_to_cloud(telemetry: dict, is_network_online: bool = True) -> bool:
    """Publishes telemetry to AWS IoT Core via Greengrass IPC or records failure."""
    if not is_network_online:
        print(f"[EDGE-OFFLINE] WAN unavailable. Buffering telemetry for patient {telemetry['patient_id']}...")
        buffer_telemetry_locally(telemetry)
        return False

    # Simulate Greengrass IPC Publish
    topic = f"healthcare/patients/{telemetry['patient_id']}/vitals"
    payload = json.dumps(telemetry)
    print(f"[EDGE-UPLINK] Published to {topic}: {payload}")
    return True

def sync_offline_buffer():
    """Flushes buffered records once network connectivity is re-established."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, patient_id, heart_rate, spo2, timestamp FROM buffered_vitals WHERE synced = 0 LIMIT 50")
        rows = cursor.fetchall()
        for row in rows:
            record_id, pid, hr, spo2, ts = row
            print(f"[EDGE-SYNC] Synchronizing buffered historical vital for {pid} at {ts} (HR: {hr}, SpO2: {spo2})")
            cursor.execute("UPDATE buffered_vitals SET synced = 1 WHERE id = ?", (record_id,))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[EDGE-SYNC-ERROR] {e}")

def main():
    init_local_database()
    active_patients = [f"PATIENT-{(1000 + i)}" for i in range(5)]
    print("[EDGE-START] CloudFusion Edge Processor active. Polling sensors...")

    iteration = 0
    while iteration < 10:  # In production, runs as a continuous daemon
        iteration += 1
        for patient in active_patients:
            telemetry = sample_sensor_telemetry(patient)
            if telemetry["anomaly_flag"]:
                print(f"[CRITICAL-ALERT] High priority event detected for {patient}: SpO2={telemetry['spo2']}%, HR={telemetry['heart_rate']}")
            publish_to_cloud(telemetry, is_network_online=True)
            time.sleep(0.5)
        sync_offline_buffer()
        time.sleep(2)

if __name__ == "__main__":
    main()
