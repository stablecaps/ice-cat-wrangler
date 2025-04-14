"""
boto3_clients.py

This module provides pre-configured boto3 clients for interacting with AWS services such as SSM, S3,
and DynamoDB. The AWS region is determined from the `AWS_REGION` environment variable.

Functions:
    - gen_boto3_client: Generates a boto3 client for a specified AWS service.

Attributes:
    - aws_region (str): The AWS region to use for the boto3 clients.
    - ssm_client: A boto3 client for the AWS Systems Manager (SSM) service.
    - s3_client: A boto3 client for the AWS S3 service.
    - dyndb_client: A boto3 client for the AWS DynamoDB service.

Usage:
    Import the required client from this module to interact with AWS services.

    Example:
        from helpers.boto3_clients import s3_client

        # Use the s3_client to list buckets
        response = s3_client.list_buckets()
        print(response)

Dependencies:
    - Python 3.12 or higher
    - `boto3_helpers` module for generating boto3 clients
    - `boto3` library for AWS interactions
"""

import os

from boto3_helpers import gen_boto3_client

aws_region = os.getenv("AWS_REGION")
print(f"Using AWS region: {aws_region}")

ssm_client = gen_boto3_client("ssm", aws_region)
s3_client = gen_boto3_client("s3", aws_region)
dyndb_client = gen_boto3_client("dynamodb", aws_region)
