output "aurora_cluster_endpoint" {
  description = "Writer endpoint for the clinical PostgreSQL database"
  value       = aws_db_instance.aurora.endpoint
}

output "aurora_cluster_reader_endpoint" {
  description = "Reader endpoint for the clinical PostgreSQL database"
  value       = aws_db_instance.aurora.endpoint
}

output "aurora_cluster_id" {
  description = "ID of the database instance"
  value       = aws_db_instance.aurora.id
}

output "dynamodb_table_name" {
  description = "Name of the DynamoDB table for patient telemetry"
  value       = aws_dynamodb_table.patient_telemetry.name
}

output "dynamodb_table_arn" {
  description = "ARN of the DynamoDB table for patient telemetry"
  value       = aws_dynamodb_table.patient_telemetry.arn
}

output "s3_bucket_name" {
  description = "Name of the S3 medical data lake bucket"
  value       = aws_s3_bucket.medical_data_lake.bucket
}

output "s3_bucket_arn" {
  description = "ARN of the S3 medical data lake bucket"
  value       = aws_s3_bucket.medical_data_lake.arn
}
