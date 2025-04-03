![terraform_infra](./images/terraform_infra.png)


![terraform_infra](./)


![terraform_infra](./)


<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | = 1.11.3 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | ~> 5.94.0 |

## Providers

No providers.

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_remote_state"></a> [remote\_state](#module\_remote\_state) | nozaq/remote-state-s3-backend/aws | 1.6.1 |

## Resources

No resources.

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_env"></a> [env](#input\_env) | Deployment environment. e.g. dev, uat, prod | `string` | n/a | yes |
| <a name="input_region"></a> [region](#input\_region) | AWS region. e.g. eu-west-1 | `string` | n/a | yes |
| <a name="input_unique_str"></a> [unique\_str](#input\_unique\_str) | A unique string to avoid conflicts | `string` | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_dynamodb_table"></a> [dynamodb\_table](#output\_dynamodb\_table) | n/a |
| <a name="output_kms_key"></a> [kms\_key](#output\_kms\_key) | n/a |
| <a name="output_kms_key_alias"></a> [kms\_key\_alias](#output\_kms\_key\_alias) | n/a |
| <a name="output_kms_key_replica"></a> [kms\_key\_replica](#output\_kms\_key\_replica) | n/a |
| <a name="output_replica_bucket"></a> [replica\_bucket](#output\_replica\_bucket) | n/a |
| <a name="output_state_bucket"></a> [state\_bucket](#output\_state\_bucket) | n/a |
| <a name="output_terraform_iam_policy"></a> [terraform\_iam\_policy](#output\_terraform\_iam\_policy) | n/a |
<!-- END_TF_DOCS -->