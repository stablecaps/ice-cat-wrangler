![terraform_infra](./images/terraform_infra.png)


<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | = 1.11.3 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | ~> 5.94.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws) | 5.94.1 |

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_s3_buckets"></a> [s3\_buckets](#module\_s3\_buckets) | terraform-aws-modules/s3-bucket/aws | 4.6.0 |

## Resources

| Name | Type |
|------|------|
| [aws_ssm_parameter.s3buckets](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ssm_parameter) | resource |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_company"></a> [company](#input\_company) | Project name | `string` | `"stablecaps"` | no |
| <a name="input_created_by"></a> [created\_by](#input\_created\_by) | Created by | `string` | `"terraform"` | no |
| <a name="input_env"></a> [env](#input\_env) | Deployment environment. e.g. dev, uat, prod | `string` | n/a | yes |
| <a name="input_owner"></a> [owner](#input\_owner) | Owner of the project | `string` | `"DevOps"` | no |
| <a name="input_project"></a> [project](#input\_project) | Project name | `string` | `"cat-wrangler"` | no |
| <a name="input_region"></a> [region](#input\_region) | AWS region. e.g. eu-west-1 | `string` | n/a | yes |
| <a name="input_s3bucket_dest_name"></a> [s3bucket\_dest\_name](#input\_s3bucket\_dest\_name) | s3 bucket destination name. Stores sucessfully processed images are stored | `string` | n/a | yes |
| <a name="input_s3bucket_fail_name"></a> [s3bucket\_fail\_name](#input\_s3bucket\_fail\_name) | s3 bucket fail name. Stores data from failed image processing | `string` | n/a | yes |
| <a name="input_s3bucket_source_name"></a> [s3bucket\_source\_name](#input\_s3bucket\_source\_name) | s3 bucket source name. Stores images to be processed | `string` | n/a | yes |
| <a name="input_unique_str"></a> [unique\_str](#input\_unique\_str) | A unique string to avoid conflicts | `string` | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_s3bucket_dest_name"></a> [s3bucket\_dest\_name](#output\_s3bucket\_dest\_name) | S3 bucket name for the destination bucket |
| <a name="output_s3bucket_fail_name"></a> [s3bucket\_fail\_name](#output\_s3bucket\_fail\_name) | S3 bucket name for the fail bucket |
| <a name="output_s3bucket_source_name"></a> [s3bucket\_source\_name](#output\_s3bucket\_source\_name) | S3 bucket name for the source bucket |
<!-- END_TF_DOCS -->
