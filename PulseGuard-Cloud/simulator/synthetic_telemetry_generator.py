import json
import random
import uuid
import boto3
from datetime import datetime


# --- CONFIGURATION ---
# Set BUCKET_NAME via environment variable for security and consistency.
# Example: add PG_S3_BUCKET=your-bucket-name to your .env file
import os
BUCKET_NAME = os.environ.get('PG_S3_BUCKET', "YOUR_S3_BUCKET_NAME_HERE")

PATIENTS = [
    {"PatientName": "Alice Smith", "DOB": "1980-05-12"},
    {"PatientName": "Bob Jones", "DOB": "1975-09-23"},
    {"PatientName": "Charlie Lee", "DOB": "1990-01-30"},
]

s3 = boto3.client('s3')

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
    print(f"Starting ingestion to bucket: {BUCKET_NAME}")
    for i in range(10):
        telemetry = generate_telemetry()
        
        # Create a unique filename for each reading
        file_name = f"telemetry_{i}_{int(datetime.now().timestamp())}.json"
        
        # Upload to the 'raw/' folder in your bucket
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=f"raw/{file_name}",
            Body=json.dumps(telemetry)
        )
        print(f"Uploaded: {file_name}")

if __name__ == "__main__":
    main()