
locals {

  tags = {
    company     = var.company
    environment = var.env
    unique_str  = var.unique_str
    project     = var.project
    owner       = var.owner
    created_by  = var.created_by
    terraform   = "true"
  }

  # TODO: tighten up these full perms
  managed_policy_arns = [
    "arn:aws:iam::aws:policy/AmazonRekognitionFullAccess",
    "arn:aws:iam::aws:policy/AWSLambda_FullAccess",
    "arn:aws:iam::aws:policy/AmazonS3FullAccess",
    "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess",
    aws_iam_policy.get_iampolicies.arn,
    data.terraform_remote_state.ice_tf_remote_backend.outputs.terraform_iam_policy.arn
  ]
}
