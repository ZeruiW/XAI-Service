terraform {
  required_providers {
    docker = {
      source = "kreuzwerker/docker"

    }
    aws = {
      source = "hashicorp/aws"
    }
  }
  backend "s3" {
    bucket         = "xai-tfstate"
    key            = "state-file/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
  }
}

provider "docker" {}

provider "aws" {
  region = var.region
}