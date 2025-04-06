# module "exif_buckets" {
#   source = "../../modules/exif_ripper_buckets"

#   env           = var.env
#   random_string = var.random_string
#   bucket_source = "stablecaps-source"
#   bucket_dest   = "stablecaps-destination"

#   tags = local.tags

#   ssm_root_prefix = var.ssm_root_prefix

# }

module "s3_buckets" {

  source  = "terraform-aws-modules/s3-bucket/aws"
  version = "4.6.0"

  for_each = toset(local.all_s3_buckets)
  bucket   = each.value

  # bucket                  = "delemetest-dcdcdd"
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

# ### uses a custom written remote module written by me
# module "lambda_role_and_policies" {

#   source = "github.com/stablecaps/terraform-aws-iam-policies-stablecaps?ref=v2.0.0"

#   role_name = "exif-ripper-${var.env}-eu-west-1-lambdaRole"
#   role_desc = "lambda iam role for exif-ripper - ${var.env}"
#   role_path = "/lambda/${var.env}/"

#   trusted_entity_principals = {
#     Service = "lambda.amazonaws.com"
#   }

#   custom_policies  = local.custom_policies
#   managed_policies = {}

#   tags = local.tags
# }
