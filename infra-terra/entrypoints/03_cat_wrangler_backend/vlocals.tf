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

  ssm_root_prefix = "/stablecaps/${var.env}/${var.project}"

  ssm_map = {
    DYNAMODB_TABLE_NAME = "${var.dynamo_db_name}-${var.unique_str}-${var.env}"
  }

}
