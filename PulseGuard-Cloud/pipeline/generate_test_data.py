


import os
import json
import random
import logging
from datetime import datetime, timedelta
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
load_dotenv()

# Configure logging (append to pipeline.log)
os.makedirs(os.path.join(os.path.dirname(__file__), '../logs'), exist_ok=True)
log_path = os.path.join(os.path.dirname(__file__), '../logs/pipeline.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_path, mode='a')
    ]
)


# Local or S3 config
RAW_DIR = os.environ.get('PG_RAW_DIR', os.path.join(os.path.dirname(__file__), '../data/raw'))
S3_BUCKET = os.environ.get('PG_S3_BUCKET')
S3_PREFIX_RAW = os.environ.get('PG_S3_PREFIX_RAW', 'raw/')

# S3 helpers
def s3_client():
    return boto3.client(
        's3',
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
        region_name=os.environ.get('AWS_REGION', 'us-east-1')
    )

def s3_write_json(key, data):
    client = s3_client()
    try:
        client.put_object(Bucket=S3_BUCKET, Key=key, Body=json.dumps(data))
    except Exception as e:
        logging.error(f"S3 write error {key}: {e}")
        raise

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
    if S3_BUCKET:
        for i in range(10):
            d = generate_valid()
            s3_write_json(f"{S3_PREFIX_RAW}valid_{i}.json", d)
        for i in range(5):
            d = generate_invalid()
            s3_write_json(f"{S3_PREFIX_RAW}invalid_{i}.json", d)
        logging.info(f"Test files generated in S3 bucket {S3_BUCKET} under {S3_PREFIX_RAW}")
    else:
        for i in range(10):
            d = generate_valid()
            with open(os.path.join(RAW_DIR, f"valid_{i}.json"), 'w') as f:
                json.dump(d, f)
        for i in range(5):
            d = generate_invalid()
            with open(os.path.join(RAW_DIR, f"invalid_{i}.json"), 'w') as f:
                json.dump(d, f)
        logging.info("Test files generated in data/raw.")


if __name__ == "__main__":
    main()

# ---
# To use S3, set these environment variables in your .env:
#   PG_S3_BUCKET=your-bucket-name
#   AWS_ACCESS_KEY_ID=...
#   AWS_SECRET_ACCESS_KEY=...
#   AWS_REGION=us-east-1
#   PG_S3_PREFIX_RAW=raw/ (optional)
# ---
