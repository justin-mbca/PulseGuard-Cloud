provider "aws" {
  region = "us-west-2"
}

# 0. Generate a random suffix for global uniqueness
resource "random_id" "suffix" {
  byte_length = 4
}

# --- NETWORKING LAYER ---

# 1. Dedicated VPC
resource "aws_vpc" "pulseguard_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags = { Name = "pulseguard-clinical-vpc" }
}

# 2. Internet Gateway (Required for the Bastion Host to talk to you)
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.pulseguard_vpc.id
  tags   = { Name = "pulseguard-igw" }
}

# 3. Subnets (A is Public for Bastion, B is Private for RDS)
resource "aws_subnet" "subnet_a" {
  vpc_id            = aws_vpc.pulseguard_vpc.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "us-west-2a"
  tags              = { Name = "pulseguard-subnet-public" }
}

resource "aws_subnet" "subnet_b" {
  vpc_id            = aws_vpc.pulseguard_vpc.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "us-west-2b"
  tags              = { Name = "pulseguard-subnet-private" }
}

# 4. Routing for Public Access
resource "aws_route_table" "public_rt" {
  vpc_id = aws_vpc.pulseguard_vpc.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }
}

resource "aws_route_table_association" "public_a" {
  subnet_id      = aws_subnet.subnet_a.id
  route_table_id = aws_route_table.public_rt.id
}

# 5. DB Subnet Group
resource "aws_db_subnet_group" "pulseguard_db_subnets" {
  name       = "pulseguard-db-subnets-${random_id.suffix.hex}"
  subnet_ids = [aws_subnet.subnet_a.id, aws_subnet.subnet_b.id]
}

# --- SECURITY GROUPS ---

# 6. Bastion Security Group (The Door)
resource "aws_security_group" "bastion_sg" {
  name   = "pulseguard-bastion-sg"
  vpc_id = aws_vpc.pulseguard_vpc.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # Recommendation: Change to your IP for production
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# 7. RDS Security Group (The Vault)
resource "aws_security_group" "rds_sg" {
  name   = "pulseguard-rds-sg"
  vpc_id = aws_vpc.pulseguard_vpc.id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.bastion_sg.id] # Only Bastion can enter
  }
}

# --- COMPUTE & STORAGE ---

# 8. Bastion Host Instance
resource "aws_instance" "bastion" {
  ami                         = "ami-05d38da78ce859165" # Amazon Linux 2023
  instance_type               = "t3.micro"
  subnet_id                   = aws_subnet.subnet_a.id
  vpc_security_group_ids      = [aws_security_group.bastion_sg.id]
  associate_public_ip_address = true
  key_name                    = "pulseguard-key" # Ensure this matches your AWS Key Pair name
  tags                        = { Name = "PulseGuard-Bastion" }
}

# 9. RDS Postgres Database
resource "aws_db_instance" "clinical_insights" {
  identifier           = "clinical-insights-v2"
  allocated_storage    = 20
  engine               = "postgres"
  engine_version       = "15"
  instance_class       = "db.t3.micro"
  db_name              = "clinical_insights"
  username             = "pulse_admin"
  password             = "changeMe123!"
  db_subnet_group_name = aws_db_subnet_group.pulseguard_db_subnets.name
  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  skip_final_snapshot  = true
  publicly_accessible  = false
}

# 10. S3 Bucket for Raw Telemetry
resource "aws_s3_bucket" "raw_telemetry" {
  bucket = "pulseguard-raw-telemetry-${random_id.suffix.hex}"
}

# --- OUTPUTS ---

output "bastion_public_ip" {
  value = aws_instance.bastion.public_ip
}

output "rds_endpoint" {
  value = aws_db_instance.clinical_insights.endpoint
}

output "s3_bucket_name" {
  value = aws_s3_bucket.raw_telemetry.id
}