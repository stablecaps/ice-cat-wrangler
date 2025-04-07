### This arn is used in github for authorisation
output "iam_role_arn" {
  description = "IAM Role ARN for Github Actions OIDC"
  value       = module.lambda_role_and_policies.iam_role_arn
}
