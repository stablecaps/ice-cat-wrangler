resource "aws_dynamodb_table" "image_cat" {
  name         = "image_cat"
  billing_mode = "PAY_PER_REQUEST"

  table_class                 = "STANDARD"
  deletion_protection_enabled = false


  hash_key = "userId"
  attribute {
    name = "userId"
    type = "S" # String data type
  }

  lifecycle {
    prevent_destroy = true
  }

  ttl {
    enabled        = true
    attribute_name = "ttl"
  }

  tags = local.tags
}
