variable "aws_region" {
  description = "The AWS region to deploy the CloudFusion healthcare infrastructure"
  type        = string
  default     = "ap-southeast-1"
}

variable "environment" {
  description = "Deployment environment (e.g., prod, staging, dev)"
  type        = string
  default     = "prod"
}

variable "project_name" {
  description = "Project name prefix used for resource naming"
  type        = string
  default     = "cha-healthcare"
}

variable "vpc_cidr" {
  description = "CIDR block for the CloudFusion VPC"
  type        = string
  default     = "10.50.0.0/16"
}

variable "availability_zones" {
  description = "List of Availability Zones to deploy resources across"
  type        = list(string)
  default     = ["ap-southeast-1a", "ap-southeast-1b", "ap-southeast-1c"]
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for the public subnets (ALB, NAT Gateways)"
  type        = list(string)
  default     = ["10.50.1.0/24", "10.50.2.0/24", "10.50.3.0/24"]
}

variable "private_app_subnet_cidrs" {
  description = "CIDR blocks for private application subnets (ECS Fargate, Lambda)"
  type        = list(string)
  default     = ["10.50.10.0/24", "10.50.20.0/24", "10.50.30.0/24"]
}

variable "private_db_subnet_cidrs" {
  description = "CIDR blocks for private database subnets (Aurora, ElastiCache)"
  type        = list(string)
  default     = ["10.50.100.0/24", "10.50.110.0/24", "10.50.120.0/24"]
}

variable "aurora_min_capacity" {
  description = "Minimum ACU (Aurora Capacity Units) for Aurora Serverless v2"
  type        = number
  default     = 0.5
}

variable "aurora_max_capacity" {
  description = "Maximum ACU (Aurora Capacity Units) for Aurora Serverless v2"
  type        = number
  default     = 4.0
}

variable "database_master_username" {
  description = "Master username for the Aurora PostgreSQL cluster"
  type        = string
  default     = "cha_db_admin"
}

variable "ecs_min_capacity" {
  description = "Minimum number of ECS Fargate tasks across all AZs"
  type        = number
  default     = 6
}

variable "ecs_max_capacity" {
  description = "Maximum number of ECS Fargate tasks under peak load"
  type        = number
  default     = 60
}
