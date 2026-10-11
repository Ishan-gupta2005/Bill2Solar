output "api_url" {
  value = aws_apigatewayv2_api.http.api_endpoint
}

output "upload_bucket" {
  value = aws_s3_bucket.uploads.bucket
}

output "estimates_table" {
  value = aws_dynamodb_table.estimates.name
}

output "lambda_name" {
  value = aws_lambda_function.api.function_name
}

output "amplify_app_id" {
  value = aws_amplify_app.web.id
}

output "amplify_url" {
  value = "https://${aws_amplify_branch.main.branch_name}.${aws_amplify_app.web.default_domain}"
}

output "region" {
  value = var.region
}
