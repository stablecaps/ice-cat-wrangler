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
            "arn:aws:logs:eu-west-1:779934699932:log-group:/aws/lambda/exif-ripper-${var.env}-exif",
            "arn:aws:logs:eu-west-1:779934699932:log-group:/aws/lambda/exif-ripper-${var.env}*:*",
            # "arn:aws:s3:::${local.bucket_source}",
            # "arn:aws:s3:::${local.bucket_dest}",
            # "arn:aws:s3:::serverless-deployment-holder-658fi8r7",
            # "arn:aws:s3:::serverless-deployment-holder-658fi8r7/*",
            # "arn:aws:s3:::${local.bucket_source}/*",
            # "arn:aws:s3:::${local.bucket_dest}/*"
          ]
        },
        {
          "Sid" : "VisualEditor1",
          "Effect" : "Allow",
          "Action" : [
            "logs:PutLogEvents"
          ],
          "Resource" : [
            "arn:aws:logs:eu-west-1:779934699932:log-group:/aws/lambda/exif-ripper-${var.env}-exif:log-stream:*",
            "arn:aws:logs:eu-west-1:779934699932:log-group:/aws/lambda/exif-ripper-${var.env}*:*:*"
          ]
        }
      ]
    }
  }
}
