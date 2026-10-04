# S3 Static Website Hosting for CloudFusion HealthPulse Frontend
# Provides a live public AWS URL in Singapore (ap-southeast-1)

data "aws_caller_identity" "current" {}

resource "aws_s3_bucket" "frontend" {
  bucket        = "cha-healthpulse-web-${data.aws_caller_identity.current.account_id}"
  force_destroy = true

  tags = {
    Name        = "cha-healthpulse-web-frontend"
    Environment = var.environment
    ManagedBy   = "Terraform"
    Project     = "CloudFusion-Healthcare-Analytics"
  }
}

resource "aws_s3_bucket_website_configuration" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  index_document {
    suffix = "index.html"
  }

  error_document {
    key = "index.html"
  }
}

resource "aws_s3_bucket_public_access_block" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_policy" "frontend" {
  depends_on = [aws_s3_bucket_public_access_block.frontend]
  bucket     = aws_s3_bucket.frontend.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "PublicReadGetObject"
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:GetObject"
        Resource  = "${aws_s3_bucket.frontend.arn}/*"
      }
    ]
  })
}

# Upload Frontend Artifacts with proper Content-Type headers
resource "aws_s3_object" "index" {
  bucket       = aws_s3_bucket.frontend.id
  key          = "index.html"
  source       = "${path.root}/../frontend/index.html"
  etag         = filemd5("${path.root}/../frontend/index.html")
  content_type = "text/html"
}

resource "aws_s3_object" "styles" {
  bucket       = aws_s3_bucket.frontend.id
  key          = "styles.css"
  source       = "${path.root}/../frontend/styles.css"
  etag         = filemd5("${path.root}/../frontend/styles.css")
  content_type = "text/css"
}

resource "aws_s3_object" "app" {
  bucket       = aws_s3_bucket.frontend.id
  key          = "app.js"
  source       = "${path.root}/../frontend/app.js"
  etag         = filemd5("${path.root}/../frontend/app.js")
  content_type = "application/javascript"
}
