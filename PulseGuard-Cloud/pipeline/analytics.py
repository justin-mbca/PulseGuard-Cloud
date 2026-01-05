import sqlite3
import os
import matplotlib.pyplot as plt

import csv

DB_PATH = os.path.join(os.path.dirname(__file__), 'telemetry.db')

def fetch_data():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT BPM, SpO2, Timestamp, PatientName FROM telemetry')
    rows = c.fetchall()
    conn.close()
    return rows

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
        print(f"{patient}: Avg BPM={avg_bpm:.1f}, Avg SpO2={avg_spo2:.1f}")

    # Export to CSV
    with open('patient_summary.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['PatientName', 'Avg_BPM', 'Avg_SpO2'])
        for patient, vals in patient_stats.items():
            avg_bpm = sum(v[0] for v in vals) / len(vals)
            avg_spo2 = sum(v[1] for v in vals) / len(vals)
            writer.writerow([patient, f"{avg_bpm:.1f}", f"{avg_spo2:.1f}"])
    print("Exported patient summary to patient_summary.csv")

if __name__ == "__main__":
    rows = fetch_data()
    if not rows:
        print("No data found.")
    else:
        print_patient_summary(rows)
        plot_bpm_spo2(rows)
