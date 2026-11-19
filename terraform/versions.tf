terraform {
  required_version = ">= 1.9"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.80"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }
  # Mock: a real deployment would use an S3 + DynamoDB-lock remote backend.
}

provider "aws" {
  region = var.region
  default_tags {
    tags = {
      Project     = "cac-demo"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}
