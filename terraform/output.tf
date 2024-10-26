# Output the endpoint of rds-postgres instance
output "postgres-endpoint" {
  value = aws_db_instance.postgres.address
}

# Output the public IP of the EC2 instance
output "ec2_public_ip" {
  value = aws_instance.parking_instance.public_ip
}

# Output the API Gateway URL
output "http_api_endpoint" {
  value = aws_apigatewayv2_api.parking_http_api.api_endpoint
}