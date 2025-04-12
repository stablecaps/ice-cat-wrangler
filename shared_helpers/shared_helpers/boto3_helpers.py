import logging
import os
import sys

import boto3
from botocore.exceptions import ClientError

# from general import safeget


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


def gen_boto3_client(service_name, aws_region=None):
    """
    Creates and returns a Boto3 client for a specified AWS service.

    Args:
        service_name (str): The name of the AWS service (e.g., 's3', 'lambda').
        aws_region (str, optional): The AWS region to use. Defaults to "eu-west-1".

    Returns:
        boto3.Client: A Boto3 client object for the specified service.
    """
    aws_region = aws_region or os.getenv("AWS_REGION", "eu-west-1")
    session = gen_boto3_session()
    return session.client(service_name, aws_region)


def safeget(dct, *keys):
    """
    Recover value safely from nested dictionary

    safeget(example_dict, 'key1', 'key2')
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
    """Sanity check whether S3 bucket exists using a Boto3 client."""

    try:
        s3_client.head_bucket(Bucket=bucket_name)
        LOG.info("Verified bucket <%s> exists", bucket_name)
    except ClientError as err:
        error_code = err.response["Error"]["Code"]
        if error_code == "404":
            LOG.critical("S3 bucket <%s> does not exist", bucket_name)
        elif error_code == "403":
            LOG.critical("Access denied to S3 bucket <%s>", bucket_name)
        else:
            LOG.critical("Failed to verify S3 bucket <%s>: <%s>", bucket_name, err)
        sys.exit(42)


def get_filebytes_from_s3(s3_client, bucket_name, s3_key):
    """
    Retrieve a file from an S3 bucket.

    Args:
        bucket_name (str): The name of the S3 bucket.
        s3_key (str): The key of the object in the S3 bucket.

    Returns:
        bytes: The content of the file as bytes.
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


def copy_s3_object(
    s3_client, source_bucket, dest_bucket, s3_key, acl="bucket-owner-full-control"
):
    """
    Copy an object from one S3 bucket to another.

    Args:
        s3_client (boto3.client): The S3 client instance.
        source_bucket (str): The source S3 bucket name.
        dest_bucket (str): The destination S3 bucket name.
        s3_key (str): The key of the object to copy.
        acl (str): The ACL to apply to the copied object. Default is "bucket-owner-full-control".

    Returns:
        None
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


# TODO: return true/false from this so we can set op status to fail if copt fails
def move_s3_object_based_on_rekog_response(
    s3_client, op_status, s3bucket_source, s3bucket_dest, s3bucket_fail, s3_key
):
    """
    Handle the Rekognition response and move the image to the appropriate S3 bucket.

    Args:
        op_status (str): success or failure status of the Rekognition operation.
        s3bucket_source (str): The source S3 bucket name.
        s3bucket_dest (str): The destination S3 bucket name for successful processing.
        s3bucket_fail (str): The destination S3 bucket name for failed processing.
        s3_key (str): The key of the object in the S3 bucket.

    Returns:
        None
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
            ACL="bucket-owner-full-control",
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

    try:
        rekog_resp = rekog_client.detect_labels(
            Image={"Bytes": image_bytes},
            MaxLabels=10,
            MinConfidence=75,
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
