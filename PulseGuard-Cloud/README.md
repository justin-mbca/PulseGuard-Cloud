# About Boston Scientific

Boston Scientific transforms lives through innovative medical technologies that improve the health of patients around the world. As a global medical technology leader for more than 40 years, we advance science for life by providing a broad range of high-performance solutions that address unmet patient needs and reduce the cost of health care. Our portfolio of devices and therapies helps physicians diagnose and treat complex cardiovascular, respiratory, digestive, oncological, neurological and urological diseases and conditions.

# Role Relevance: Medical Data Specialist II

This project demonstrates:
- Secure, HIPAA-compliant cloud data architecture (AWS, Terraform)
- Automated ETL pipelines and real-time data ingestion (Python, Spark, Lambda)
- Clinical data modeling (PostgreSQL, FHIR/HL7-ready schemas)
- API/data delivery design (RESTful, HL7/FHIR integration planned)
- Automation, monitoring, and compliance (CI/CD, CloudTrail, encryption)

# Skills Demonstrated

- **ETL Development:** Automated pipelines with Python, Spark, AWS Glue
- **Data Modeling:** Clinical schemas in PostgreSQL, FHIR/HL7-ready
- **Cloud Platforms:** HIPAA-compliant AWS setup
- **Programming:** Python, SQL, Spark
- **APIs & Integration:** (Planned) RESTful, HL7/FHIR
- **Automation:** Terraform, GitHub Actions

# Architecture Diagram (Mermaid)

```mermaid
flowchart TD
    VPC[VPC_HIPAA_boundary]
    subgraph Public_Subnet_10_0_1_0_24
        Bastion[Bastion_Host_EC2_API_Data_Ingestion]
        IGW[Internet_Gateway]
    end
    subgraph Private_Subnet_10_0_2_0_24
        RDS[RDS_clinical_insights_PostgreSQL_Encrypted_Audit]
        MySQL[MySQL]
        Mongo[MongoDB]
        Dynamo[DynamoDB]
    end
    S3[S3_Bucket_Raw_Processed_Data]
    Glue[AWS_Glue]
    Lambda[AWS_Lambda]
    EMR[AWS_EMR]
    Spark[Spark_Scala]
    Flink[Flink]
    Kafka[Kafka]
    Athena[Athena]
    QuickSight[QuickSight]
    Streamlit[Streamlit]
    FHIR[FHIR_HL7_OMOP]
    API[RESTful_API_HL7_FHIR]
    KMS[KMS]
    Secrets[Secrets_Manager]
    CloudTrail[CloudTrail]
    Activity[Activity_Streams]
    GH[GitHub_Actions]
    NAT[NAT_Gateway]
    TF[Terraform]
    ECS[ECS]

    VPC --> IGW
    IGW --> Bastion
    VPC --> NAT
    Bastion --> API
    API --> Lambda
    API --> Glue
    API --> Kafka
    Lambda --> Glue
    Lambda --> EMR
    Glue --> EMR
    Glue --> Spark
    Kafka --> Flink
    Flink --> EMR
    Spark --> EMR
    EMR --> S3
    Glue --> S3
    Lambda --> S3
    API --> RDS
    API --> MySQL
    API --> Mongo
    API --> Dynamo
    S3 --> Athena
    S3 --> QuickSight
    S3 --> Streamlit
    RDS --> Athena
    RDS --> QuickSight
    RDS --> Streamlit
    FHIR --> API
    FHIR --> RDS
    FHIR --> Glue
    KMS -.-> S3
    KMS -.-> RDS
    KMS -.-> MySQL
    KMS -.-> Dynamo
    Secrets -.-> Lambda
    Secrets -.-> Glue
    Secrets -.-> EMR
    CloudTrail -.-> RDS
    CloudTrail -.-> S3
    Activity -.-> RDS
    Activity -.-> S3
    GH -.-> TF
    TF --> VPC
    TF --> IGW
    TF --> NAT
    TF --> Bastion
    TF --> ECS
    TF --> RDS
    TF --> S3
    TF --> MySQL
    TF --> Mongo
    TF --> Dynamo
```
