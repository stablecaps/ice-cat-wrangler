
### uses a custom written remote module written by me
module "lambda_role_and_policies" {

  source = "github.com/stablecaps/terraform-aws-iam-policies-stablecaps" #?ref=v2.1.0"

  role_name = "github-actions-ice-cat-${var.env}"
  role_desc = "github actions role for ice-cat ${var.env}"
  role_path = "/stablecaps/${var.env}/${var.project}/"

  trusted_entity_principals = {
    Service = "lambda.amazonaws.com"
  }

  custom_policies = {}

  # TODO: tighten up these full perms
  managed_policies = local.managed_policy_arns

  tags = local.tags

  depends_on = [aws_iam_policy.get_iampolicies]
}


# https://mahendranp.medium.com/configure-github-openid-connect-oidc-provider-in-aws-b7af1bca97dd
