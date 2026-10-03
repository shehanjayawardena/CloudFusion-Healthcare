variable "project_name" {
  type        = string
  description = "Project name prefix"
}

variable "environment" {
  type        = string
  description = "Environment name"
}

variable "vpc_id" {
  type        = string
  description = "VPC ID"
}

variable "private_db_subnet_ids" {
  type        = list(string)
  description = "Subnet IDs for DB subnet group"
}

variable "database_security_group" {
  type        = string
  description = "Security Group ID for Aurora DB"
}

variable "kms_key_arn" {
  type        = string
  description = "KMS Key ARN for storage encryption"
}

variable "aurora_min_capacity" {
  type        = number
  description = "Minimum ACU for Aurora Serverless v2"
}

variable "aurora_max_capacity" {
  type        = number
  description = "Maximum ACU for Aurora Serverless v2"
}

variable "master_username" {
  type        = string
  description = "Master username for Aurora PostgreSQL"
}
