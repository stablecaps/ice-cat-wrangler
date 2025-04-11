terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.94.0"
    }
  }
  required_version = "= 1.11.3"

  # IMPORTANT: On 1st run we create a local tfstate file. we should need to back it up to keep it safe
  # After 1st run uncomment below
  # and run `$terraform_exec init -backend-config ../../envs/${env}/${env}.backend.hcl -migrate-state` to push to remote state we just created
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
