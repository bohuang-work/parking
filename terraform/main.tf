# Create a resource, vpc for parking app.
resource "aws_vpc" "parking_vpc" {
  cidr_block = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support = true

  tags = {
    Name = "parking_vpc"
  }
}

# Create an aws subnet (two subnets for availability zone coverage)
resource "aws_subnet" "parking_subnet_1" {
  vpc_id     = aws_vpc.parking_vpc.id
  cidr_block = "10.0.1.0/24"
  availability_zone = "eu-central-1a"
  map_public_ip_on_launch = true

  tags = {
    Name = "parking_subnet_1"
  }
}

resource "aws_subnet" "parking_subnet_2" {
  vpc_id     = aws_vpc.parking_vpc.id
  cidr_block = "10.0.2.0/24"
  availability_zone = "eu-central-1b"
  map_public_ip_on_launch = true

  tags = {
    Name = "parking_subnet_2"
  }
}

# Create a aws internet gateway
resource "aws_internet_gateway" "parking_gateway" {
  vpc_id = aws_vpc.parking_vpc.id

  tags = {
    Name = "parking_gateway"
  }
}

# Create a aws route table
resource "aws_route_table" "parking_route_table" {
  vpc_id = aws_vpc.parking_vpc.id

  tags = {
    Name = "parking_route_table"
  }
}

# Create a aws route
resource "aws_route" "parking_route" {
  route_table_id         = aws_route_table.parking_route_table.id
  destination_cidr_block = "0.0.0.0/0" # allow all traffic hit the gateway
  gateway_id             = aws_internet_gateway.parking_gateway.id
}

# Create aws route table associations
resource "aws_route_table_association" "parking_route_association_1" {
  subnet_id      = aws_subnet.parking_subnet_1.id
  route_table_id = aws_route_table.parking_route_table.id
}

resource "aws_route_table_association" "parking_route_association_2" {
  subnet_id      = aws_subnet.parking_subnet_2.id
  route_table_id = aws_route_table.parking_route_table.id
}

# Create a aws security group
resource "aws_security_group" "parking_security_group" {
  vpc_id = aws_vpc.parking_vpc.id
  name = "parking_security_group"

  # Allow inbound ssh traffic via port 22
  ingress {
    from_port = 22
    to_port = 22
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow inbound http traffic via port 80
  ingress {
    from_port = 80
    to_port = 80
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow inbound traffic to PostgreSQL (port 5432)
  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # You might want to restrict this to the security group of the EC2 instance
  }

  # Allow outbound traffic to anywhere
  egress {
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "parking_security_group"
  }
}

# Create a key pair
resource "aws_key_pair" "parking_key_pair" {
  key_name   = "aws"
  public_key = file("~/.ssh/id_rsa.pub")
}

# Create an aws instance EC2
resource "aws_instance" "parking_instance" {
  ami = data.aws_ami.parking_ami.id
  instance_type = "t2.micro"
  key_name = aws_key_pair.parking_key_pair.key_name
  subnet_id = aws_subnet.parking_subnet_1.id  # Use one of the subnets
  vpc_security_group_ids = [aws_security_group.parking_security_group.id]
  user_data = file("userdata.tpl")

  root_block_device {
    volume_size = 10
  }

  tags = {
    Name = "parking_instance"
  }
}

# Create a security group for RDS
resource "aws_security_group" "rds_security_group" {
  vpc_id = aws_vpc.parking_vpc.id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # Update this to restrict access as necessary
  }

  egress {
    from_port = 0
    to_port   = 0
    protocol  = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "rds_security_group"
  }
}

# Create a DB subnet group
resource "aws_db_subnet_group" "parking_db_subnet_group" {
  name       = "parking-db-subnet-group"
  subnet_ids = [aws_subnet.parking_subnet_1.id, aws_subnet.parking_subnet_2.id]  # Include both subnets

  tags = {
    Name = "parking_db_subnet_group"
  }
}

# Create an RDS PostgreSQL instance
resource "aws_db_instance" "postgres" {
  allocated_storage    = 20
  storage_type        = "gp2"
  engine              = "postgres"
  engine_version      = "16.3"  # Use the specified version
  instance_class      = "db.t4g.micro"  # Ensure this is a free tier option
  identifier          = "parking-db"
  username            = "dbadmin" # Change to your desired username
  password            = "adminAdmin123!" # Change to a secure password
  db_name             = "parkingdb"
  skip_final_snapshot = true
  publicly_accessible  = false  # Set to false for better security
  vpc_security_group_ids = [aws_security_group.rds_security_group.id]
  db_subnet_group_name = aws_db_subnet_group.parking_db_subnet_group.id

  tags = {
    Name = "parking_db"
  }
}

# Create the HTTP API Gateway
resource "aws_apigatewayv2_api" "parking_http_api" {
  name          = "parking-http-api"
  protocol_type = "HTTP"  # HTTP API type
}

# Create the integration with EC2 instance (forward to EC2)
resource "aws_apigatewayv2_integration" "parking_http_integration" {
  api_id           = aws_apigatewayv2_api.parking_http_api.id
  integration_type = "HTTP_PROXY"
  integration_uri  = "http://${aws_instance.parking_instance.public_ip}:80/{proxy}"  # Forward requests to EC2
  integration_method = "ANY"
}

# Create the default route to proxy all requests
resource "aws_apigatewayv2_route" "proxy_route" {
  api_id    = aws_apigatewayv2_api.parking_http_api.id
  route_key = "ANY /{proxy+}"  # This will match all paths
  target    = "integrations/${aws_apigatewayv2_integration.parking_http_integration.id}"
}

# Create a stage (default stage for production use)
resource "aws_apigatewayv2_stage" "default_stage" {
  api_id      = aws_apigatewayv2_api.parking_http_api.id
  name        = "$default"  # Default stage
  auto_deploy = true  # Automatically deploy the changes
}