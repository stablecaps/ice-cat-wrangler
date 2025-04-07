resource "aws_iam_openid_connect_provider" "github" {
  url = "https://token.actions.githubusercontent.com"

  client_id_list = [
    "sts.amazonaws.com",
  ]

  # thumbprints are deprecated with aws, so set to "ffffffffffffffffffffffffffffffffffffffff"
  thumbprint_list = ["ffffffffffffffffffffffffffffffffffffffff"]

  tags = local.tags
}
