# ECS Cluster with Container Insights Enabled
resource "aws_ecs_cluster" "main" {
  name = "${var.project_name}-${var.environment}-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-ecs-cluster"
  }
}

# Capacity Provider Strategy: Blend FARGATE with FARGATE_SPOT for 40%+ Cost Reduction
resource "aws_ecs_cluster_capacity_providers" "main" {
  cluster_name = aws_ecs_cluster.main.name

  capacity_providers = ["FARGATE", "FARGATE_SPOT"]

  default_capacity_provider_strategy {
    capacity_provider = "FARGATE"
    weight            = 1
    base              = 2
  }

  default_capacity_provider_strategy {
    capacity_provider = "FARGATE_SPOT"
    weight            = 3
  }
}

# Application Load Balancer
resource "aws_lb" "main" {
  name               = "${var.project_name}-${var.environment}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [var.alb_security_group_id]
  subnets            = var.public_subnet_ids

  enable_deletion_protection = false

  tags = {
    Name = "${var.project_name}-${var.environment}-alb"
  }
}

# Target Group: Telemedicine and Patient Portal (TPP) API
resource "aws_lb_target_group" "tpp" {
  name        = "${var.project_name}-${var.environment}-tpp-tg"
  port        = 8080
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"

  health_check {
    enabled             = true
    path                = "/health"
    protocol            = "HTTP"
    port                = "8080"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 3
    unhealthy_threshold = 3
    matcher             = "200"
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-tpp-tg"
  }
}

# Target Group: Patient Monitoring Platform (PMP) Ingestion
resource "aws_lb_target_group" "pmp" {
  name        = "${var.project_name}-${var.environment}-pmp-tg"
  port        = 8080
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"

  health_check {
    enabled             = true
    path                = "/health"
    protocol            = "HTTP"
    port                = "8080"
    interval            = 15
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 3
    matcher             = "200"
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-pmp-tg"
  }
}

# ALB HTTP Listener (Port 80 -> Redirect to HTTPS)
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type = "redirect"

    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}

# ALB Mock HTTPS Listener (Port 443 with self-signed / ACM cert placeholder)
resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.main.arn
  port              = "443"
  protocol          = "HTTP" # In production, set to HTTPS with certificate_arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.tpp.arn
  }
}

# ALB Listener Rule for PMP Telemetry Endpoint
resource "aws_lb_listener_rule" "pmp_rule" {
  listener_arn = aws_lb_listener.https.arn
  priority     = 10

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.pmp.arn
  }

  condition {
    path_pattern {
      values = ["/api/v1/pmp/*", "/api/v1/telemetry/*"]
    }
  }
}

# CloudWatch Log Group for Encrypted Container Logging
resource "aws_cloudwatch_log_group" "ecs_logs" {
  name              = "/ecs/${var.project_name}-${var.environment}"
  retention_in_days = 90
  kms_key_id        = var.kms_key_arn

  tags = {
    Name = "${var.project_name}-${var.environment}-ecs-logs"
  }
}

# IAM Role for ECS Task Execution
resource "aws_iam_role" "ecs_execution_role" {
  name = "${var.project_name}-${var.environment}-ecs-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_execution_standard" {
  role       = aws_iam_role.ecs_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# IAM Role for ECS Application Tasks
resource "aws_iam_role" "ecs_task_role" {
  name = "${var.project_name}-${var.environment}-ecs-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

# Task Definition: TPP API Service
resource "aws_ecs_task_definition" "tpp_api" {
  family                   = "${var.project_name}-${var.environment}-tpp-api"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "2048"
  memory                   = "4096"
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name      = "tpp-api"
      image     = "public.ecr.aws/docker/library/node:18-alpine"
      essential = true
      portMappings = [
        {
          containerPort = 8080
          hostPort      = 8080
          protocol      = "tcp"
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.ecs_logs.name
          "awslogs-region"        = "ap-southeast-1"
          "awslogs-stream-prefix" = "tpp-api"
        }
      }
      environment = [
        { name = "NODE_ENV", value = var.environment },
        { name = "PORT", value = "8080" }
      ]
    }
  ])
}

# Task Definition: PMP Real-Time Ingestion Service
resource "aws_ecs_task_definition" "pmp_ingestion" {
  family                   = "${var.project_name}-${var.environment}-pmp-ingestion"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "1024"
  memory                   = "2048"
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name      = "pmp-ingestion"
      image     = "public.ecr.aws/docker/library/python:3.11-slim"
      essential = true
      portMappings = [
        {
          containerPort = 8080
          hostPort      = 8080
          protocol      = "tcp"
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.ecs_logs.name
          "awslogs-region"        = "ap-southeast-1"
          "awslogs-stream-prefix" = "pmp-ingestion"
        }
      }
      environment = [
        { name = "SERVICE_NAME", value = "PMP-Ingestion" },
        { name = "ENV", value = var.environment }
      ]
    }
  ])
}

# ECS Service: TPP API
resource "aws_ecs_service" "tpp_api" {
  name            = "${var.project_name}-${var.environment}-tpp-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.tpp_api.arn
  desired_count   = var.ecs_min_capacity

  capacity_provider_strategy {
    capacity_provider = "FARGATE"
    weight            = 1
    base              = 2
  }

  capacity_provider_strategy {
    capacity_provider = "FARGATE_SPOT"
    weight            = 3
  }

  network_configuration {
    subnets          = var.private_app_subnet_ids
    security_groups  = [var.ecs_security_group_id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.tpp.arn
    container_name   = "tpp-api"
    container_port   = 8080
  }

  depends_on = [aws_lb_listener.https]
}

# ECS Service: PMP Ingestion
resource "aws_ecs_service" "pmp_ingestion" {
  name            = "${var.project_name}-${var.environment}-pmp-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.pmp_ingestion.arn
  desired_count   = var.ecs_min_capacity

  capacity_provider_strategy {
    capacity_provider = "FARGATE"
    weight            = 1
    base              = 2
  }

  capacity_provider_strategy {
    capacity_provider = "FARGATE_SPOT"
    weight            = 3
  }

  network_configuration {
    subnets          = var.private_app_subnet_ids
    security_groups  = [var.ecs_security_group_id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.pmp.arn
    container_name   = "pmp-ingestion"
    container_port   = 8080
  }

  depends_on = [aws_lb_listener.https]
}

# Auto Scaling Target for TPP API
resource "aws_appautoscaling_target" "tpp_scale_target" {
  max_capacity       = var.ecs_max_capacity
  min_capacity       = var.ecs_min_capacity
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.tpp_api.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

# Auto Scaling Policy: Target Tracking CPU Utilization (65%)
resource "aws_appautoscaling_policy" "tpp_cpu_policy" {
  name               = "${var.project_name}-${var.environment}-tpp-cpu-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.tpp_scale_target.resource_id
  scalable_dimension = aws_appautoscaling_target.tpp_scale_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.tpp_scale_target.service_namespace

  target_tracking_scaling_policy_configuration {
    target_value       = 65.0
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    scale_in_cooldown  = 300
    scale_out_cooldown = 60
  }
}
