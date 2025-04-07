locals {
  tags = {
    environment = var.env
    unique_str  = var.unique_str
    project     = var.project
    owner       = var.owner
    created_by  = var.created_by
    terraform   = "true"
  }

  s3bucket_source_name = "${var.s3bucket_source_name}.${var.unique_str}-${var.env}"
  s3bucket_dest_name   = "${var.s3bucket_dest_name}.${var.unique_str}-${var.env}"
  s3bucket_fail_name   = "${var.s3bucket_fail_name}.${var.unique_str}-${var.env}"

  all_s3_buckets = [
    local.s3bucket_source_name,
    local.s3bucket_dest_name,
    local.s3bucket_fail_name
  ]
}
