# Create a resource, vpc for parking app.
resource "aws_vpc" "parking_vpc" {
  cidr_block = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support = true

  tags = {
    Name = "parking_vpc"
  }
}

# create a aws subnet
resource "aws_subnet" "parking_subnet" {
  vpc_id     = aws_vpc.parking_vpc.id
  cidr_block = "10.0.1.0/24"
  availability_zone = "eu-central-1a"
  map_public_ip_on_launch = true

  tags = {
    Name = "parking_subnet"
  }
}

# create a aws internet gateway
resource "aws_internet_gateway" "parking_gateway" {
  vpc_id = aws_vpc.parking_vpc.id

  tags = {
    Name = "parking_gateway"
  }
}

# create a aws route table
resource "aws_route_table" "parking_route_table" {
  vpc_id = aws_vpc.parking_vpc.id

  tags = {
    Name = "parking_route_table"
  }
}

# create a aws route
resource "aws_route" "parking_route" {
  route_table_id         = aws_route_table.parking_route_table.id
  destination_cidr_block = "0.0.0.0/0" # allow all traffic hit the gateway
  gateway_id             = aws_internet_gateway.parking_gateway.id
}

# create aws route table association
resource "aws_route_table_association" "parking_route_association" {
  subnet_id      = aws_subnet.parking_subnet.id
  route_table_id = aws_route_table.parking_route_table.id
}

# create a aws security group
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

# create a key pair
resource "aws_key_pair" "parking_key_pair" {
  key_name   = "aws"
  public_key = file("~/.ssh/id_rsa.pub")
}

# create a aws instance EC2
resource "aws_instance" "parking_instance" {
  ami = data.aws_ami.parking_ami.id
  instance_type = "t2.micro"
  key_name = aws_key_pair.parking_key_pair.key_name
  subnet_id = aws_subnet.parking_subnet.id
  vpc_security_group_ids = [aws_security_group.parking_security_group.id]
  user_data = file("userdata.tpl")

  root_block_device {
    volume_size = 10
  }

  tags = {
    Name = "parking_instance"
  }
}