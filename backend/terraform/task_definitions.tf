resource "aws_ecs_task_definition" "td-xai-central-ec2" {
  family                   = "td-xai-central-ec2"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  requires_compatibilities = ["EC2"]
  cpu                      = "256"
  memory                   = "512"
  container_definitions = jsonencode([ {
      "name": "xai-central-ec2",
      "image": aws_ecr_repository.xai-ecr-repository-backend-central.repository_url,
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
      }
    }])
    runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "X86_64"
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
            "image": aws_ecr_repository.xai-ecr-repository-backend-xai_service_pytorch_cam.repository_url,
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

resource "aws_ecs_task_definition" "td-xai-azure-blob-ec2" {
  family                   = "td-xai-azure-blob-ec2"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  requires_compatibilities = ["EC2"]
  cpu                      = "256"
  memory                   = "512"
  container_definitions = jsonencode([
        {
            "name": "xai-grad-cam-ec2",
            "image": aws_ecr_repository.xai-ecr-repository-azure-blob.repository_url,
            "cpu": 0,
            "portMappings": [
                {
                    "name": "xai-grad-cam-ec2-5009-tcp",
                    "containerPort": 5009,
                    "hostPort": 5009,
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

resource "aws_ecs_task_definition" "td-xai-model_service_rn50_1-ec2" {
  family                   = "td-xai-model_service_rn50_1-ec2"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  requires_compatibilities = ["EC2"]
  cpu                      = "256"
  memory                   = "512"
  container_definitions = jsonencode([
        {
            "name": "xai-model_service_rn50_1-ec2",
            "image": aws_ecr_repository.xai-ecr-repository-backend-model_service_rn50_1.repository_url,
            "cpu": 0,
            "portMappings": [
                {
                    "name": "xai-model_service_rn50_1-ec2-5001-tcp",
                    "containerPort": 5001,
                    "hostPort": 5001,
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

resource "aws_ecs_task_definition" "td-xai-azure-cog-ec2" {
  family                   = "td-xai-azure-cog-ec2"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  requires_compatibilities = ["EC2"]
  cpu                      = "256"
  memory                   = "512"
  container_definitions = jsonencode([
        {
            "name": "xai-azure-cog-ec2",
            "image": aws_ecr_repository.xai-ecr-repository-azure-cog.repository_url,
            "cpu": 0,
            "portMappings": [
                {
                    "name": "xai-azure-cog-ec2-5007-tcp",
                    "containerPort": 5007,
                    "hostPort": 5007,
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

resource "aws_ecs_task_definition" "td-xai-evaluation_service-ec2" {
  family                   = "td-xai-evaluation_service-ec2"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  requires_compatibilities = ["EC2"]
  cpu                      = "256"
  memory                   = "512"
  container_definitions = jsonencode([
        {
            "name": "xai-evaluation_service-ec2",
            "image": aws_ecr_repository.xai-ecr-repository-backend-evaluation_service.repository_url,
            "cpu": 0,
            "portMappings": [
                {
                    "name": "xai-evaluation_service-ec2-5004-tcp",
                    "containerPort": 5004,
                    "hostPort": 5004,
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