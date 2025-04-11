module "s3_serverless_deployment_bucket" {

  source  = "terraform-aws-modules/s3-bucket/aws"
  version = "4.6.0"

  bucket                  = local.bucket_name
  acl                     = "private"
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true

  control_object_ownership = true
  object_ownership         = "ObjectWriter"

  force_destroy = true

  versioning = {
    enabled = true
  }

  tags = local.tags
}


resource "aws_ssm_parameter" "sls_deploy_bucket" {

  for_each = local.ssm_map

  name      = "${local.ssm_root_prefix}/${each.key}"
  type      = "String"
  value     = each.value
  overwrite = true

  tags = local.tags
}
