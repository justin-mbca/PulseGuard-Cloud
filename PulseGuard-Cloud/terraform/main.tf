  region = "us-east-1"
}

  bucket = "raw-zone"
  force_destroy = true
}

  allocated_storage    = 20
  storage_type         = "gp2"
  engine               = "postgres"
  engine_version       = "15.3"
  instance_class       = "db.t3.micro"
  name                 = "pulseguarddb"
  username             = "admin"
  password             = "changeMe123!"
  parameter_group_name = "default.postgres15"
  skip_final_snapshot  = true
}
provider "aws" {
  region = "us-west-2"
}

resource "aws_s3_bucket" "raw_telemetry" {
  bucket = "pulseguard-raw-telemetry"
  force_destroy = true

  versioning {
    enabled = true
  }

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
}

resource "aws_s3_bucket_public_access_block" "raw_telemetry_block" {
  bucket                  = aws_s3_bucket.raw_telemetry.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_db_instance" "clinical_insights" {
  allocated_storage    = 20
  storage_type         = "gp2"
  engine               = "postgres"
  engine_version       = "15.3"
  instance_class       = "db.t3.micro"
  name                 = "clinical_insights"
  username             = "admin"
  password             = "changeMe123!"
  parameter_group_name = "default.postgres15"
  skip_final_snapshot  = true
  storage_encrypted    = true
  publicly_accessible  = false
}

output "s3_bucket_arn" {
  value = aws_s3_bucket.raw_telemetry.arn
}

output "rds_endpoint" {
  value = aws_db_instance.clinical_insights.endpoint
}
