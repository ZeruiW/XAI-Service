resource "aws_ecr_repository" "xai-ecr-repository" {
  name = "xai-central"
}

locals {
  docker_image_name = "xai-central"
  docker_image_tag  = "latest"
}

data "aws_ecr_authorization_token" "auth" {}

resource "null_resource" "docker_push" {
  depends_on = [aws_ecr_repository.xai-ecr-repository]

  provisioner "local-exec" {
    command = "aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 979458579914.dkr.ecr.us-east-1.amazonaws.com"
  }

  provisioner "local-exec" {
    command = "docker tag ${local.docker_image_name}:${local.docker_image_tag} ${aws_ecr_repository.xai-ecr-repository.registry_id}.dkr.ecr.us-east-1.amazonaws.com/${aws_ecr_repository.xai-ecr-repository.name}:${local.docker_image_tag}"
  }

  provisioner "local-exec" {
    command = "docker push ${aws_ecr_repository.xai-ecr-repository.registry_id}.dkr.ecr.us-east-1.amazonaws.com/${aws_ecr_repository.xai-ecr-repository.name}:${local.docker_image_tag}"
  }
}


resource "aws_ecs_cluster" "fargate-cluster" {
  name = "${var.name_prefix}-cluster"
}

resource "aws_ecs_cluster_capacity_providers" "cluster" {
  cluster_name = aws_ecs_cluster.fargate-cluster.name

  capacity_providers = ["FARGATE_SPOT", "FARGATE"]

  default_capacity_provider_strategy {
    capacity_provider = "FARGATE_SPOT"
  }
}

resource "aws_ecs_task_definition" "td-xai-central" {
  family                   = "td-xai-central"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  container_definitions = jsonencode([ {
      "name": "central",
      "image": aws_ecr_repository.xai-ecr-repository.repository_url,
      "cpu": 0,
      "portMappings": [
        {
          "name": "central-5009-tcp",
          "containerPort": 5009,
          "hostPort": 5009,
          "protocol": "tcp",
          "appProtocol": "http"
        }
      ],
      "essential": true,
      "environment": [],
      "environmentFiles": [],
      "mountPoints": [],
      "volumesFrom": [],
      "ulimits": [],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-create-group": "true",
          "awslogs-group": "/ecs/test",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "platform_version": "LATEST",
      "cpu_architecture": "ARM64"
    }])
    runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "ARM64"
  }
}

resource "aws_ecs_service" "service-xai-central" {
  name            = "xai-central"
  cluster         = aws_ecs_cluster.fargate-cluster.id
  task_definition = aws_ecs_task_definition.td-xai-central.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    security_groups  = [aws_security_group.ecs_security_group.id]
    subnets          = [aws_subnet.PublicSubnetOne.id, aws_subnet.PublicSubnetTwo.id]
    assign_public_ip = true
  }

}


resource "aws_launch_configuration" "ecs_launch_config" {
  name                 = "ecs-launch-config"
  image_id             = "ami-0bcaab066c3611e2a"
  instance_type        = "g3s.xlarge"
  iam_instance_profile = aws_iam_instance_profile.ecs_instance_profile.name
  security_groups      = [aws_security_group.ecs_security_group.id]
  key_name             = "ec2-test"
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
  max_size             = 2
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

resource "aws_ecs_task_definition" "td-xai-grad-cam-ec2" {
  family                   = "td-xai-grad-cam-ec2"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  requires_compatibilities = ["EC2"]
  cpu                      = "256"
  memory                   = "512"
  container_definitions = jsonencode([
        {
            "name": "xai-grad-cam-ec2",
            "image": "979458579914.dkr.ecr.us-east-1.amazonaws.com/xai-grad-cam:latest",
            "cpu": 0,
            "portMappings": [
                {
                    "name": "xai-grad-cam-ec2-5003-tcp",
                    "containerPort": 5003,
                    "hostPort": 5003,
                    "protocol": "tcp",
                    "appProtocol": "http"
                }
            ],
            "essential": true,
            "environment": [],
            "mountPoints": [],
            "volumesFrom": [],
            "logConfiguration": {
                "logDriver": "awslogs",
                "options": {
                    "awslogs-create-group": "true",
                    "awslogs-group": "xai-central",
                    "awslogs-region": "us-east-1",
                    "awslogs-stream-prefix": "firelens"
                }
            }
        }
    ])
    runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "X86_64"
  }
}

resource "aws_ecs_service" "service-xai-grad-cam" {
  name            = "xai-grad-cam"
  cluster         = aws_ecs_cluster.ec2-cluster.id
  task_definition = aws_ecs_task_definition.td-xai-grad-cam-ec2.arn
  desired_count   = 1
  launch_type     = "EC2"

  deployment_minimum_healthy_percent = 100
  deployment_maximum_percent         = 200

  deployment_controller {
    type = "ECS"
  }

}

# Output ECS cluster ARN
output "ecs_cluster_arn" {
  value = aws_ecs_cluster.ec2-cluster.arn
}

