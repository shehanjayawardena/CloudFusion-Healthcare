output "kms_healthcare_key_arn" {
  description = "ARN of the healthcare Customer Managed KMS Key"
  value       = aws_kms_key.healthcare.arn
}

output "kms_healthcare_key_id" {
  description = "ID of the healthcare Customer Managed KMS Key"
  value       = aws_kms_key.healthcare.key_id
}

output "alb_security_group_id" {
  description = "ID of the ALB security group"
  value       = aws_security_group.alb.id
}

output "ecs_security_group_id" {
  description = "ID of the ECS Fargate tasks security group"
  value       = aws_security_group.ecs.id
}

output "database_security_group_id" {
  description = "ID of the Aurora database security group"
  value       = aws_security_group.database.id
}

output "cache_security_group_id" {
  description = "ID of the ElastiCache Redis security group"
  value       = aws_security_group.cache.id
}
