resource "aws_dynamodb_table" "image_cat" {
  name         = "IceCatWrangler"
  billing_mode = "PAY_PER_REQUEST"

  table_class                 = "STANDARD"
  deletion_protection_enabled = false

  # Primary Key
  hash_key  = "batch_id"
  range_key = "img_fprint"

  # Attributes
  attribute {
    name = "batch_id"
    type = "N"
  }

  attribute {
    name = "img_fprint"
    type = "S"
  }

  attribute {
    name = "client_id"
    type = "S"
  }

  attribute {
    name = "op_status"
    type = "S"
  }

  attribute {
    name = "rek_iscat"
    type = "S" # (Boolean stored as string)
  }

  attribute {
    name = "upload_ts"
    type = "N"
  }

  # Global Secondary Indexes (GSIs)
  global_secondary_index {
    name            = "GSI1"
    hash_key        = "batch_id"
    range_key       = "upload_ts"
    projection_type = "ALL"
  }

  global_secondary_index {
    name            = "GSI2"
    hash_key        = "client_id"
    range_key       = "upload_ts"
    projection_type = "ALL"
  }

  global_secondary_index {
    name            = "GSI3"
    hash_key        = "batch_id"
    range_key       = "client_id"
    projection_type = "ALL"
  }

  global_secondary_index {
    name            = "GSI4"
    hash_key        = "batch_id"
    range_key       = "op_status"
    projection_type = "ALL"
  }

  global_secondary_index {
    name            = "GSI5"
    hash_key        = "rek_iscat"
    range_key       = "upload_ts"
    projection_type = "ALL"
  }

  ttl {
    enabled        = true
    attribute_name = "ttl"
  }
  lifecycle {
    prevent_destroy = true
  }

  # Tags
  tags = local.tags
}
