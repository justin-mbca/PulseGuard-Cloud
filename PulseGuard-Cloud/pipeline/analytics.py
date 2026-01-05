from dotenv import load_dotenv
load_dotenv()
import os
DB_TYPE = os.environ.get('PG_DB_TYPE', 'sqlite')
import sqlite3
import logging
import boto3
from botocore.exceptions import ClientError
import matplotlib.pyplot as plt
import csv

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
DB_TYPE = os.environ.get('PG_DB_TYPE', 'sqlite')
DB_PATH = os.environ.get('PG_DB_PATH', os.path.join(os.path.dirname(__file__), 'telemetry.db'))
# PostgreSQL config
PG_DB_HOST = os.environ.get('PG_DB_HOST')
PG_DB_PORT = os.environ.get('PG_DB_PORT', '5432')
PG_DB_USER = os.environ.get('PG_DB_USER')
PG_DB_PASS = os.environ.get('PG_DB_PASS')
PG_DB_NAME = os.environ.get('PG_DB_NAME')
S3_BUCKET = os.environ.get('PG_S3_BUCKET')
S3_PREFIX_ANALYTICS = os.environ.get('PG_S3_PREFIX_ANALYTICS', 'analytics/')

# S3 helpers
def s3_client():
    return boto3.client(
        's3',
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
        region_name=os.environ.get('AWS_REGION', 'us-east-1')
    )

def s3_write_csv(key, rows):
    import io
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['PatientName', 'Avg_BPM', 'Avg_SpO2'])
    for row in rows:
        writer.writerow(row)
    client = s3_client()
    try:
        client.put_object(Bucket=S3_BUCKET, Key=key, Body=output.getvalue())
    except Exception as e:
        logging.error(f"S3 write error {key}: {e}")
        raise

def fetch_data():
    if DB_TYPE == 'postgres':
        import psycopg2
        conn = psycopg2.connect(
            host=PG_DB_HOST,
            port=PG_DB_PORT,
            user=PG_DB_USER,
            password=PG_DB_PASS,
            dbname=PG_DB_NAME
        )
        c = conn.cursor()
        c.execute('SELECT BPM, SpO2, Timestamp, PatientName FROM telemetry')
        rows = c.fetchall()
        conn.close()
        return rows
    else:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT BPM, SpO2, Timestamp, PatientName FROM telemetry')
        rows = c.fetchall()
        conn.close()
        return rows
# ---
# To use S3, set these environment variables in your .env:
#   PG_S3_BUCKET=your-bucket-name
#   AWS_ACCESS_KEY_ID=...
#   AWS_SECRET_ACCESS_KEY=...
#   AWS_REGION=us-east-1
#   PG_S3_PREFIX_ANALYTICS=analytics/ (optional)
# ---

# ---
# To use PostgreSQL, set these environment variables in your .env:
#   PG_DB_TYPE=postgres
#   PG_DB_HOST=your-db-host
#   PG_DB_PORT=5432
#   PG_DB_USER=your-db-user
#   PG_DB_PASS=your-db-password
#   PG_DB_NAME=your-db-name
# ---

def plot_bpm_spo2(rows):
    bpms = [row[0] for row in rows]
    spo2s = [row[1] for row in rows]
    patients = [row[3] for row in rows]
    plt.figure(figsize=(8,4))
    plt.subplot(1,2,1)
    plt.hist(bpms, bins=range(60, 110, 5), color='skyblue', edgecolor='black')
    plt.title('BPM Distribution')
    plt.xlabel('BPM')
    plt.ylabel('Count')
    plt.subplot(1,2,2)
    plt.hist(spo2s, bins=range(90, 101, 1), color='lightgreen', edgecolor='black')
    plt.title('SpO2 Distribution')
    plt.xlabel('SpO2')
    plt.ylabel('Count')
    plt.tight_layout()
    plt.show()

def print_patient_summary(rows):
    from collections import defaultdict
    patient_stats = defaultdict(list)
    for bpm, spo2, ts, patient in rows:
        patient_stats[patient].append((bpm, spo2))
    for patient, vals in patient_stats.items():
        avg_bpm = sum(v[0] for v in vals) / len(vals)
        avg_spo2 = sum(v[1] for v in vals) / len(vals)
        logging.info(f"{patient}: Avg BPM={avg_bpm:.1f}, Avg SpO2={avg_spo2:.1f}")

    # Export to CSV (S3 or local)
    summary_rows = []
    for patient, vals in patient_stats.items():
        avg_bpm = sum(v[0] for v in vals) / len(vals)
        avg_spo2 = sum(v[1] for v in vals) / len(vals)
        summary_rows.append([patient, f"{avg_bpm:.1f}", f"{avg_spo2:.1f}"])

    if S3_BUCKET:
        s3_write_csv(f"{S3_PREFIX_ANALYTICS}patient_summary.csv", summary_rows)
        logging.info(f"Exported patient summary to S3 bucket {S3_BUCKET} under {S3_PREFIX_ANALYTICS}patient_summary.csv")
    else:
        with open('patient_summary.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['PatientName', 'Avg_BPM', 'Avg_SpO2'])
            for row in summary_rows:
                writer.writerow(row)
        logging.info("Exported patient summary to patient_summary.csv")


if __name__ == "__main__":
    rows = fetch_data()
    if not rows:
        logging.warning("No data found.")
    else:
        print_patient_summary(rows)
        plot_bpm_spo2(rows)

# ---
# To use S3, set these environment variables in your .env:
#   PG_S3_BUCKET=your-bucket-name
#   AWS_ACCESS_KEY_ID=...
#   AWS_SECRET_ACCESS_KEY=...
#   AWS_REGION=us-east-1
#   PG_S3_PREFIX_ANALYTICS=analytics/ (optional)
# ---
