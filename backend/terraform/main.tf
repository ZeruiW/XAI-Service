resource "aws_ecr_repository" "xai-ecr-repository-azure-cog" {
   name = "backend-azure-cog"
}

resource "aws_ecr_repository" "xai-ecr-repository-azure-blob" {
   name = "backend-azure-blob"
}
resource "aws_ecr_repository" "xai-ecr-repository-backend-model_service_rn50_1" {
   name = "backend-model_service_rn50_1"
}
resource "aws_ecr_repository" "xai-ecr-repository-backend-central" {
   name = "backend-central"
}
resource "aws_ecr_repository" "xai-ecr-repository-backend-evaluation_service" {
   name = "backend-evaluation_service"
}
resource "aws_ecr_repository" "xai-ecr-repository-backend-xai_service_pytorch_cam" {
   name = "backend-xai_service_pytorch_cam"
}

data "aws_ecr_authorization_token" "auth" {}


resource "null_resource" "docker_push" {
  provisioner "local-exec" {
    command = <<EOT
      # Authenticate Docker with ECR
      aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 979458579914.dkr.ecr.us-east-1.amazonaws.com

      # docker tag backend-azure-cog:latest ${aws_ecr_repository.xai-ecr-repository-azure-cog.registry_id}.dkr.ecr.us-east-1.amazonaws.com/${aws_ecr_repository.xai-ecr-repository-azure-cog.name}:latest
      # docker push ${aws_ecr_repository.xai-ecr-repository-azure-cog.registry_id}.dkr.ecr.us-east-1.amazonaws.com/${aws_ecr_repository.xai-ecr-repository-azure-cog.name}:latest

      # docker tag backend-azure-blob:latest ${aws_ecr_repository.xai-ecr-repository-azure-blob.registry_id}.dkr.ecr.us-east-1.amazonaws.com/${aws_ecr_repository.xai-ecr-repository-azure-blob.name}:latest
      # docker push ${aws_ecr_repository.xai-ecr-repository-azure-blob.registry_id}.dkr.ecr.us-east-1.amazonaws.com/${aws_ecr_repository.xai-ecr-repository-azure-blob.name}:latest

      # docker tag backend-model_service_rn50_1:latest ${aws_ecr_repository.xai-ecr-repository-backend-model_service_rn50_1.registry_id}.dkr.ecr.us-east-1.amazonaws.com/${aws_ecr_repository.xai-ecr-repository-backend-model_service_rn50_1.name}:latest
      # docker push ${aws_ecr_repository.xai-ecr-repository-backend-model_service_rn50_1.registry_id}.dkr.ecr.us-east-1.amazonaws.com/${aws_ecr_repository.xai-ecr-repository-backend-model_service_rn50_1.name}:latest

      docker tag backend-central:latest ${aws_ecr_repository.xai-ecr-repository-backend-central.registry_id}.dkr.ecr.us-east-1.amazonaws.com/${aws_ecr_repository.xai-ecr-repository-backend-central.name}:latest
      docker push ${aws_ecr_repository.xai-ecr-repository-backend-central.registry_id}.dkr.ecr.us-east-1.amazonaws.com/${aws_ecr_repository.xai-ecr-repository-backend-central.name}:latest

      # docker tag backend-evaluation_service:latest ${aws_ecr_repository.xai-ecr-repository-backend-evaluation_service.registry_id}.dkr.ecr.us-east-1.amazonaws.com/${aws_ecr_repository.xai-ecr-repository-backend-evaluation_service.name}:latest
      # docker push ${aws_ecr_repository.xai-ecr-repository-backend-evaluation_service.registry_id}.dkr.ecr.us-east-1.amazonaws.com/${aws_ecr_repository.xai-ecr-repository-backend-evaluation_service.name}:latest

      docker tag backend-xai_service_pytorch_cam:latest ${aws_ecr_repository.xai-ecr-repository-backend-xai_service_pytorch_cam.registry_id}.dkr.ecr.us-east-1.amazonaws.com/${aws_ecr_repository.xai-ecr-repository-backend-xai_service_pytorch_cam.name}:latest
      docker push ${aws_ecr_repository.xai-ecr-repository-backend-xai_service_pytorch_cam.registry_id}.dkr.ecr.us-east-1.amazonaws.com/${aws_ecr_repository.xai-ecr-repository-backend-xai_service_pytorch_cam.name}:latest
    EOT
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

# Output ECS cluster ARN
output "ecs_cluster_arn" {
  value = aws_ecs_cluster.ec2-cluster.arn
}

