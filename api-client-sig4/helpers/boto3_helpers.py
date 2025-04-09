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

    upload_local_image_blocking(img_path, function_name):
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
import hashlib
import json
import os
import sys
import time
from datetime import datetime

import boto3
from botocore.exceptions import ClientError
from rich import print


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


session = gen_boto3_session()
lambda_client = gen_boto3_client("lambda", "eu-west-1")


# def check_bucket_exists(bucket_name):
#     """Sanity check whether s3 bucket exists."""

#     s3_client = boto3.resource("s3")

#     try:
#         s3_client.meta.client.head_bucket(Bucket=bucket_name)
#         print("Verified bucket %s exists", bucket_name)
#     except ClientError:
#         print("s3 bucket %s does not exist or access denied", bucket_name)
#         sys.exit(1)


def fetch_env_from_ssm(ssm_keys):
    """
    Fetches environment variables from AWS SSM Parameter Store.

    Args:
        ssm_keys (list): A list of SSM parameter keys to fetch.

    Returns:
        dict: A dictionary containing the fetched environment variables.

    Raises:
        SystemExit: If any of the specified SSM keys are missing or invalid,
        or if there is an error fetching parameters from SSM.
    """
    ssm_client = gen_boto3_client("ssm", "eu-west-1")
    env_vars = {}

    try:
        response = ssm_client.get_parameters(Names=ssm_keys, WithDecryption=True)
        # Store successfully fetched parameters
        for param in response["Parameters"]:
            env_vars[param["Name"]] = param["Value"]

        # Check for missing parameters
        missing_keys = response.get("InvalidParameters", [])
        if missing_keys:
            print(
                f"Warning: The following SSM keys are missing or invalid: {missing_keys}"
            )
            sys.exit(42)

    except ClientError as err:
        print(f"Error fetching parameters from SSM: {err}")
        sys.exit(1)

    return env_vars


def upload_local_image_blocking(img_path, function_name):
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


def calculate_file_hash(file_path):
    """
    Calculates the SHA256 hash of a file.

    Args:
        file_path (str): The path to the file.

    Returns:
        str: The SHA256 hash of the file as a hexadecimal string.
    """
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def upload_images_to_s3(folder_path, bucket_name, client_id, s3_prefix="", debug=False):
    """
    Uploads all images from a local folder to a specified S3 bucket.

    Args:
        folder_path (str): The path to the local folder containing images.
        bucket_name (str): The name of the S3 bucket.
        s3_prefix (str, optional): The prefix (folder path) in the S3 bucket. Defaults to "".
        debug (bool, optional): If True, enables debug output. Defaults to False.

    Returns:
        None
    """
    s3_client = gen_boto3_client("s3", "eu-west-1")

    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)

            if not file.lower().endswith((".png", ".jpg", ".jpeg")):
                if debug:
                    print(f"Skipping non-image file: {file_path}")
                continue

            # Calculate file hash
            file_hash = calculate_file_hash(file_path)

            # Get current date and epoch timestamp
            current_date = datetime.utcnow().strftime("%Y-%m-%d")
            epoch_timestamp = int(time.time())

            # Construct the S3 key
            s3_key = f"{file_hash}/{client_id}/{current_date}/{epoch_timestamp}.png"

            try:
                print(f"Uploading {file_path} to s3://{bucket_name}/{s3_key}")
                s3_client.upload_file(file_path, bucket_name, s3_key)
            except ClientError as err:
                print(f"Error uploading {file_path} to S3: {err}")
                continue

    print("\nAll eligible images have been uploaded successfully.")
