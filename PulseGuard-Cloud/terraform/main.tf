# Terraform configuration for PulseGuard S3 bucket

provider "aws" {
  region = "us-east-1"
  # Consider using a named profile or environment variables for credentials
}

resource "aws_s3_bucket" "pulseguard_telemetry" {
  bucket = "pulseguard-telemetry-data-${random_id.suffix.hex}"
  force_destroy = true

  tags = {
    Name        = "PulseGuard Telemetry Data"
    Environment = "dev"
  }
}

# Enable versioning for data protection
resource "aws_s3_bucket_versioning" "pulseguard_versioning" {
  bucket = aws_s3_bucket.pulseguard_telemetry.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Enable server-side encryption by default
resource "aws_s3_bucket_server_side_encryption_configuration" "pulseguard_encryption" {
  bucket = aws_s3_bucket.pulseguard_telemetry.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "random_id" "suffix" {
  byte_length = 4
}

resource "aws_s3_bucket_public_access_block" "pulseguard_block" {
  bucket = aws_s3_bucket.pulseguard_telemetry.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

output "pulseguard_s3_bucket_name" {
  value = aws_s3_bucket.pulseguard_telemetry.bucket
}

# IAM user for secure S3 access
resource "aws_iam_user" "pulseguard_simulator" {
  name = "pulseguard-simulator"
}

# IAM policy for S3 access (read/write to the telemetry bucket only)
resource "aws_iam_policy" "pulseguard_s3_policy" {
  name        = "pulseguard-s3-access"
  description = "Allow only required S3 actions for PulseGuard telemetry bucket. Explicitly deny all others."
  policy      = jsonencode({
    Version = "2012-10-17",
    Statement = [
      # Allow only GetObject and PutObject on the bucket objects
      {
        Effect = "Allow",
        Action = [
          "s3:GetObject",
          "s3:PutObject"
        ],
        Resource = "${aws_s3_bucket.pulseguard_telemetry.arn}/*"
      },
      # (Optional) Allow ListBucket if your app needs to list objects
      # {
      #   Effect = "Allow",
      #   Action = ["s3:ListBucket"],
      #   Resource = aws_s3_bucket.pulseguard_telemetry.arn
      # },
      # Explicitly deny all other S3 actions on this bucket
      {
        Effect = "Deny",
        NotAction = [
          "s3:GetObject",
          "s3:PutObject"
          # "s3:ListBucket" # Uncomment if ListBucket is allowed
        ],
        Resource = [
          aws_s3_bucket.pulseguard_telemetry.arn,
          "${aws_s3_bucket.pulseguard_telemetry.arn}/*"
        ]
      }
    ]
  })
}

# S3 bucket policy for extra restriction (e.g., allow only from specific IP or VPC)
resource "aws_s3_bucket_policy" "pulseguard_restrict" {
  bucket = aws_s3_bucket.pulseguard_telemetry.id
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Deny",
        Principal = "*",
        Action = "s3:*",
        Resource = [
          aws_s3_bucket.pulseguard_telemetry.arn,
          "${aws_s3_bucket.pulseguard_telemetry.arn}/*"
        ],
        Condition = {
          Bool = { "aws:SecureTransport": "false" }
        }
      }
      # Add more conditions here for IP/VPC restrictions if needed
    ]
  })
}


# Attach policy to user
resource "aws_iam_user_policy_attachment" "pulseguard_simulator_attach" {
  user       = aws_iam_user.pulseguard_simulator.name
  policy_arn = aws_iam_policy.pulseguard_s3_policy.arn
}

# ---
# SECURITY NOTE:
# For production, prefer using IAM roles with temporary credentials (e.g., EC2, ECS, Lambda) instead of long-lived access keys.
# Rotate access keys regularly and monitor usage with AWS CloudTrail.
# ---

# Create access key for the user
resource "aws_iam_access_key" "pulseguard_simulator_key" {
  user = aws_iam_user.pulseguard_simulator.name
}

output "pulseguard_simulator_access_key_id" {
  value     = aws_iam_access_key.pulseguard_simulator_key.id
  sensitive = true
}

output "pulseguard_simulator_secret_access_key" {
  value     = aws_iam_access_key.pulseguard_simulator_key.secret
  sensitive = true
}
