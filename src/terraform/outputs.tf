output "vpc_id" {
  description = "The ID of the CloudFusion VPC"
  value       = module.vpc.vpc_id
}

output "public_subnet_ids" {
  description = "List of public subnet IDs"
  value       = module.vpc.public_subnet_ids
}

output "private_app_subnet_ids" {
  description = "List of private application subnet IDs"
  value       = module.vpc.private_app_subnet_ids
}

output "private_db_subnet_ids" {
  description = "List of private database subnet IDs"
  value       = module.vpc.private_db_subnet_ids
}

output "alb_dns_name" {
  description = "Public DNS name of the Application Load Balancer"
  value       = module.ecs_fargate.alb_dns_name
}

output "ecs_cluster_name" {
  description = "Name of the ECS Fargate cluster"
  value       = module.ecs_fargate.cluster_name
}

output "aurora_endpoint" {
  description = "Writer endpoint for the Amazon Aurora PostgreSQL cluster"
  value       = module.database.aurora_cluster_endpoint
}

output "aurora_reader_endpoint" {
  description = "Reader endpoint for the Amazon Aurora PostgreSQL cluster"
  value       = module.database.aurora_cluster_reader_endpoint
}

output "dynamodb_telemetry_table_name" {
  description = "Name of the DynamoDB table storing patient IoT telemetry"
  value       = module.database.dynamodb_table_name
}

output "s3_medical_data_lake_bucket" {
  description = "S3 bucket for the healthcare data lake and historical archives"
  value       = module.database.s3_bucket_name
}

output "kms_healthcare_key_arn" {
  description = "ARN of the Customer Managed KMS Key for healthcare encryption"
  value       = module.security.kms_healthcare_key_arn
}

output "frontend_website_url" {
  description = "Live Public AWS URL for the CloudFusion HealthPulse Frontend on Amazon S3"
  value       = module.frontend_s3.website_url
}

output "sagemaker_endpoint_name" {
  description = "Name of the deployed Amazon SageMaker Serverless Inference Endpoint"
  value       = module.sagemaker.sagemaker_endpoint_name
}

output "sagemaker_model_name" {
  description = "Name of the Amazon SageMaker Model"
  value       = module.sagemaker.sagemaker_model_name
}
