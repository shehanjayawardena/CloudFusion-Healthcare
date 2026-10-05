# Amazon SageMaker Machine Learning Terraform Variables
# Module: COMP60010 - Enterprise Cloud and Distributed Web Applications
# Author: Shehan Jaye (CB012510) | AWS Account: 460060049985

variable "project_name" {
  description = "Project name identifier"
  type        = string
  default     = "cha-healthcare"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "prod"
}

variable "kms_key_arn" {
  description = "ARN of KMS Customer Managed Key for encrypting ML artifacts and endpoints"
  type        = string
  default     = ""
}

variable "data_lake_bucket_name" {
  description = "S3 Data Lake bucket name holding training vitals and model artifacts"
  type        = string
  default     = "cha-healthcare-prod-lake-460060049985"
}

variable "model_s3_key" {
  description = "S3 object key for the packaged SageMaker model archive (model.tar.gz)"
  type        = string
  default     = "ml-models/sepsis/model.tar.gz"
}

variable "serverless_memory_size_mb" {
  description = "Memory allocated for Serverless SageMaker inference (MB)"
  type        = number
  default     = 2048
}

variable "serverless_max_concurrency" {
  description = "Maximum concurrent invocations for Serverless SageMaker endpoint"
  type        = number
  default     = 20
}
