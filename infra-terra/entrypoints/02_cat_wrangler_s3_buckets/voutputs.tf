output "s3bucket_source_name" {
  description = "S3 bucket name for the source bucket"
  value       = module.s3_buckets["S3BUCKET_SOURCE"].s3_bucket_id
}

output "s3bucket_dest_name" {
  description = "S3 bucket name for the destination bucket"
  value       = module.s3_buckets["S3BUCKET_DEST"].s3_bucket_id
}

output "s3bucket_fail_name" {
  description = "S3 bucket name for the fail bucket"
  value       = module.s3_buckets["S3BUCKET_FAIL"].s3_bucket_id
}
