import subprocess
import sys
import os

# Activate venv if not already active (for interactive use)
def in_venv():
    return sys.prefix != sys.base_prefix

if not in_venv():
    print("Please activate your virtual environment before running this script.")
    sys.exit(1)

# Step 1: Generate test data
print("Generating test data...")
subprocess.run([sys.executable, os.path.join('pipeline', 'generate_test_data.py')], check=True)

# Step 2: Run ETL pipeline
print("Running ETL pipeline...")
subprocess.run([sys.executable, os.path.join('pipeline', 'etl.py')], check=True)

# Step 3: Run analytics and export results
print("Running analytics and exporting results...")
subprocess.run([sys.executable, os.path.join('pipeline', 'analytics.py')], check=True)

print("All steps completed. Check data/processed, data/invalid, pipeline/telemetry.db, and patient_summary.csv.")
