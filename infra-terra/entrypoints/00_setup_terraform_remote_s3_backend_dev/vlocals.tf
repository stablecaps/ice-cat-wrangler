locals {
  tags = {
    environment = var.env
    unique_str  = var.unique_str
    project     = var.project
    owner       = var.owner
    created_by  = var.created_by
    terraform   = "true"
  }

  base_name = "terraform-remotestate-stablecaps-${var.unique_str}-${var.env}"

}
