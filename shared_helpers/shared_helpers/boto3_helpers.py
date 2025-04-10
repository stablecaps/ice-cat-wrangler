import logging
import os
import sys

import boto3
from botocore.exceptions import ClientError

LOG = logging.getLogger(__name__)


def gen_boto3_session():
    """
    Creates and returns a Boto3 session using environment variables.

    Returns:
        boto3.Session: A Boto3 session object initialized with AWS credentials
        and region from environment variables.
    """
    return boto3.Session(
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        aws_session_token=os.getenv("AWS_SESSION_TOKEN"),
        region_name=os.getenv("AWS_REGION"),
    )


def gen_boto3_client(service_name, aws_region="eu-west-1"):
    """
    Creates and returns a Boto3 client for a specified AWS service.

    Args:
        service_name (str): The name of the AWS service (e.g., 's3', 'lambda').
        aws_region (str, optional): The AWS region to use. Defaults to "eu-west-1".

    Returns:
        boto3.Client: A Boto3 client object for the specified service.
    """
    session = gen_boto3_session()
    return session.client(service_name, aws_region)


def check_bucket_exists(bucket_name):
    """Sanity check whether S3 bucket exists using a Boto3 client."""

    s3_client = gen_boto3_client("s3", "eu-west-1")

    try:
        s3_client.head_bucket(Bucket=bucket_name)
        LOG.info("Verified bucket <%s> exists", bucket_name)
    except ClientError as err:
        error_code = err.response["Error"]["Code"]
        if error_code == "404":
            print("S3 bucket <%s> does not exist", bucket_name)
        elif error_code == "403":
            print("Access denied to S3 bucket <%s>", bucket_name)
        else:
            print("Failed to verify S3 bucket <%s>: <%s>", bucket_name, err)
        sys.exit(1)
