from boto3_helpers import gen_boto3_client

ssm_client = gen_boto3_client("ssm", "eu-west-1")
s3_client = gen_boto3_client("s3", "eu-west-1")
