import os
import json

import sqlite3
from jsonschema import validate, ValidationError
from datetime import datetime


# Define paths

RAW_DIR = os.path.join(os.path.dirname(__file__), '../data/raw')
PROCESSED_DIR = os.path.join(os.path.dirname(__file__), '../data/processed')
INVALID_DIR = os.path.join(os.path.dirname(__file__), '../data/invalid')
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'telemetry_schema.json')
DB_PATH = os.path.join(os.path.dirname(__file__), 'telemetry.db')

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

# Insert record into DB
def insert_to_db(data):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT INTO telemetry (DeviceID, PatientName, DOB, BPM, SpO2, Timestamp, IngestedAt)
                 VALUES (?, ?, ?, ?, ?, ?, ?)''',
              (data['DeviceID'], data['PatientName'], data['DOB'], data['BPM'], data['SpO2'], data['Timestamp'], data['IngestedAt']))
    conn.commit()
    conn.close()

# Load schema
def load_schema():
    with open(SCHEMA_PATH, 'r') as f:
        return json.load(f)

# Process files

def process_files():
    schema = load_schema()
    init_db()
    for filename in os.listdir(RAW_DIR):
        if filename.endswith('.json'):
            raw_path = os.path.join(RAW_DIR, filename)
            with open(raw_path, 'r') as f:
                try:
                    data = json.load(f)
                    validate(instance=data, schema=schema)
                    data = transform_data(data)
                except (json.JSONDecodeError, ValidationError) as e:
                    print(f"Invalid file {filename}: {e}")
                    # Move invalid file to INVALID_DIR
                    invalid_path = os.path.join(INVALID_DIR, filename)
                    os.rename(raw_path, invalid_path)
                    continue
            # Save to processed
            processed_path = os.path.join(PROCESSED_DIR, filename)
            with open(processed_path, 'w') as pf:
                json.dump(data, pf)
            insert_to_db(data)
            print(f"Processed and stored: {filename}")

if __name__ == "__main__":
    process_files()
