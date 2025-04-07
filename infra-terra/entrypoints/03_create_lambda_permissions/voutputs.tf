output "iam_role_arn" {
  description = "Lambda IAM role arn used for serverless function"
  value       = module.lambda_role_and_policies.iam_role_arn
}
