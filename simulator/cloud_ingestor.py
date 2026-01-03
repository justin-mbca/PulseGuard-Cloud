import json
import random
import uuid
import boto3
from datetime import datetime

# CONFIGURATION
BUCKET_NAME = "pulseguard-raw-telemetry-38c47f77" # From your Terraform Output
s3 = boto3.client('s3')

PATIENTS = [
    {"PatientName": "Alice Smith", "DOB": "1980-05-12"},
    {"PatientName": "Bob Jones", "DOB": "1975-09-23"},
    {"PatientName": "Charlie Lee", "DOB": "1990-01-30"},
]

def generate_telemetry():
    patient = random.choice(PATIENTS)
    return {
        "DeviceID": str(uuid.uuid4()),
        "PatientName": patient["PatientName"],
        "DOB": patient["DOB"],
        "BPM": random.randint(60, 100),
        "SpO2": random.randint(95, 100),
        "Timestamp": datetime.utcnow().isoformat() + "Z"
    }

def main():
    print(f"Ingesting data to {BUCKET_NAME}...")
    for i in range(10):
        data = generate_telemetry()
        # Create a unique filename for each vital sign check
        file_name = f"telemetry_{uuid.uuid4().hex[:8]}.json"
        
        # Uploading to the 'raw/' folder in your S3 bucket
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=f"raw/{file_name}",
            Body=json.dumps(data)
        )
        print(f"Uploaded {file_name}")

if __name__ == "__main__":
    main()