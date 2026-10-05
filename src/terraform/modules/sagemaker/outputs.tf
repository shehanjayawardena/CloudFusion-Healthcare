# Amazon SageMaker Terraform Outputs
# Module: COMP60010 - Enterprise Cloud and Distributed Web Applications
# Author: Shehan Jaye (CB012510) | AWS Account: 460060049985

output "sagemaker_execution_role_arn" {
  description = "ARN of the SageMaker Execution Role"
  value       = aws_iam_role.sagemaker_execution_role.arn
}

output "sagemaker_model_name" {
  description = "Name of the registered SageMaker Model"
  value       = aws_sagemaker_model.sepsis_predictor.name
}

output "sagemaker_endpoint_config_name" {
  description = "Name of the SageMaker Serverless Endpoint Configuration"
  value       = aws_sagemaker_endpoint_configuration.sepsis_serverless_cfg.name
}

output "sagemaker_endpoint_name" {
  description = "Name of the deployed SageMaker Serverless Endpoint"
  value       = aws_sagemaker_endpoint.sepsis_endpoint.name
}

output "sagemaker_endpoint_arn" {
  description = "ARN of the deployed SageMaker Serverless Endpoint"
  value       = aws_sagemaker_endpoint.sepsis_endpoint.arn
}
