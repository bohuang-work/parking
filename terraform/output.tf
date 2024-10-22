# Output the endpoint of rds-postgres instance
output "postgres-endpoint" {
  value = "${aws_db_instance.postgres.endpoint}"
}

# Output the API Gateway URL
output "http_api_endpoint" {
  value = aws_apigatewayv2_api.parking_http_api.api_endpoint
}