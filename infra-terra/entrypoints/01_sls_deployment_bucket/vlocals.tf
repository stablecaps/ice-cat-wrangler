locals {
  tags = {
    company     = var.company
    environment = var.env
    unique_str  = var.unique_str
    project     = var.project
    owner       = var.owner
    created_by  = var.created_by
    terraform   = "true"
  }


  bucket_name = "serverless-deployment-holder-${var.unique_str}-${var.env}"

  ssm_root_prefix = "/stablecaps/${var.env}/${var.project}"
  ssm_map = {
    SLS_DEPLOY_BUCKET = local.bucket_name
  }
}
