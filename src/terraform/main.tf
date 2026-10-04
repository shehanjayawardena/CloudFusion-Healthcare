# CloudFusion Healthcare Analytics Ltd (CHA)
# Root Terraform Orchestration Configuration

module "vpc" {
  source = "./modules/vpc"

  project_name             = var.project_name
  environment              = var.environment
  vpc_cidr                 = var.vpc_cidr
  availability_zones       = var.availability_zones
  public_subnet_cidrs      = var.public_subnet_cidrs
  private_app_subnet_cidrs = var.private_app_subnet_cidrs
  private_db_subnet_cidrs  = var.private_db_subnet_cidrs
}

module "security" {
  source = "./modules/security"

  project_name = var.project_name
  environment  = var.environment
  vpc_id       = module.vpc.vpc_id
}

module "ecs_fargate" {
  source = "./modules/ecs_fargate"

  project_name             = var.project_name
  environment              = var.environment
  vpc_id                   = module.vpc.vpc_id
  public_subnet_ids        = module.vpc.public_subnet_ids
  private_app_subnet_ids   = module.vpc.private_app_subnet_ids
  alb_security_group_id    = module.security.alb_security_group_id
  ecs_security_group_id    = module.security.ecs_security_group_id
  kms_key_arn              = module.security.kms_healthcare_key_arn
  ecs_min_capacity         = var.ecs_min_capacity
  ecs_max_capacity         = var.ecs_max_capacity
}

module "database" {
  source = "./modules/database"

  project_name            = var.project_name
  environment             = var.environment
  vpc_id                  = module.vpc.vpc_id
  private_db_subnet_ids   = module.vpc.private_db_subnet_ids
  database_security_group = module.security.database_security_group_id
  kms_key_arn             = module.security.kms_healthcare_key_arn
  aurora_min_capacity     = var.aurora_min_capacity
  aurora_max_capacity     = var.aurora_max_capacity
  master_username         = var.database_master_username
}

module "frontend_s3" {
  source = "./modules/frontend_s3"

  project_name = var.project_name
  environment  = var.environment
}
