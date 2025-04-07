![terraform_infra](./images/terraform_infra.png)


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
| <a name="module_lambda_role_and_policies"></a> [lambda\_role\_and\_policies](#module\_lambda\_role\_and\_policies) | github.com/stablecaps/terraform-aws-iam-policies-stablecaps | v2.0.0 |

## Resources

No resources.

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_created_by"></a> [created\_by](#input\_created\_by) | Created by | `string` | `"terraform"` | no |
| <a name="input_env"></a> [env](#input\_env) | Deployment environment. e.g. dev, uat, prod | `string` | n/a | yes |
| <a name="input_owner"></a> [owner](#input\_owner) | Owner of the project | `string` | `"DevOps"` | no |
| <a name="input_project"></a> [project](#input\_project) | Project name | `string` | `"cat-wrangler"` | no |
| <a name="input_region"></a> [region](#input\_region) | AWS region. e.g. eu-west-1 | `string` | n/a | yes |
| <a name="input_unique_str"></a> [unique\_str](#input\_unique\_str) | A unique string to avoid conflicts | `string` | n/a | yes |

## Outputs

No outputs.
<!-- END_TF_DOCS -->
