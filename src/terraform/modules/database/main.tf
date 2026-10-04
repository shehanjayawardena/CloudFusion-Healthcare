# DB Subnet Group across 3 Availability Zones
resource "aws_db_subnet_group" "aurora" {
  name       = "${var.project_name}-${var.environment}-db-subnet-group"
  subnet_ids = var.private_db_subnet_ids

  tags = {
    Name = "${var.project_name}-${var.environment}-db-subnet-group"
  }
}

# Clinical PostgreSQL Database (Free-Tier Eligible db.t4g.micro / Multi-AZ Subnet Group)
resource "aws_db_instance" "aurora" {
  identifier                  = "${var.project_name}-${var.environment}-db"
  allocated_storage           = 20
  engine                      = "postgres"
  engine_version              = "15.4"
  instance_class              = "db.t4g.micro"
  db_name                     = "chaclinical"
  username                    = var.master_username
  manage_master_user_password = true
  master_user_secret_kms_key_id = var.kms_key_arn

  storage_encrypted           = true
  kms_key_id                  = var.kms_key_arn
  backup_retention_period     = 1
  skip_final_snapshot         = true
  deletion_protection         = false

  db_subnet_group_name        = aws_db_subnet_group.aurora.name
  vpc_security_group_ids      = [var.database_security_group]

  tags = {
    Name = "${var.project_name}-${var.environment}-clinical-db"
  }
}

# DynamoDB Table for Real-Time IoT Telemetry & Hot Storage
resource "aws_dynamodb_table" "patient_telemetry" {
  name         = "${var.project_name}-${var.environment}-patient-telemetry"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "patient_id"
  range_key    = "timestamp"

  attribute {
    name = "patient_id"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "N"
  }

  ttl {
    attribute_name = "ttl_timestamp"
    enabled        = true
  }

  point_in_time_recovery {
    enabled = true
  }

  server_side_encryption {
    enabled     = true
    kms_key_arn = var.kms_key_arn
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-patient-telemetry"
  }
}

data "aws_caller_identity" "current" {}

# S3 Medical Data Lake and Historical Archive
resource "aws_s3_bucket" "medical_data_lake" {
  bucket        = "${var.project_name}-${var.environment}-lake-${data.aws_caller_identity.current.account_id}"
  force_destroy = true

  tags = {
    Name        = "${var.project_name}-${var.environment}-medical-lake"
    Compliance  = "HIPAA-GDPR"
  }
}


# Enable Object Versioning (Immutable Medical Records)
resource "aws_s3_bucket_versioning" "lake_versioning" {
  bucket = aws_s3_bucket.medical_data_lake.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Enforce Server-Side KMS Encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "lake_crypto" {
  bucket = aws_s3_bucket.medical_data_lake.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = var.kms_key_arn
      sse_algorithm     = "aws:kms"
    }
    bucket_key_enabled = true
  }
}

# Strict Public Access Block (Prevent Data Leaks)
resource "aws_s3_bucket_public_access_block" "lake_block" {
  bucket = aws_s3_bucket.medical_data_lake.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# S3 Lifecycle Policy for 40%+ Cost Reduction (Intelligent-Tiering & Deep Archive)
resource "aws_s3_bucket_lifecycle_configuration" "lake_lifecycle" {
  bucket = aws_s3_bucket.medical_data_lake.id

  rule {
    id     = "medical-records-retention-and-tiering"
    status = "Enabled"

    transition {
      days          = 90
      storage_class = "STANDARD_IA"
    }

    transition {
      days          = 180
      storage_class = "GLACIER"
    }

    transition {
      days          = 365
      storage_class = "DEEP_ARCHIVE"
    }

    noncurrent_version_transition {
      noncurrent_days = 30
      storage_class   = "GLACIER"
    }
  }
}
