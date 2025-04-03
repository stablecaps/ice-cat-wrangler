terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.94.0"
    }
  }
  required_version = "= 1.11.3"

  # IMPORTANT: Local tf file. we should probably delete to keep it safe
  # once created we so not need the state file really - so uncomment below
  # and run tf init to push to remote state we just created
  # backend "s3" {
  #   key     = "terraform-remotestate-stablecaps-dev/terraform.tfstate"
  #   encrypt = "true"
  # }
}

provider "aws" {
  region = var.region
}

# Not currently used but seems to be mandatory for this module
provider "aws" {
  alias = "replica"
}
