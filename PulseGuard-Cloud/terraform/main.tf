# Terraform configuration for PulseGuard S3 bucket

provider "aws" {
  region = "us-east-1"
}

resource "aws_s3_bucket" "pulseguard_telemetry" {
  bucket = "pulseguard-telemetry-data-${random_id.suffix.hex}"
  force_destroy = true

  tags = {
    Name        = "PulseGuard Telemetry Data"
    Environment = "dev"
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
  description = "Allow read/write access to PulseGuard telemetry S3 bucket."
  policy      = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.pulseguard_telemetry.arn,
          "${aws_s3_bucket.pulseguard_telemetry.arn}/*"
        ]
      }
    ]
  })
}

# Attach policy to user
resource "aws_iam_user_policy_attachment" "pulseguard_simulator_attach" {
  user       = aws_iam_user.pulseguard_simulator.name
  policy_arn = aws_iam_policy.pulseguard_s3_policy.arn
}

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
