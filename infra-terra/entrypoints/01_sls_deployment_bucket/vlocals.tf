locals {
  tags = {
    environment = var.env
    project     = "stablecaps"
    owner       = "DevOps"
    created_by  = "terraform"
  }

  bucket_name = "serverless-deployment-holder-${var.unique_str}-${var.env}"
}
