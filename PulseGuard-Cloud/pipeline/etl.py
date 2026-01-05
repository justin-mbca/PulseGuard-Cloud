# Insert record into DB
def insert_to_db(data):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT INTO telemetry (DeviceID, PatientName, DOB, BPM, SpO2, Timestamp, IngestedAt)
                 VALUES (?, ?, ?, ?, ?, ?, ?)''',
              (data['DeviceID'], data['PatientName'], data['DOB'], data['BPM'], data['SpO2'], data['Timestamp'], data['IngestedAt']))
    conn.commit()
    conn.close()


import os
import json
import logging

import sqlite3
DB_TYPE = os.environ.get('PG_DB_TYPE', 'sqlite')
if DB_TYPE == 'postgres':
    import psycopg2
    from psycopg2 import sql
from jsonschema import validate, ValidationError
from datetime import datetime
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
load_dotenv()

# Configure logging
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
PROCESSED_DIR = os.environ.get('PG_PROCESSED_DIR', os.path.join(os.path.dirname(__file__), '../data/processed'))
INVALID_DIR = os.environ.get('PG_INVALID_DIR', os.path.join(os.path.dirname(__file__), '../data/invalid'))
SCHEMA_PATH = os.environ.get('PG_SCHEMA_PATH', os.path.join(os.path.dirname(__file__), 'telemetry_schema.json'))
DB_PATH = os.environ.get('PG_DB_PATH', os.path.join(os.path.dirname(__file__), 'telemetry.db'))
S3_BUCKET = os.environ.get('PG_S3_BUCKET')  # If set, use S3 for file I/O
S3_PREFIX_RAW = os.environ.get('PG_S3_PREFIX_RAW', 'raw/')
S3_PREFIX_PROCESSED = os.environ.get('PG_S3_PREFIX_PROCESSED', 'processed/')
S3_PREFIX_INVALID = os.environ.get('PG_S3_PREFIX_INVALID', 'invalid/')

# S3 helpers
def s3_client():
    return boto3.client(
        's3',
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
        region_name=os.environ.get('AWS_REGION', 'us-east-1')
    )

def s3_list_files(prefix):
    client = s3_client()
    try:
        resp = client.list_objects_v2(Bucket=S3_BUCKET, Prefix=prefix)
        return [obj['Key'] for obj in resp.get('Contents', []) if obj['Key'].endswith('.json')]
    except ClientError as e:
        logging.error(f"S3 list error: {e}")
        return []

def s3_read_json(key):
    client = s3_client()
    try:
        obj = client.get_object(Bucket=S3_BUCKET, Key=key)
        return json.load(obj['Body'])
    except Exception as e:
        logging.error(f"S3 read error {key}: {e}")
        raise

def s3_write_json(key, data):
    client = s3_client()
    try:
        client.put_object(Bucket=S3_BUCKET, Key=key, Body=json.dumps(data))
    except Exception as e:
        logging.error(f"S3 write error {key}: {e}")
        raise

def s3_move_file(src_key, dest_key):
    client = s3_client()
    try:
        client.copy_object(Bucket=S3_BUCKET, CopySource={'Bucket': S3_BUCKET, 'Key': src_key}, Key=dest_key)
        client.delete_object(Bucket=S3_BUCKET, Key=src_key)
    except Exception as e:
        logging.error(f"S3 move error {src_key} -> {dest_key}: {e}")
        raise

# Transformation: add ingestion timestamp and uppercase patient name
def transform_data(data):
    data['IngestedAt'] = datetime.utcnow().isoformat() + 'Z'
    data['PatientName'] = data['PatientName'].upper()
    return data

# Initialize SQLite DB
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS telemetry (
        DeviceID TEXT,
        PatientName TEXT,
        DOB TEXT,
        BPM INTEGER,
        SpO2 INTEGER,
        Timestamp TEXT,
        IngestedAt TEXT
    )''')
    conn.commit()
    conn.close()

# Load schema
def load_schema():
    with open(SCHEMA_PATH, 'r') as f:
        return json.load(f)


# Process files (local or S3)
def process_files():
    schema = load_schema()
    init_db()
    if S3_BUCKET:
        # S3 mode
        raw_files = s3_list_files(S3_PREFIX_RAW)
        for key in raw_files:
            filename = os.path.basename(key)
            try:
                data = s3_read_json(key)
                validate(instance=data, schema=schema)
                data = transform_data(data)
            except (json.JSONDecodeError, ValidationError) as e:
                logging.warning(f"Invalid file {filename}: {e}")
                # Move invalid file to S3 invalid/
                s3_move_file(key, S3_PREFIX_INVALID + filename)
                continue
            # Save to processed
            s3_write_json(S3_PREFIX_PROCESSED + filename, data)
            s3_move_file(key, S3_PREFIX_PROCESSED + filename)  # Remove from raw
            insert_to_db(data)
            logging.info(f"Processed and stored (S3): {filename}")
    else:
        # Local mode
        for filename in os.listdir(RAW_DIR):
            if filename.endswith('.json'):
                raw_path = os.path.join(RAW_DIR, filename)
                with open(raw_path, 'r') as f:
                    try:
                        data = json.load(f)
                        validate(instance=data, schema=schema)
                        data = transform_data(data)
                    except (json.JSONDecodeError, ValidationError) as e:
                        logging.warning(f"Invalid file {filename}: {e}")
                        # Move invalid file to INVALID_DIR
                        invalid_path = os.path.join(INVALID_DIR, filename)
                        os.rename(raw_path, invalid_path)
                        continue
                # Save to processed
                processed_path = os.path.join(PROCESSED_DIR, filename)
                with open(processed_path, 'w') as pf:
                    json.dump(data, pf)
                insert_to_db(data)
                logging.info(f"Processed and stored: {filename}")


if __name__ == "__main__":
    process_files()

# ---
# To use S3, set these environment variables in your .env:
#   PG_S3_BUCKET=your-bucket-name
#   AWS_ACCESS_KEY_ID=...
#   AWS_SECRET_ACCESS_KEY=...
#   AWS_REGION=us-east-1
#   PG_S3_PREFIX_RAW=raw/ (optional)
#   PG_S3_PREFIX_PROCESSED=processed/ (optional)
#   PG_S3_PREFIX_INVALID=invalid/ (optional)
# ---
