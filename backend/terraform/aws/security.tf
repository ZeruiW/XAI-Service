resource "aws_security_group" "ecs_security_group" {
  
  name        = "security group"
  description = "enable http access on port 5006"
  vpc_id      = aws_vpc.main.id


  ingress {
    description = "Custom TCP"
    from_port   = 5006
    to_port     = 5006
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    description = "Custom TCP"
    from_port   = 5004
    to_port     = 5004
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
      description = "Custom TCP"
      from_port   = 5003
      to_port     = 5003
      protocol    = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
      description = "Custom TCP"
      from_port   = 5001
      to_port     = 5001
      protocol    = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
      description = "Custom TCP"
      from_port   = 5009
      to_port     = 5009
      protocol    = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
      description = "Custom TCP"
      from_port   = 5012
      to_port     = 5012
      protocol    = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
      description = "Custom TCP"
      from_port   = 5007
      to_port     = 5007
      protocol    = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
  }

   ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "ecs_sg"
  }
}
