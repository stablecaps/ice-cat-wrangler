resource "aws_iam_role" "github_actions" {
  name_prefix        = "github-actions-ecr-role-${var.env}"
  assume_role_policy = data.aws_iam_policy_document.github_actions_oidc.json

  path = "/providers/${var.env}/${var.project}/"

  # inline_policy {
  #   name   = "github-action-ecr"
  #   policy = data.aws_iam_policy_document.github_actions_ecr.json
  # }


  lifecycle {
    create_before_destroy = true
  }

  tags = local.tags
}

# TODO: tighten up these full perms
resource "aws_iam_role_policy_attachment" "attach" {
  count      = length(local.managed_policy_arns)
  role       = aws_iam_role.github_actions.name
  policy_arn = local.managed_policy_arns[count.index]
}

# https://mahendranp.medium.com/configure-github-openid-connect-oidc-provider-in-aws-b7af1bca97dd
