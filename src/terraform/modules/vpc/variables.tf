variable "project_name" {
  type        = string
  description = "Project name prefix"
}

variable "environment" {
  type        = string
  description = "Environment name"
}

variable "vpc_cidr" {
  type        = string
  description = "CIDR block for the VPC"
}

variable "availability_zones" {
  type        = list(string)
  description = "List of availability zones"
}

variable "public_subnet_cidrs" {
  type        = list(string)
  description = "CIDR blocks for public subnets"
}

variable "private_app_subnet_cidrs" {
  type        = list(string)
  description = "CIDR blocks for private application subnets"
}

variable "private_db_subnet_cidrs" {
  type        = list(string)
  description = "CIDR blocks for private database subnets"
}
