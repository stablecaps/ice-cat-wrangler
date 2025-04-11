
module "s3_buckets" {

  source  = "terraform-aws-modules/s3-bucket/aws"
  version = "4.6.0"

  for_each = local.s3bucket_map
  bucket   = each.value

  acl                     = "private"
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true

  control_object_ownership = true
  object_ownership         = "ObjectWriter"

  force_destroy = true

  versioning = {
    enabled = false
  }

  tags = local.tags
}

resource "aws_ssm_parameter" "s3buckets" {

  for_each = local.s3bucket_map

  name      = "${local.ssm_root_prefix}/${each.key}"
  type      = "String"
  value     = each.value
  overwrite = true

  tags = local.tags
}
