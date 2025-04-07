### uses a custom written remote module written by me
module "lambda_role_and_policies" {

  source = "github.com/stablecaps/terraform-aws-iam-policies-stablecaps?ref=v2.1.0"

  role_name = "${local.func_analyser_role_name}-role"
  role_desc = "lambda iam role for ${local.func_analyser_role_name}"
  role_path = "/lambda/${var.env}/${var.project}/"

  trusted_entity_principals = {
    Service = "lambda.amazonaws.com"
  }

  custom_policies = local.func_analyser_custom_policy

  managed_policies = ["arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole", "arn:aws:iam::aws:policy/AmazonRekognitionFullAccess"]

  tags = local.tags
}
