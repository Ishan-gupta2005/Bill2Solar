terraform {
  required_version = ">= 1.5"
  required_providers {
    aws     = { source = "hashicorp/aws", version = "~> 6.0" }
    archive = { source = "hashicorp/archive", version = "~> 2.4" }
  }
}

provider "aws" {
  region = var.region
}

data "aws_caller_identity" "current" {}

locals {
  name = "bill2solar"
  tags = {
    Project   = "Bill2Solar"
    Hackathon = "WeMakeDevs-EnvironmentalHacks-2026"
    Track     = "WasteAndEnergy"
  }
}

# ---------------------------------------------------------------------------
# S3: bill uploads (presigned PUT from the browser, read by Lambda/Rekognition)
# ---------------------------------------------------------------------------
resource "aws_s3_bucket" "uploads" {
  bucket        = "${local.name}-uploads-${data.aws_caller_identity.current.account_id}"
  force_destroy = true
  tags          = local.tags
}

resource "aws_s3_bucket_public_access_block" "uploads" {
  bucket                  = aws_s3_bucket.uploads.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_cors_configuration" "uploads" {
  bucket = aws_s3_bucket.uploads.id
  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["PUT", "GET", "HEAD"]
    allowed_origins = ["*"]
    expose_headers  = ["ETag"]
    max_age_seconds = 3600
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "uploads" {
  bucket = aws_s3_bucket.uploads.id
  rule {
    id     = "expire-bills"
    status = "Enabled"
    filter {}
    expiration {
      days = 7
    }
  }
}

# ---------------------------------------------------------------------------
# DynamoDB: one row per estimate
# ---------------------------------------------------------------------------
resource "aws_dynamodb_table" "estimates" {
  name         = "${local.name}-estimates"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id"
  attribute {
    name = "id"
    type = "S"
  }
  ttl {
    attribute_name = "expires_at"
    enabled        = true
  }
  tags = local.tags
}

# ---------------------------------------------------------------------------
# Lambda: single function, routes on path
# ---------------------------------------------------------------------------
resource "aws_iam_role" "lambda" {
  name = "${local.name}-lambda-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
  tags = local.tags
}

resource "aws_iam_role_policy" "lambda" {
  name = "${local.name}-lambda-policy"
  role = aws_iam_role.lambda.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"]
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Effect   = "Allow"
        Action   = ["s3:GetObject", "s3:PutObject"]
        Resource = "${aws_s3_bucket.uploads.arn}/*"
      },
      {
        Effect   = "Allow"
        Action   = ["rekognition:DetectText"]
        Resource = "*"
      },
      {
        Effect   = "Allow"
        Action   = ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream"]
        Resource = "*"
      },
      {
        Effect   = "Allow"
        Action   = ["dynamodb:PutItem", "dynamodb:GetItem", "dynamodb:UpdateItem"]
        Resource = aws_dynamodb_table.estimates.arn
      }
    ]
  })
}

data "archive_file" "api" {
  type        = "zip"
  source_dir  = "${path.module}/../backend/src"
  output_path = "${path.module}/build/api.zip"
}

resource "aws_cloudwatch_log_group" "api" {
  name              = "/aws/lambda/${local.name}-api"
  retention_in_days = 7
  tags              = local.tags
}

resource "aws_lambda_function" "api" {
  function_name    = "${local.name}-api"
  role             = aws_iam_role.lambda.arn
  runtime          = "python3.13"
  handler          = "app.handler"
  filename         = data.archive_file.api.output_path
  source_code_hash = data.archive_file.api.output_base64sha256
  timeout          = 60
  memory_size      = 1024
  architectures    = ["arm64"]

  environment {
    variables = {
      UPLOAD_BUCKET        = aws_s3_bucket.uploads.bucket
      ESTIMATES_TABLE      = aws_dynamodb_table.estimates.name
      BEDROCK_REGIONS      = join(",", var.bedrock_regions)
      BEDROCK_ACCESS_KEY_ID     = var.bedrock_access_key_id
      BEDROCK_SECRET_ACCESS_KEY = var.bedrock_secret_access_key
      BEDROCK_VISION_MODEL = var.bedrock_vision_model
      BEDROCK_TEXT_MODEL   = var.bedrock_text_model
      BEDROCK_FALLBACKS    = join(",", var.bedrock_fallback_models)
      LOG_LEVEL            = "INFO"
    }
  }

  depends_on = [aws_cloudwatch_log_group.api, aws_iam_role_policy.lambda]
  tags       = local.tags
}

# ---------------------------------------------------------------------------
# API Gateway HTTP API
# ---------------------------------------------------------------------------
resource "aws_apigatewayv2_api" "http" {
  name          = "${local.name}-api"
  protocol_type = "HTTP"
  cors_configuration {
    allow_origins = ["*"]
    allow_methods = ["GET", "POST", "OPTIONS"]
    allow_headers = ["content-type", "authorization"]
    max_age       = 3600
  }
  tags = local.tags
}

resource "aws_apigatewayv2_integration" "lambda" {
  api_id                 = aws_apigatewayv2_api.http.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.api.invoke_arn
  payload_format_version = "2.0"
  timeout_milliseconds   = 30000
}

resource "aws_apigatewayv2_route" "routes" {
  for_each = toset([
    "GET /health",
    "POST /presign",
    "POST /analyze",
    "POST /proposal",
    "GET /estimates/{id}",
  ])
  api_id    = aws_apigatewayv2_api.http.id
  route_key = each.value
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.http.id
  name        = "$default"
  auto_deploy = true
  tags        = local.tags
}

resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http.execution_arn}/*/*"
}

# ---------------------------------------------------------------------------
# Amplify Hosting: manual zip deployments (no git connection needed)
# ---------------------------------------------------------------------------
resource "aws_amplify_app" "web" {
  name     = local.name
  platform = "WEB"

  # SPA rewrite: anything that is not a static asset serves index.html
  custom_rule {
    source = "</^[^.]+$|\\.(?!(css|gif|ico|jpg|jpeg|js|png|txt|svg|woff|woff2|ttf|map|json|webp)$)([^.]+$)/>"
    status = "200"
    target = "/index.html"
  }

  environment_variables = {
    VITE_API_URL = aws_apigatewayv2_api.http.api_endpoint
  }
  tags = local.tags
}

resource "aws_amplify_branch" "main" {
  app_id      = aws_amplify_app.web.id
  branch_name = "main"
  stage       = "PRODUCTION"
  tags        = local.tags
}
