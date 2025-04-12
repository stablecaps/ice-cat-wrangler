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

  s3bucket_map = {
    S3BUCKET_SOURCE = "${var.s3bucket_source_name}-${var.unique_str}-${var.env}"
    S3BUCKET_DEST   = "${var.s3bucket_dest_name}-${var.unique_str}-${var.env}"
    S3BUCKET_FAIL   = "${var.s3bucket_fail_name}-${var.unique_str}-${var.env}"
  }

}
