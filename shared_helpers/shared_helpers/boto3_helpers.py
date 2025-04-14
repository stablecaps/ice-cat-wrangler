"""
boto3_helpers.py

This module provides helper functions for interacting with AWS services using boto3. It includes utilities
for generating boto3 sessions and clients, performing S3 operations, and categorizing images using AWS
Rekognition.

Functions:
    - gen_boto3_session: Creates a boto3 session using environment variables.
    - gen_boto3_client: Creates a boto3 client for a specified AWS service.
    - safeget: Safely retrieves a value from a nested dictionary.
    - check_bucket_exists: Checks whether an S3 bucket exists.
    - get_filebytes_from_s3: Retrieves the contents of a file from an S3 bucket as bytes.
    - copy_s3_object: Copies an object from one S3 bucket to another.
    - move_s3_object_based_on_rekog_response: Moves an S3 object based on Rekognition results.
    - rekog_image_categorise: Categorizes an image using AWS Rekognition.

Dependencies:
    - Python 3.12 or higher
    - `boto3` for AWS interactions
    - `botocore` for handling AWS client errors
"""

import logging
import os

import boto3
from botocore.exceptions import ClientError

# TODO: check logs propagate into dynamodb
# use without __name__ as this module will propagate logs to lambda root logger to enable LogCollectorHandler
LOG = logging.getLogger()


DEFAULT_S3_ACL = "bucket-owner-full-control"
DEFAULT_MIN_CONFIDENCE = 75
MAX_LABELS = 10


def gen_boto3_session():
    """
    Creates and returns a boto3 session using environment variables.

    Returns:
        boto3.Session: A boto3 session object initialized with AWS credentials and region.
    """
    return boto3.Session(
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        aws_session_token=os.getenv("AWS_SESSION_TOKEN"),
        region_name=os.getenv("AWS_REGION"),
    )


def gen_boto3_client(service_name, aws_region=None):
    """
    Creates and returns a boto3 client for a specified AWS service.

    Args:
        service_name (str): The name of the AWS service (e.g., 's3', 'rekognition').
        aws_region (str, optional): The AWS region to use. Defaults to "eu-west-1".

    Returns:
        boto3.Client: A boto3 client object for the specified service.
    """
    aws_region = aws_region or os.getenv("AWS_REGION", "eu-west-1")
    session = gen_boto3_session()
    return session.client(service_name, aws_region)


def safeget(dct, *keys):
    """
    Safely retrieves a value from a nested dictionary.

    Args:
        dct (dict): The dictionary to retrieve the value from.
        *keys (str): The keys to traverse in the dictionary.

    Returns:
        Any: The value if found, otherwise None.
    """
    for key in keys:
        try:
            dct = dct[key]
        except KeyError:
            return None
    return dct


################################################################################
# s3 functions
def check_bucket_exists(s3_client, bucket_name):
    """
    Checks whether an S3 bucket exists.

    Args:
        s3_client (boto3.client): The S3 client instance.
        bucket_name (str): The name of the S3 bucket to check.

    Raises:
        ClientError: If the bucket does not exist or access is denied.
    """
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        LOG.info("Verified bucket <%s> exists", bucket_name)
    except ClientError as err:
        error_code = safeget(err.response, "Error", "Code")
        if error_code == "404":
            LOG.critical("S3 bucket <%s> does not exist", bucket_name)
            raise ValueError(f"S3 bucket <{bucket_name}> does not exist") from err
        if error_code == "403":
            LOG.critical("Access denied to S3 bucket <%s>", bucket_name)
            raise PermissionError(
                f"Access denied to S3 bucket <{bucket_name}>"
            ) from err

        LOG.critical("Failed to verify S3 bucket <%s>: <%s>", bucket_name, err)
        raise RuntimeError(
            f"Failed to verify S3 bucket <{bucket_name}>: {err}", bucket_name, err
        ) from err


def get_filebytes_from_s3(s3_client, bucket_name, s3_key):
    """
    Retrieves the contents of a file from an S3 bucket as bytes.

    Args:
        s3_client (boto3.client): The S3 client instance.
        bucket_name (str): The name of the S3 bucket.
        s3_key (str): The key of the file in the S3 bucket.

    Returns:
        bytes: The contents of the file as bytes.

    Raises:
        ClientError: If there is an error retrieving the file.
        Exception: For any unexpected errors.
    """
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=s3_key)
        file_bytes = response["Body"].read()
        return file_bytes
    except ClientError as err:
        LOG.error(
            "ClientError while retrieving file <%s> from bucket <%s>: <%s>",
            s3_key,
            bucket_name,
            err,
        )
        raise
    except Exception as err:
        LOG.error(
            "Unexpected error while retrieving file <%s> from bucket <%s>: <%s>",
            s3_key,
            bucket_name,
            err,
        )
        raise


