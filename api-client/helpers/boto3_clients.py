import os

from boto3_helpers import gen_boto3_client

aws_region = os.getenv("AWS_REGION")
print(f"Using AWS region: {aws_region}")
ssm_client = gen_boto3_client("ssm", aws_region)
s3_client = gen_boto3_client("s3", aws_region)
dyndb_client = gen_boto3_client("dynamodb", aws_region)
