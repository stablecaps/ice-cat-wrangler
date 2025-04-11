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

  base_name = "terraform-remotestate-${var.company}-${var.unique_str}-${var.env}"

}
