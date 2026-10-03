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

variable "public_subnet_ids" {
  type        = list(string)
  description = "Public subnet IDs for the ALB"
}

variable "private_app_subnet_ids" {
  type        = list(string)
  description = "Private application subnet IDs for ECS tasks"
}

variable "alb_security_group_id" {
  type        = string
  description = "Security Group ID for the ALB"
}

variable "ecs_security_group_id" {
  type        = string
  description = "Security Group ID for ECS tasks"
}

variable "kms_key_arn" {
  type        = string
  description = "KMS Key ARN for secret decryption and log encryption"
}

variable "ecs_min_capacity" {
  type        = number
  description = "Minimum ECS task count"
}

variable "ecs_max_capacity" {
  type        = number
  description = "Maximum ECS task count"
}
