### uses a custom written remote module written by me
module "lambda_role_and_policies" {

  source = "github.com/stablecaps/terraform-aws-iam-policies-stablecaps?ref=v2.1.0"

  role_name = "${local.lambda_cat_wrangler_app_role_name}-role"
  role_desc = "lambda iam role for ${local.lambda_cat_wrangler_app_role_name}"
  role_path = "/lambda/${var.env}/${var.project}/"

  trusted_entity_principals = {
    Service = "lambda.amazonaws.com"
  }

  custom_policies = local.lambda_cat_wrangler_app_custom_policy

  managed_policies = [
    "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
    "arn:aws:iam::aws:policy/AmazonRekognitionFullAccess",
    "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess"
  ]

  tags = local.tags
}


resource "aws_ssm_parameter" "lambda_role_cat_arn" {

  name      = "${local.ssm_root_prefix}/lambda_role_cat_arn"
  type      = "String"
  value     = module.lambda_role_and_policies.iam_role_arn
  overwrite = true

  tags = local.tags
}
