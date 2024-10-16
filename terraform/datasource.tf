data "aws_ami" "parking_ami" {
  most_recent = true
  owners      = ["099720109477"] # Ubuntu official account ID

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
  }
}