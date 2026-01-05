import pytest
import json
import os
from pipeline import etl

def test_transform_data():
    data = {
        "DeviceID": "1",
        "PatientName": "alice smith",
        "DOB": "1980-05-12",
        "BPM": 80,
        "SpO2": 99,
        "Timestamp": "2026-01-04T12:00:00Z"
    }
    transformed = etl.transform_data(data.copy())
    assert transformed['PatientName'] == "ALICE SMITH"
    assert 'IngestedAt' in transformed

def test_schema_validation_valid():
    schema = etl.load_schema()
    valid_data = {
        "DeviceID": "1",
        "PatientName": "Alice Smith",
        "DOB": "1980-05-12",
        "BPM": 80,
        "SpO2": 99,
        "Timestamp": "2026-01-04T12:00:00Z"
    }
    # Should not raise
    etl.validate(instance=valid_data, schema=schema)

def test_schema_validation_invalid():
    schema = etl.load_schema()
    invalid_data = {
        "DeviceID": "1",
        "PatientName": "Alice Smith",
        # Missing DOB
        "BPM": 80,
        "SpO2": 99,
        "Timestamp": "2026-01-04T12:00:00Z"
    }
    with pytest.raises(Exception):
        etl.validate(instance=invalid_data, schema=schema)
