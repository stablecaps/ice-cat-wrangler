locals {
  tags = {
    environment = var.env
    unique_str  = var.unique_str
    project     = var.project
    owner       = var.owner
    created_by  = var.created_by
    terraform   = "true"
  }

  ssm_root_prefix = "/stablecaps/${var.env}/${var.project}"

}
