### creating terraform backend **without** s3 repication. Will enable versioning
### No lifecycle rules implemented (e.g. noncurrent_version_transitions)

module "remote_state" {
  source  = "nozaq/remote-state-s3-backend/aws"
  version = "1.6.1"

  ### s3 settings
  override_s3_bucket_name = true
  s3_bucket_name          = local.base_name

  enable_replication      = false
  s3_bucket_force_destroy = false

  noncurrent_version_transitions = []


  ### DynamoDb settings
  dynamodb_table_name                    = local.base_name
  dynamodb_table_billing_mode            = "PAY_PER_REQUEST"
  dynamodb_enable_server_side_encryption = true

  ### kms
  kms_key_alias = local.base_name

  ### Iam: Defaults are fine because we should use name prefix


  providers = {
    aws         = aws
    aws.replica = aws.replica # not used but required
  }

  tags = local.tags
}
