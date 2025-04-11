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
