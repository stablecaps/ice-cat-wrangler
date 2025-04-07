terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.94.0"
    }
  }
  required_version = "= 1.11.3"

  backend "s3" {
    key     = "cat-wrangler/lambda-perms/terraform.tfstate"
    encrypt = "true"
  }
}

provider "aws" {
  region = var.region
}
