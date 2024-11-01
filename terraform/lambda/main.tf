### Providers ###
terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}

provider "aws" {
  region                   = "eu-central-1"
  shared_credentials_files = ["~/.aws/credentials"]
  profile                  = "bohuang-admin"
}

### Data Sources Docker Image ###
data "aws_ami" "parking_ami" {
  most_recent = true
  owners      = ["099720109477"] # Ubuntu official account ID

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
  }
}

### AWS Resources ###
# Create a VPC for parking app.
resource "aws_vpc" "parking_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "parking_vpc"
  }
}

# Create two subnets for high availability
resource "aws_subnet" "parking_subnet_1" {
  vpc_id                  = aws_vpc.parking_vpc.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "eu-central-1a"
  map_public_ip_on_launch = true

  tags = {
    Name = "parking_subnet_1"
  }
}

resource "aws_subnet" "parking_subnet_2" {
  vpc_id                  = aws_vpc.parking_vpc.id
  cidr_block              = "10.0.2.0/24"
  availability_zone       = "eu-central-1b"
  map_public_ip_on_launch = true

  tags = {
    Name = "parking_subnet_2"
  }
}

# Create an Internet Gateway
resource "aws_internet_gateway" "parking_gateway" {
  vpc_id = aws_vpc.parking_vpc.id

  tags = {
    Name = "parking_gateway"
  }
}

# Create a Route Table
resource "aws_route_table" "parking_route_table" {
  vpc_id = aws_vpc.parking_vpc.id

  tags = {
    Name = "parking_route_table"
  }
}

# Route to Internet Gateway
resource "aws_route" "parking_route" {
  route_table_id         = aws_route_table.parking_route_table.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.parking_gateway.id
}

# Route Table Associations for subnets
resource "aws_route_table_association" "parking_route_association_1" {
  subnet_id      = aws_subnet.parking_subnet_1.id
  route_table_id = aws_route_table.parking_route_table.id
}

resource "aws_route_table_association" "parking_route_association_2" {
  subnet_id      = aws_subnet.parking_subnet_2.id
  route_table_id = aws_route_table.parking_route_table.id
}

# Create a Security Group for RDS
resource "aws_security_group" "rds_security_group" {
  vpc_id = aws_vpc.parking_vpc.id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # Adjust as necessary for security
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "rds_security_group"
  }
}

# Create an RDS Subnet Group
resource "aws_db_subnet_group" "parking_db_subnet_group" {
  name       = "parking-db-subnet-group"
  subnet_ids = [aws_subnet.parking_subnet_1.id, aws_subnet.parking_subnet_2.id]

  tags = {
    Name = "parking_db_subnet_group"
  }
}

# Create a PostgreSQL RDS Instance
resource "aws_db_instance" "postgres" {
  allocated_storage      = 20
  storage_type           = "gp2"
  engine                 = "postgres"
  engine_version         = "16.3"         # Adjust the version if needed
  instance_class         = "db.t4g.micro" # Suitable for testing
  identifier             = "parking-db"
  username               = "dbadmin"        # Set your DB username
  password               = "adminAdmin123!" # Set your DB password securely
  db_name                = "parkingdb"
  skip_final_snapshot    = true
  publicly_accessible    = false
  vpc_security_group_ids = [aws_security_group.rds_security_group.id]
  db_subnet_group_name   = aws_db_subnet_group.parking_db_subnet_group.id

  tags = {
    Name = "parking_db"
  }
}

# Create a Security Group for Lambda
resource "aws_security_group" "lambda_security_group" {
  vpc_id = aws_vpc.parking_vpc.id

  # Allow Lambda to connect to the RDS instance on port 5432
  egress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "lambda_security_group"
  }
}

# Lambda IAM Role
resource "aws_iam_role" "lambda_execution_role" {
  name = "lambda_execution_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })

  tags = {
    Name = "lambda_execution_role"
  }
}

# Attach policies to Lambda Role
resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "lambda_vpc_access_execution" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

# Create Lambda function
resource "aws_lambda_function" "parking_lambda" {
  filename      = "lambda_artifact.zip" # Assumes you'll upload this manually to match your code
  function_name = "parkingLambda"
  role          = aws_iam_role.lambda_execution_role.arn
  handler       = "main.handler" # Adjust to your handler if different
  runtime       = "python3.11"
  timeout       = 10

  environment {
    variables = {
      DB_ENDPOINT = aws_db_instance.postgres.address
      DB_NAME     = aws_db_instance.postgres.db_name
      DB_USERNAME = "dbadmin"
      DB_PASSWORD = "adminAdmin123!"
    }
  }

  vpc_config {
    subnet_ids         = [aws_subnet.parking_subnet_1.id, aws_subnet.parking_subnet_2.id]
    security_group_ids = [aws_security_group.lambda_security_group.id]
  }

  tags = {
    Name = "parking_lambda"
  }
}

# Lambda Function URL
resource "aws_lambda_function_url" "lambda_function_url" {
  function_name      = aws_lambda_function.parking_lambda.function_name
  authorization_type = "NONE" # Change to "AWS_IAM" if you want to restrict access
}
