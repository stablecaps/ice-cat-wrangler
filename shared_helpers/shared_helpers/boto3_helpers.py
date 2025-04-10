"""
boto3_helpers.py

This module provides helper functions to interact with AWS services using the Boto3 library.
It includes utilities for creating Boto3 sessions and clients, fetching environment variables
from AWS SSM Parameter Store, and uploading images to AWS Lambda functions.

Functions:
    gen_boto3_session():
        Creates and returns a Boto3 session using environment variables.

    gen_boto3_client(service_name, aws_region="eu-west-1"):
        Creates and returns a Boto3 client for a specified AWS service.

    fetch_env_from_ssm(ssm_keys):
        Fetches environment variables from AWS SSM Parameter Store.

    upload_local_image_2rekog_blocking(img_path, function_name):
        Uploads a local image to an AWS Lambda function and processes the response.

Dependencies:
    - boto3
    - botocore.exceptions.ClientError
    - requests
    - base64
    - json
    - os
    - sys
    - rich.print
"""

import os

import boto3
from botocore.exceptions import ClientError


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
