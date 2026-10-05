# Amazon SageMaker Machine Learning Infrastructure as Code
# Module: COMP60010 - Enterprise Cloud and Distributed Web Applications
# Author: Shehan Jaye (CB012510) | AWS Account: 460060049985
# Target AWS Region: ap-southeast-1 (Singapore)

data "aws_region" "current" {}
data "aws_caller_identity" "current" {}

# 1. IAM Execution Role for Amazon SageMaker
resource "aws_iam_role" "sagemaker_execution_role" {
  name        = "${var.project_name}-sagemaker-execution-role-${var.environment}"
  description = "Execution role granting SageMaker permission to access S3 Data Lake, KMS, and CloudWatch Logs"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "sagemaker.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-sagemaker-execution-role"
    Environment = var.environment
    ManagedBy   = "Terraform"
    Project     = "CloudFusion-Healthcare-Analytics"
  }
}

# Attach AWS managed policy for SageMaker operations
resource "aws_iam_role_policy_attachment" "sagemaker_core" {
  role       = aws_iam_role.sagemaker_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSageMakerFullAccess"
}

# Custom least-privilege policy for S3 Data Lake & KMS Encryption
resource "aws_iam_policy" "sagemaker_datalake_access" {
  name        = "${var.project_name}-sagemaker-datalake-policy-${var.environment}"
  description = "Allows SageMaker to read training datasets and read/write model artifacts in S3 Data Lake"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "S3DataLakeReadWrite"
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::${var.data_lake_bucket_name}",
          "arn:aws:s3:::${var.data_lake_bucket_name}/*"
        ]
      },
      {
        Sid    = "CloudWatchLogging"
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Sid    = "KMSAccess"
        Effect = "Allow"
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:DescribeKey"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "sagemaker_datalake_attach" {
  role       = aws_iam_role.sagemaker_execution_role.name
  policy_arn = aws_iam_policy.sagemaker_datalake_access.arn
}

# 2. SageMaker Model Definition
# Uses official AWS XGBoost inference container for Singapore (ap-southeast-1)
locals {
  xgboost_container = "475088407865.dkr.ecr.${data.aws_region.current.name}.amazonaws.com/sagemaker-xgboost:1.5-1"
}

resource "aws_sagemaker_model" "sepsis_predictor" {
  name               = "${var.project_name}-sepsis-predictor-${var.environment}"
  execution_role_arn = aws_iam_role.sagemaker_execution_role.arn

  primary_container {
    image          = local.xgboost_container
    model_data_url = "s3://${var.data_lake_bucket_name}/${var.model_s3_key}"

    environment = {
      SAGEMAKER_PROGRAM          = "inference.py"
      SAGEMAKER_SUBMIT_DIRECTORY = "s3://${var.data_lake_bucket_name}/${var.model_s3_key}"
    }
  }

  tags = {
    Name        = "${var.project_name}-sepsis-predictor-model"
    Environment = var.environment
    ManagedBy   = "Terraform"
    Project     = "CloudFusion-Healthcare-Analytics"
  }
}

# 3. SageMaker Serverless Endpoint Configuration
# Zero idle cost ($0.00 base charge) - scales down to 0 when idle
resource "aws_sagemaker_endpoint_configuration" "sepsis_serverless_cfg" {
  name = "${var.project_name}-sepsis-serverless-cfg-${var.environment}"

  production_variants {
    variant_name = "AllTraffic"
    model_name   = aws_sagemaker_model.sepsis_predictor.name

    serverless_config {
      memory_size_in_mb = var.serverless_memory_size_mb
      max_concurrency   = var.serverless_max_concurrency
    }
  }

  tags = {
    Name        = "${var.project_name}-sepsis-serverless-endpoint-config"
    Environment = var.environment
    FinOps      = "Serverless-ZeroIdleCost"
    ManagedBy   = "Terraform"
    Project     = "CloudFusion-Healthcare-Analytics"
  }
}

# 4. SageMaker Real-Time / Serverless Endpoint
resource "aws_sagemaker_endpoint" "sepsis_endpoint" {
  name                 = "${var.project_name}-sepsis-prediction-endpoint-${var.environment}"
  endpoint_config_name = aws_sagemaker_endpoint_configuration.sepsis_serverless_cfg.name

  tags = {
    Name        = "${var.project_name}-sepsis-prediction-endpoint"
    Environment = var.environment
    ManagedBy   = "Terraform"
    Project     = "CloudFusion-Healthcare-Analytics"
  }
}

# 5. S3 Upload for Training Dataset
resource "aws_s3_object" "training_dataset" {
  bucket = var.data_lake_bucket_name
  key    = "ml-training/train_vitals.csv"
  source = "${path.root}/../ml/data/train_vitals_xgboost.csv"
  etag   = filemd5("${path.root}/../ml/data/train_vitals_xgboost.csv")
}

