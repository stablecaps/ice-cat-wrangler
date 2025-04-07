"""Boto3 helpers to run AWS routines."""

import base64
import json
import os
import sys

import boto3
from botocore.exceptions import ClientError
from rich import print


def get_boto3_session():
    """Creates and returns a Boto3 session using environment variables.

    Returns:
        boto3.Session: A Boto3 session object.
    """
    return boto3.Session(
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        aws_session_token=os.getenv("AWS_SESSION_TOKEN"),
        region_name=os.getenv("AWS_REGION"),
    )


def create_boto3_client(service_name, aws_region="eu-west-1"):
    """Creates and returns a Boto3 client for a specified AWS service.

    Args:
        service_name (str): The name of the AWS service (e.g., 's3', 'lambda').

    Returns:
        boto3.Client: A Boto3 client object for the specified service.
    """
    session = get_boto3_session()
    return session.client(service_name, aws_region)


session = get_boto3_session()
lambda_client = create_boto3_client("lambda", "eu-west-1")


# def check_bucket_exists(bucket_name):
#     """Sanity check whether s3 bucket exists."""

#     s3_client = boto3.resource("s3")

#     try:
#         s3_client.meta.client.head_bucket(Bucket=bucket_name)
#         print("Verified bucket %s exists", bucket_name)
#     except ClientError:
#         print("s3 bucket %s does not exist or access denied", bucket_name)
#         sys.exit(1)

import requests


def upload_local_image_blocking(img_path, function_name):

    print(f"Uploading local image {img_path}.")

    with open(img_path, "rb") as image_file:
        image_bytes = image_file.read()
        data = base64.b64encode(image_bytes).decode("utf8")

        print("Image data size:", len(data))
        print("Image data (truncated):", data[:50], "...")

        lambda_payload = json.dumps({"image": data})
        # return lambda_payload

        # Invoke the Lambda function with the event payload
        response = lambda_client.invoke(
            FunctionName=function_name, Payload=(lambda_payload)
        )
        print("\nsubmit status code", response["StatusCode"])

        rekog_decoded = json.loads(response["Payload"].read().decode())

        if rekog_decoded["statusCode"] != 200:
            print("\nrekog_decoded", rekog_decoded)
            sys.exit(42)

        print("\nrekog_decoded", rekog_decoded["body"])
        print("\nrekog_decoded", rekog_decoded["statusCode"])

        return
