output "dynamodb_table" {
  value = module.remote_state.dynamodb_table
}

output "kms_key" {
  value = module.remote_state.kms_key
}

output "kms_key_alias" {
  value = module.remote_state.kms_key_alias
}

output "kms_key_replica" {
  value = module.remote_state.kms_key_replica
}

output "replica_bucket" {
  value = module.remote_state.replica_bucket
}

output "state_bucket" {
  value = module.remote_state.state_bucket
}

output "terraform_iam_policy" {
  value = module.remote_state.terraform_iam_policy
}