def copy_s3_object(s3_client, source_bucket, dest_bucket, s3_key, acl=DEFAULT_S3_ACL):
    """
    Copies an object from one S3 bucket to another.

    Args:
        s3_client (boto3.client): The S3 client instance.
        source_bucket (str): The name of the source S3 bucket.
        dest_bucket (str): The name of the destination S3 bucket.
        s3_key (str): The key of the object to copy.
        acl (str, optional): The ACL to apply to the copied object. Defaults to "bucket-owner-full-control".

    Raises:
        ClientError: If there is an error copying the object.
    """
    try:
        copy_source = {"Bucket": source_bucket, "Key": s3_key}
        s3_client.copy_object(
            CopySource=copy_source,
            Bucket=dest_bucket,
            Key=s3_key,
            ACL=acl,
        )
        LOG.info(
            "Object <%s> copied from <%s> to %s", s3_key, source_bucket, dest_bucket
        )
    except ClientError as err:
        LOG.error(
            "Error copying object <%s> from <%s> to %s: %s",
            s3_key,
            source_bucket,
            dest_bucket,
            err,
        )
        raise


def move_s3_object_based_on_rekog_response(
    s3_client, op_status, s3bucket_source, s3bucket_dest, s3bucket_fail, s3_key
):
    """
    Moves an S3 object based on Rekognition results.

    Args:
        s3_client (boto3.client): The S3 client instance.
        op_status (str): The operation status ("success" or "failure").
        s3bucket_source (str): The source S3 bucket name.
        s3bucket_dest (str): The destination S3 bucket name for successful processing.
        s3bucket_fail (str): The destination S3 bucket name for failed processing.
        s3_key (str): The key of the object in the S3 bucket.

    Returns:
        bool: True if the object was moved successfully, False otherwise.

    Raises:
        ClientError: If there is an error moving the object.
        Exception: For any unexpected errors.
    """
    try:
        if op_status == "success":
            target_bucket = s3bucket_dest
        else:
            target_bucket = s3bucket_fail

        copy_source = {"Bucket": s3bucket_source, "Key": s3_key}
        s3_client.copy_object(
            CopySource=copy_source,
            Bucket=target_bucket,
            Key=s3_key,
            ACL=DEFAULT_S3_ACL,
        )
        s3_client.delete_object(Bucket=s3bucket_source, Key=s3_key)
        LOG.info("Moved object <%s> to <%s>", s3_key, target_bucket)
        return True

    except ClientError as err:
        LOG.error("Error moving object %s: %s", s3_key, err)
        raise
    except Exception as err:
        LOG.error("Unexpected error while handling Rekognition response: %s", err)
        raise


################################################################################
# rekognition functions
def rekog_image_categorise(rekog_client, image_bytes, label_pattern="cat"):
    """
    Categorizes an image using AWS Rekognition.

    Args:
        rekog_client (boto3.client): The Rekognition client instance.
        image_bytes (bytes): The image data as bytes.
        label_pattern (str, optional): The label pattern to match. Defaults to "cat".

    Returns:
        dict: A dictionary containing the Rekognition response and match status.

    Raises:
        Exception: If there is an error processing the image.
    """
    try:
        rekog_resp = rekog_client.detect_labels(
            Image={"Bytes": image_bytes},
            MaxLabels=MAX_LABELS,
            MinConfidence=DEFAULT_MIN_CONFIDENCE,
        )

        # Print labels detected
        labels = [label["Name"].lower() for label in rekog_resp["Labels"]]

        rek_match = "False"
        if label_pattern in labels:
            rek_match = "True"

        LOG.info("Labels detected: <%s>", labels)
        LOG.info("rek_match for label_pattern: <%s> is <%s>", label_pattern, rek_match)

        return {"rekog_resp": rekog_resp, "rek_match": rek_match}

    except Exception as err:
        LOG.error("Error processing image from S3: <%s>", err)
        raise
