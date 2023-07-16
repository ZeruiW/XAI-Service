variable "region" {
  description = "name region"
  default     = "us-east-1"
}


variable "project_name" {
  type        = string
  description = "This configures the project name"
  default     = "ecs-fargate"
}

variable "name_prefix" {
  type        = string
  description = "This configures a name variable to name other resources"
  default     = "ecs-xai"
}

variable "az_count" {
  description = "Number of AZs to cover in a given region"
  default     = "2"
}

variable "ecs_task_execution_role_name" {
  description = "ECS task execution role name"
  default = "ecs-task-execution-role"
}

variable "app_port" {
  description = "Port exposed by the docker image to redirect traffic to"
  default     = 5006
}