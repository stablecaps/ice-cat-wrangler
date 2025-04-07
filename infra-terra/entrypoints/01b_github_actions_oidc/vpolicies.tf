data "aws_iam_policy_document" "github_actions_oidc" {
  statement {
    sid     = "GithubActionsRepoAssume"
    actions = ["sts:AssumeRoleWithWebIdentity"]
    principals {
      type        = "Federated"
      identifiers = [aws_iam_openid_connect_provider.github.arn]
    }
    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }
    condition {
      test     = "StringLike"
      variable = "token.actions.githubusercontent.com:sub"

      values = ["repo:stablecaps/ice-cat-wrangler:*"]
    }
  }
}


############################################
resource "aws_iam_policy" "get_iampolicies" {
  name_prefix = "githubactions_getiam"
  path        = "/"
  policy      = data.aws_iam_policy_document.get_iampolicy_docs.json

  lifecycle {
    create_before_destroy = true
  }
}

data "aws_iam_policy_document" "get_iampolicy_docs" {
  statement {
    sid = "iamGetPassRole"
    actions = [
      "iam:GetRole",
      "iam:GetPolicy",
      "iam:GetPolicyVersion",
      "iam:ListRolePolicies"
    ]
    # TODO: tighten up resource paths
    resources = [
      # "arn:aws:iam::${var.aws_acc_no}:policy/${var.project}*",
      # "arn:aws:iam::${var.aws_acc_no}:role/${var.project}*",
      "arn:aws:iam::${var.aws_acc_no}:policy/*",
      "arn:aws:iam::${var.aws_acc_no}:role/*",
    ]
  }
}
