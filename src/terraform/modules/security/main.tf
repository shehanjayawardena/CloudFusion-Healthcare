# Customer Managed Key (CMK) for Healthcare Envelope Encryption
resource "aws_kms_key" "healthcare" {
  description             = "KMS CMK for CloudFusion Healthcare Analytics (HIPAA/GDPR Compliant Data-at-Rest Encryption)"
  deletion_window_in_days = 30
  enable_key_rotation     = true

  tags = {
    Name = "${var.project_name}-${var.environment}-kms-key"
  }
}

resource "aws_kms_alias" "healthcare" {
  name          = "alias/${var.project_name}-${var.environment}-key"
  target_key_id = aws_kms_key.healthcare.key_id
}

# 1. Perimeter Security Group: Application Load Balancer
resource "aws_security_group" "alb" {
  name        = "${var.project_name}-${var.environment}-alb-sg"
  description = "Allows incoming HTTPS traffic from clients; egress to ECS tasks only"
  vpc_id      = var.vpc_id

  ingress {
    description = "Allow inbound HTTPS from Internet"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Allow inbound HTTP for redirection to HTTPS"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "Egress strictly to ECS Fargate tasks"
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["10.50.0.0/16"]
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-alb-sg"
  }
}

# 2. Application Security Group: ECS Fargate Microservices
resource "aws_security_group" "ecs" {
  name        = "${var.project_name}-${var.environment}-ecs-sg"
  description = "Allows ingress from ALB on port 8080; egress to DB, Redis, and HTTPS endpoints"
  vpc_id      = var.vpc_id

  ingress {
    description     = "Allow traffic from ALB only"
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    description = "Outbound HTTPS to AWS APIs, Secrets Manager, and KMS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "Outbound PostgreSQL traffic to Aurora"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["10.50.100.0/24", "10.50.110.0/24", "10.50.120.0/24"]
  }

  egress {
    description = "Outbound Redis traffic to ElastiCache"
    from_port   = 6379
    to_port     = 6379
    protocol    = "tcp"
    cidr_blocks = ["10.50.100.0/24", "10.50.110.0/24", "10.50.120.0/24"]
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-ecs-sg"
  }
}

# 3. Database Security Group: Amazon Aurora PostgreSQL
resource "aws_security_group" "database" {
  name        = "${var.project_name}-${var.environment}-db-sg"
  description = "Allows incoming PostgreSQL traffic strictly from ECS application tier"
  vpc_id      = var.vpc_id

  ingress {
    description     = "Inbound PostgreSQL from ECS microservices only"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs.id]
  }

  egress {
    description = "No outbound access permitted"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["127.0.0.1/32"]
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-db-sg"
  }
}

# 4. Cache Security Group: Amazon ElastiCache Redis
resource "aws_security_group" "cache" {
  name        = "${var.project_name}-${var.environment}-cache-sg"
  description = "Allows incoming Redis traffic strictly from ECS application tier"
  vpc_id      = var.vpc_id

  ingress {
    description     = "Inbound Redis from ECS microservices only"
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs.id]
  }

  egress {
    description = "No outbound access permitted"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["127.0.0.1/32"]
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-cache-sg"
  }
}
