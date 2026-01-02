# PulseGuard-Cloud

**Scalable HIPAA-compliant pipeline for real-time medical device telemetry**

PulseGuard-Cloud is designed for Medical Data Specialists to securely ingest, process, and analyze real-time telemetry from medical devices. The pipeline supports synthetic and real data, ensuring compliance and scalability for healthcare environments.

## Project Structure

- `/simulator` — Python script for generating synthetic heart rate telemetry (BPM, SpO2, DeviceID, PatientName, DOB) in JSON format.
- `/terraform` — Infrastructure as Code for AWS S3 bucket (`raw-zone`) and PostgreSQL database on RDS.
- `/spark_jobs` — PySpark scripts for scalable data processing.
- `/scripts` — Deployment and automation scripts.

## Key Features
- Real-time ingestion of medical telemetry
- Synthetic data generation for testing
- Scalable Spark-based analytics
- Secure AWS S3 storage and managed PostgreSQL
- HIPAA-compliant design

## Target Audience
**Medical Data Specialists** seeking robust, compliant, and scalable solutions for medical device data pipelines.
