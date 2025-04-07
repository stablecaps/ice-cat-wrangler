resource "aws_iam_role" "github_action_role" {
  name_prefix = "github-actions-ice-cat-${var.env}"
  description = "github actions role for ice-cat ${var.env}"
  path        = "/stablecaps/${var.env}/${var.project}/"

  assume_role_policy = data.aws_iam_policy_document.github_actions_oidc.json

}

### Loop & attach AWS managed policies
resource "aws_iam_role_policy_attachment" "this" {

  count = length(local.managed_policy_arns)

  role       = aws_iam_role.github_action_role.name
  policy_arn = local.managed_policy_arns[count.index]
}


# https://mahendranp.medium.com/configure-github-openid-connect-oidc-provider-in-aws-b7af1bca97dd
