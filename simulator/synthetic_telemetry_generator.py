import json
import random
from datetime import datetime, timedelta
import uuid

# Sample patient data
PATIENTS = [
    {"PatientName": "Alice Smith", "DOB": "1980-05-12"},
    {"PatientName": "Bob Jones", "DOB": "1975-09-23"},
    {"PatientName": "Charlie Lee", "DOB": "1990-01-30"},
]

def generate_telemetry():
    patient = random.choice(PATIENTS)
    data = {
        "DeviceID": str(uuid.uuid4()),
        "PatientName": patient["PatientName"],
        "DOB": patient["DOB"],
        "BPM": random.randint(60, 100),
        "SpO2": random.randint(95, 100),
        "Timestamp": datetime.utcnow().isoformat() + "Z"
    }
    return data

def main():
    for _ in range(10):
        telemetry = generate_telemetry()
        print(json.dumps(telemetry))

if __name__ == "__main__":
    main()
