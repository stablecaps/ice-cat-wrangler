### This arn is used in github for authorisation
output "iam_role_arn" {
  description = "IAM Role ARN for Github Actions OIDC"
  value       = aws_iam_role.github_action_role.arn
}

output "gha_oidc_provider_arn" {
  description = "Github Actions OIDC Connect Provider ARN"
  value       = aws_iam_openid_connect_provider.github.arn
}
