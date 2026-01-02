import json
import re
import subprocess

REQUIRED_FIELDS = ["device_id", "bpm", "patient_name"]
ISO_8601_REGEX = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z$"

# Update this path if the simulator script is elsewhere
SIMULATOR_PATH = "../simulator/device_sim.py"


def run_simulator(num_records=5):
    """Run the device simulator and yield each JSON record as a dict."""
    proc = subprocess.Popen([
        "python", SIMULATOR_PATH, str(num_records)
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    for line in proc.stdout:
        line = line.strip()
        if line:
            yield json.loads(line)
    proc.stdout.close()
    proc.wait()


def validate_record(record):
    # Check required fields
    for field in REQUIRED_FIELDS:
        if field not in record:
            print(f"Missing required field: {field}")
            return False
    # Check bpm is integer
    if not isinstance(record["bpm"], int):
        print("'bpm' is not an integer")
        return False
    # Check timestamp format
    timestamp = record.get("timestamp")
    if not timestamp or not re.match(ISO_8601_REGEX, timestamp):
        print("'timestamp' is missing or not ISO 8601 format")
        return False
    return True


def main():
    all_valid = True
    for record in run_simulator():
        if not validate_record(record):
            all_valid = False
    if all_valid:
        print("Success: Data is ready for Phase 2 Spark processing.")
    else:
        print("Validation failed.")

if __name__ == "__main__":
    main()
