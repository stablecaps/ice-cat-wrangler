terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.94.0"
    }
  }
  required_version = "= 1.11.3"

  backend "s3" {
    key     = "sls_deployment_bucket/terraform.tfstate"
    encrypt = "true"
  }
}

provider "aws" {
  region = var.region
}
