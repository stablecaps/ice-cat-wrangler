locals {
  lambda_cat_wrangler_app_custom_policy = {
    "${local.lambda_cat_wrangler_app_role_name}-pol" = {
      Version = "2012-10-17"
      Statement = [
        {
          "Sid" : "VisualEditor0",
          "Effect" : "Allow",
          "Action" : [
            "s3:ListBucket",
            "logs:CreateLogStream",
            "logs:CreateLogGroup"
          ],
          "Resource" : [
            "arn:aws:logs:${var.region}:${var.aws_acc_no}:log-group:/aws/lambda/*",
            "arn:aws:logs:${var.region}:${var.aws_acc_no}:log-group:/aws/lambda/*",
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
            "arn:aws:logs:${var.region}:${var.aws_acc_no}:log-group:/aws/lambda/*:log-stream:*",
            "arn:aws:logs:${var.region}:${var.aws_acc_no}:log-group:/aws/lambda/*:*:*"
          ]
        },
        {
          "Sid" : "VisualEditor2",
          "Effect" : "Allow",
          "Action" : [
            "s3:PutObject",
            "s3:GetObject",
            "s3:PutObjectAcl",
            "s3:DeleteObject",
          ],
          "Resource" : [
            "arn:aws:s3:::${local.s3bucket_source_fullname}/*",
            "arn:aws:s3:::${local.s3bucket_dest_fullname}/*",
            "arn:aws:s3:::${local.s3bucket_fail_fullname}/*",
          ]
        }
      ]
    }
  }

}
