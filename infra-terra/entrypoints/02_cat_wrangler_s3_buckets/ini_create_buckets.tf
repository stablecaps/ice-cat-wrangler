module "s3_buckets" {

  source  = "terraform-aws-modules/s3-bucket/aws"
  version = "4.6.0"

  for_each = toset(local.all_s3_buckets)
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
