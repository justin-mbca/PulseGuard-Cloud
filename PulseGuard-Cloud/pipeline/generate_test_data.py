import os
import json
import random
from datetime import datetime, timedelta

RAW_DIR = os.path.join(os.path.dirname(__file__), '../data/raw')

PATIENTS = [
    {"PatientName": "Alice Smith", "DOB": "1980-05-12"},
    {"PatientName": "Bob Jones", "DOB": "1975-09-23"},
    {"PatientName": "Charlie Lee", "DOB": "1990-01-30"},
]

def random_timestamp():
    base = datetime.utcnow() - timedelta(days=random.randint(0, 30))
    return base.replace(microsecond=0).isoformat() + "Z"

def generate_valid():
    patient = random.choice(PATIENTS)
    return {
        "DeviceID": str(random.randint(1000, 9999)),
        "PatientName": patient["PatientName"],
        "DOB": patient["DOB"],
        "BPM": random.randint(55, 110),
        "SpO2": random.randint(90, 100),
        "Timestamp": random_timestamp()
    }

def generate_invalid():
    # Randomly drop a field or use out-of-range values
    data = generate_valid()
    err_type = random.choice(["missing", "range", "date"])
    if err_type == "missing":
        data.pop(random.choice(list(data.keys())), None)
    elif err_type == "range":
        data["BPM"] = random.choice([-10, 300])
        data["SpO2"] = random.choice([-5, 150])
    elif err_type == "date":
        data["DOB"] = "not-a-date"
    return data

def main():
    for i in range(10):
        d = generate_valid()
        with open(os.path.join(RAW_DIR, f"valid_{i}.json"), 'w') as f:
            json.dump(d, f)
    for i in range(5):
        d = generate_invalid()
        with open(os.path.join(RAW_DIR, f"invalid_{i}.json"), 'w') as f:
            json.dump(d, f)
    print("Test files generated in data/raw.")

if __name__ == "__main__":
    main()
