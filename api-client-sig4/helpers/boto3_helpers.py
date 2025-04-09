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

import base64
import json
import os
import sys

# import boto3
# from botocore.exceptions import ClientError
from rich import print

from shared_helpers.boto3_helpers import gen_boto3_client, gen_boto3_session

session = gen_boto3_session()
lambda_client = gen_boto3_client("lambda", "eu-west-1")


def upload_local_image_2rekog_blocking(img_path, function_name):
    """
    Uploads a local image to an AWS Lambda function and processes the response.

    Args:
        img_path (str): The file path of the image to upload.
        function_name (str): The name of the AWS Lambda function to invoke.

    Returns:
        None

    Raises:
        SystemExit: If the Lambda function returns a non-200 status code.
    """
    print(f"Uploading local image {img_path}.")

    with open(img_path, "rb") as image_file:
        image_bytes = image_file.read()
        data = base64.b64encode(image_bytes).decode("utf8")

        print("Image data size:", len(data))
        print("Image data (truncated):", data[:50], "...")

        lambda_payload = json.dumps({"image": data})

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
