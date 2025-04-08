locals {
  lambda_cat_wrangler_app_custom_policy = {
    "${local.lambda_cat_wrangler_app_role_name}-pol" = {
      Version = "2012-10-17"
      Statement = [
        {
          "Sid" : "VisualEditor0",
          "Effect" : "Allow",
          "Action" : [
            "s3:PutObject",
            "s3:GetObject",
            "logs:CreateLogStream",
            "s3:ListBucket",
            "logs:CreateLogGroup",
            "s3:PutObjectAcl"
          ],
          "Resource" : [
            "arn:aws:logs:eu-west-1:${var.aws_acc_no}:log-group:/aws/lambda/*",
            "arn:aws:logs:eu-west-1:${var.aws_acc_no}:log-group:/aws/lambda/*",
            "arn:aws:s3:::${local.s3bucket_source_fullname}",
            "arn:aws:s3:::${local.s3bucket_dest_fullname}",
            "arn:aws:s3:::${local.s3bucket_fail_fullname}",
          ]
        },
        {
          "Sid" : "VisualEditor1",
          "Effect" : "Allow",
          "Action" : [
            "logs:PutLogEvents"
          ],
          "Resource" : [
            "arn:aws:logs:eu-west-1:${var.aws_acc_no}:log-group:/aws/lambda/*:log-stream:*",
            "arn:aws:logs:eu-west-1:${var.aws_acc_no}:log-group:/aws/lambda/*:*:*"
          ]
        }
      ]
    }
  }

}
