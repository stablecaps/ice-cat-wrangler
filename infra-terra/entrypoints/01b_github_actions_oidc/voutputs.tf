### This arn is used in github for authorisation
output "iam_role_arn" {
  value = aws_iam_role.github_actions.arn
}
