locals {
  tags = {
    environment = var.env
    unique_str  = var.unique_str
    project     = var.project
    owner       = var.owner
    created_by  = var.created_by
    terraform   = "true"
  }
  lambda_cat_wrangler_app_role_name = "${var.project}-${var.env}-${var.region}"

  ssm_root_prefix = "/stablecaps/${var.env}/${var.project}"

  s3bucket_source_fullname = "${var.s3bucket_source_name}-${var.unique_str}-${var.env}"
  s3bucket_dest_fullname   = "${var.s3bucket_dest_name}-${var.unique_str}-${var.env}"
  s3bucket_fail_fullname   = "${var.s3bucket_fail_name}-${var.unique_str}-${var.env}"

}
