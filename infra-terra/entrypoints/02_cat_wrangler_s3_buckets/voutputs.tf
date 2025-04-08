output "s3bucket_source_name" {
  description = "S3 bucket name for the source bucket"
  value       = module.s3_buckets["s3bucket_source"].s3_bucket_id
}

output "s3bucket_dest_name" {
  description = "S3 bucket name for the destination bucket"
  value       = module.s3_buckets["s3bucket_dest"].s3_bucket_id
}

output "s3bucket_fail_name" {
  description = "S3 bucket name for the fail bucket"
  value       = module.s3_buckets["s3bucket_fail"].s3_bucket_id
}
