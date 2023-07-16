resource "aws_ecs_service" "service-xai-central-ec2" {
  name            = "xai-central"
  cluster         = aws_ecs_cluster.ec2-cluster.id
  task_definition = aws_ecs_task_definition.td-xai-central-ec2.arn
  desired_count   = 1
  launch_type     = "EC2"

  deployment_minimum_healthy_percent = 100
  deployment_maximum_percent         = 200

  deployment_controller {
    type = "ECS"
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

resource "aws_ecs_service" "service-xai-azure-cog" {
  name            = "xai-azure-cog"
  cluster         = aws_ecs_cluster.ec2-cluster.id
  task_definition = aws_ecs_task_definition.td-xai-azure-cog-ec2.arn
  desired_count   = 1
  launch_type     = "EC2"

  deployment_minimum_healthy_percent = 100
  deployment_maximum_percent         = 200

  deployment_controller {
    type = "ECS"
  }
}

resource "aws_ecs_service" "service-xai-azure-blob" {
  name            = "xai-azure-blob"
  cluster         = aws_ecs_cluster.ec2-cluster.id
  task_definition = aws_ecs_task_definition.td-xai-azure-blob-ec2.arn
  desired_count   = 1
  launch_type     = "EC2"

  deployment_minimum_healthy_percent = 100
  deployment_maximum_percent         = 200

  deployment_controller {
    type = "ECS"
  }
}

resource "aws_ecs_service" "service-xai-restnet50" {
  name            = "xai-restnet50"
  cluster         = aws_ecs_cluster.ec2-cluster.id
  task_definition = aws_ecs_task_definition.td-xai-model_service_rn50_1-ec2.arn
  desired_count   = 1
  launch_type     = "EC2"

  deployment_minimum_healthy_percent = 100
  deployment_maximum_percent         = 200

  deployment_controller {
    type = "ECS"
  }
}

resource "aws_ecs_service" "service-xai-evaluation_service" {
  name            = "xai-evaluation_service"
  cluster         = aws_ecs_cluster.ec2-cluster.id
  task_definition = aws_ecs_task_definition.td-xai-evaluation_service-ec2.arn
  desired_count   = 1
  launch_type     = "EC2"

  deployment_minimum_healthy_percent = 100
  deployment_maximum_percent         = 200

  deployment_controller {
    type = "ECS"
  }
}