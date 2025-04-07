locals {
  tags = {
    environment = var.env
    unique_str  = var.unique_str
    project     = var.project
    owner       = var.owner
    created_by  = var.created_by
    terraform   = "true"
  }
  func_analyser_role_name = "${var.project}-${var.env}-${var.region}"
}
