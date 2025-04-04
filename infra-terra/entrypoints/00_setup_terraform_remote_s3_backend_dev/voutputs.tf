output "dynamodb_table" {
  description = "The DynamoDB table to manage lock states."
  value       = module.remote_state.dynamodb_table
}

output "kms_key" {
  description = "The KMS customer master key to encrypt state buckets."
  value       = module.remote_state.kms_key
}

output "kms_key_alias" {
  description = "The alias of the KMS customer master key used to encrypt state bucket and dynamodb."
  value       = module.remote_state.kms_key_alias
}

output "kms_key_replica" {
  description = "The KMS customer master key to encrypt replica bucket and dynamodb."
  value       = module.remote_state.kms_key_replica
}

output "replica_bucket" {
  description = "The S3 bucket to replicate the state S3 bucket."
  value       = module.remote_state.replica_bucket
}

output "state_bucket" {
  description = "The S3 bucket to store the remote state file."
  value       = module.remote_state.state_bucket
}

output "terraform_iam_policy" {
  description = "The IAM Policy to access remote state environment."
  value       = module.remote_state.terraform_iam_policy
}
