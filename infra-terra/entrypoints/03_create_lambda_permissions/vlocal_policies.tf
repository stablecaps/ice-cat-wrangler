locals {
  func_analyser_custom_policy = {
    "${local.func_analyser_role_name}-pol" = {
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
            "arn:aws:s3:::${var.s3bucket_source_name}",
            "arn:aws:s3:::${var.s3bucket_dest_name}",
            "arn:aws:s3:::${var.s3bucket_fail_name}",
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
