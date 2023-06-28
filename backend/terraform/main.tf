resource "aws_launch_configuration" "ecs_launch_config" {
  name                 = "ecs-launch-config"
  image_id             = "ami-0817f4be8d3c41be4"
  instance_type        = "g3.4xlarge"
  iam_instance_profile = aws_iam_instance_profile.ecs_instance_profile.name
  security_groups      = [aws_security_group.ecs_security_group.id]
  key_name             = "ec2-test"
  root_block_device {
    volume_type           = "gp2"
    volume_size           = 100
    delete_on_termination = true
  }
  
  lifecycle {
    create_before_destroy = true
  }
  user_data = <<-SCRIPT
    #!/bin/bash
    echo "ECS_CLUSTER=${aws_ecs_cluster.ec2-cluster.id}" >> /etc/ecs/ecs.config
    SCRIPT
}

resource "aws_autoscaling_group" "ecs_autoscaling_group" {
  name                 = "ecs-autoscaling-group"
  launch_configuration = aws_launch_configuration.ecs_launch_config.name
  min_size             = 1
  max_size             = 9
  desired_capacity     = 1
  vpc_zone_identifier  = [aws_subnet.PublicSubnetOne.id, aws_subnet.PublicSubnetTwo.id]
  force_delete         = true
}


resource "aws_ecs_cluster" "ec2-cluster" {
  name = "${var.name_prefix}-ec2-cluster"
  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

# Output ECS cluster ARN
output "ecs_cluster_arn" {
  value = aws_ecs_cluster.ec2-cluster.arn
}

