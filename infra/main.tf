terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region
}

variable "region" {
  default = "us-east-1"
}

# Container registry for the churn image
resource "aws_ecr_repository" "churnguard" {
  name                 = "churnguard"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true   # DevSecOps: AWS scans every pushed image for CVEs
  }
}

output "ecr_url" {
  value = aws_ecr_repository.churnguard.repository_url
}
