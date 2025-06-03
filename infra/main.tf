terraform {
  required_version = ">= 1.0"
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

resource "aws_s3_bucket" "cv_bucket" {
  bucket = var.cv_bucket
  force_destroy = true
}

# Additional resources like Cognito, Aurora, and OpenSearch would be defined here.
