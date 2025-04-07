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

      values = ["repo:ice-cat-wrangler/*"]
    }
  }
}

data "aws_iam_policy_document" "github_actions_ecr" {
  statement {
    sid = "RepoReadWriteAccess"
    actions = [
      "ecr:BatchGetImage",
      "ecr:BatchCheckLayerAvailability",
      "ecr:CompleteLayerUpload",
      "ecr:GetDownloadUrlForLayer",
      "ecr:InitiateLayerUpload",
      "ecr:PutImage",
      "ecr:UploadLayerPart",
    ]
    resources = [
      "arn:aws:ecr:eu-west-1:${var.aws_acc_no}:repository/*"
    ]
  }

  statement {
    sid       = "GetAuthorizationToken"
    actions   = ["ecr:GetAuthorizationToken"]
    resources = ["*"]
  }
}

############################################
resource "aws_iam_policy" "iam_getpolicy" {
  name_prefix = "githubactions_getiam"
  path        = "/"
  policy      = data.aws_iam_policy_document.iam_get_poldoc.json

  lifecycle {
    create_before_destroy = true
  }
}

data "aws_iam_policy_document" "iam_get_poldoc" {
  statement {
    sid = "iamGetPassRole"
    actions = [
      "iam:GetRole",
      "iam:GetPolicy",
      "iam:GetPolicyVersion",
      "iam:ListRolePolicies"
    ]
    resources = [
      "arn:aws:iam::${var.aws_acc_no}:policy/${var.project}*",
      "arn:aws:iam::${var.aws_acc_no}:role/${var.project}*",
    ]
  }
}
