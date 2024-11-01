output "lambda_function_url" {
  description = "The URL endpoint for the Lambda function"
  value       = aws_lambda_function_url.lambda_function_url.function_url
}