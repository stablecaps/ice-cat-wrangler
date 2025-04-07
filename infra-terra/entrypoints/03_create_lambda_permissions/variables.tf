variable "aws_acc_no" {
  description = "AWS account number"
  type        = string
}

variable "project" {
  description = "Project name"
  type        = string
  default     = "cat-wrangler"
}

variable "owner" {
  description = "Owner of the project"
  type        = string
  default     = "DevOps"
}

variable "created_by" {
  description = "Created by"
  type        = string
  default     = "terraform"
}

variable "region" {
  description = "AWS region. e.g. eu-west-1"
  type        = string
}

variable "env" {
  description = "Deployment environment. e.g. dev, uat, prod"
  type        = string
}

variable "unique_str" {
  description = "A unique string to avoid conflicts"
  type        = string
}

variable "s3bucket_source_name" {
  description = "s3 bucket source name. Stores images to be processed"
  type        = string
}


variable "s3bucket_dest_name" {
  description = "s3 bucket destination name. Stores sucessfully processed images are stored"
  type        = string
}

variable "s3bucket_fail_name" {
  description = "s3 bucket fail name. Stores data from failed image processing"
  type        = string
}
