# Fetch AZs in the current region
data "aws_availability_zones" "available" {
  state = "available"
}

resource "aws_vpc" "main" {
  cidr_block            = "172.19.0.0/16"
  enable_dns_hostnames  = true
  enable_dns_support    = true
}

resource "aws_subnet" "PublicSubnetOne" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "172.19.0.0/24"
  availability_zone       = "us-east-1b"
  map_public_ip_on_launch = true
}

resource "aws_subnet" "PublicSubnetTwo" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "172.19.1.0/24"
  availability_zone       = "us-east-1c"
  map_public_ip_on_launch = true
}

# Internet Gateway for the public subnet
resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.main.id
}

resource "aws_route_table" "PublicRouteTable" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "PublicRouteTable"
  }
}

resource "aws_route" "PublicRoute1" {
  route_table_id         = aws_route_table.PublicRouteTable.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.gw.id
}

resource "aws_route" "PublicRoute2" {
  route_table_id         = aws_route_table.PublicRouteTable.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.gw.id
}

resource "aws_route_table_association" "PublicSubnetOneRouteTableAssociation" {
  subnet_id      = aws_subnet.PublicSubnetOne.id
  route_table_id = aws_route_table.PublicRouteTable.id
}

resource "aws_route_table_association" "PublicSubnetTwoRouteTableAssociation" {
  subnet_id      = aws_subnet.PublicSubnetTwo.id
  route_table_id = aws_route_table.PublicRouteTable.id
}

output "VpcId" {
  description = "The ID of the VPC that this stack is deployed in"
  value       = aws_vpc.main.id
}

output "PublicSubnetOne" {
  description = "Public subnet one"
  value       = aws_subnet.PublicSubnetOne.id
}

output "PublicSubnetTwo" {
  description = "Public subnet two"
  value       = aws_subnet.PublicSubnetTwo.id
}
