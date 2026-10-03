output "cluster_name" {
  description = "Name of the ECS Cluster"
  value       = aws_ecs_cluster.main.name
}

output "cluster_arn" {
  description = "ARN of the ECS Cluster"
  value       = aws_ecs_cluster.main.arn
}

output "alb_dns_name" {
  description = "DNS name of the ALB"
  value       = aws_lb.main.dns_name
}

output "alb_arn" {
  description = "ARN of the ALB"
  value       = aws_lb.main.arn
}

output "pmp_service_name" {
  description = "Name of the PMP ingestion ECS service"
  value       = aws_ecs_service.pmp_ingestion.name
}

output "tpp_service_name" {
  description = "Name of the TPP API ECS service"
  value       = aws_ecs_service.tpp_api.name
}
