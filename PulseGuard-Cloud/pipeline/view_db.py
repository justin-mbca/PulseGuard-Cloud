

import sqlite3
import os
import logging
from dotenv import load_dotenv
load_dotenv()

# Use environment variable for DB path, fallback to default
DB_PATH = os.environ.get('PG_DB_PATH', os.path.join(os.path.dirname(__file__), 'telemetry.db'))

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

def print_all_records():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM telemetry')
    rows = c.fetchall()
    for row in rows:
        logging.info(f"DB Record: {row}")
    conn.close()

if __name__ == "__main__":
    print_all_records()
