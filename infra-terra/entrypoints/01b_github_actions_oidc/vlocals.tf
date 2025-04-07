
locals {

  tags = {
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
    aws_iam_policy.iam_getpolicy.arn,
  ]
}
