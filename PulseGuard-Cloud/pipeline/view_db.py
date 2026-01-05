import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'telemetry.db')

def print_all_records():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM telemetry')
    rows = c.fetchall()
    for row in rows:
        print(row)
    conn.close()

if __name__ == "__main__":
    print_all_records()
