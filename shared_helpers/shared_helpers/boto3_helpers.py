import logging
import os
import sys

import boto3
from botocore.exceptions import ClientError

# from general import safeget

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
            print("S3 bucket <%s> does not exist", bucket_name)
        elif error_code == "403":
            print("Access denied to S3 bucket <%s>", bucket_name)
        else:
            print("Failed to verify S3 bucket <%s>: <%s>", bucket_name, err)
        sys.exit(1)


def get_filebytes_from_s3(s3_client, bucket_name, object_key):
    """
    Retrieve a file from an S3 bucket.

    Args:
        bucket_name (str): The name of the S3 bucket.
        object_key (str): The key of the object in the S3 bucket.

    Returns:
        bytes: The content of the file as bytes.
    """
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        file_bytes = response["Body"].read()
        return file_bytes
    except ClientError as err:
        LOG.error(
            "ClientError while retrieving file <%s> from bucket <%s>: <%s>",
            object_key,
            bucket_name,
            err,
        )
        raise
        raise
    except Exception as err:
        LOG.error(
            "Unexpected error while retrieving file <%s> from bucket <%s>: <%s>",
            object_key,
            bucket_name,
            err,
        )
        raise


def copy_s3_object(
    s3_client, source_bucket, dest_bucket, object_key, acl="bucket-owner-full-control"
):
    """
    Copy an object from one S3 bucket to another.

    Args:
        s3_client (boto3.client): The S3 client instance.
        source_bucket (str): The source S3 bucket name.
        dest_bucket (str): The destination S3 bucket name.
        object_key (str): The key of the object to copy.
        acl (str): The ACL to apply to the copied object. Default is "bucket-owner-full-control".

    Returns:
        None
    """
    try:
        copy_source = {"Bucket": source_bucket, "Key": object_key}
        s3_client.copy_object(
            CopySource=copy_source,
            Bucket=dest_bucket,
            Key=object_key,
            ACL=acl,
        )
        LOG.info(
            "Object <%s> copied from <%s> to %s", object_key, source_bucket, dest_bucket
        )
    except ClientError as err:
        LOG.error(
            "Error copying object <%s> from <%s> to %s: %s",
            object_key,
            source_bucket,
            dest_bucket,
            err,
        )
        raise


def move_s3_object_based_on_rekog_response(
    s3_client, rekog_resp, s3bucket_source, s3bucket_dest, s3bucket_fail, object_key
):
    """
    Handle the Rekognition response and move the image to the appropriate S3 bucket.

    Args:
        rekog_resp (dict): The response from Rekognition.
        s3bucket_source (str): The source S3 bucket name.
        s3bucket_dest (str): The destination S3 bucket name for successful processing.
        s3bucket_fail (str): The destination S3 bucket name for failed processing.
        object_key (str): The key of the object in the S3 bucket.

    Returns:
        None
    """
    try:
        http_status_code = safeget(rekog_resp, "ResponseMetadata", "HTTPStatusCode")
        if http_status_code == 200:
            # Move to success bucket
            copy_source = {"Bucket": s3bucket_source, "Key": object_key}
            copy_s3_object(
                s3_client,
                source_bucket=s3bucket_source,
                dest_bucket=s3bucket_dest,
                object_key=object_key,
                acl="bucket-owner-full-control",
            )
            LOG.info(
                "Object <%s> copied to success bucket %s", object_key, s3bucket_dest
            )

            # Delete from source bucket
            s3_client.delete_object(Bucket=s3bucket_source, Key=object_key)
            LOG.info(
                "Object <%s> deleted from source bucket %s", object_key, s3bucket_source
            )
        else:
            # Move to failure bucket
            copy_source = {"Bucket": s3bucket_source, "Key": object_key}
            copy_s3_object(
                s3_client,
                source_bucket=s3bucket_source,
                dest_bucket=s3bucket_fail,
                object_key=object_key,
                acl="bucket-owner-full-control",
            )
            LOG.info(
                "Object <%s> copied to failure bucket %s", object_key, s3bucket_fail
            )

            # Delete from source bucket
            s3_client.delete_object(Bucket=s3bucket_source, Key=object_key)
            LOG.info(
                "Object <%s> deleted from source bucket %s", object_key, s3bucket_source
            )

    except ClientError as err:
        LOG.error("Error moving object %s: %s", object_key, err)
        raise
    except Exception as err:
        LOG.error("Unexpected error while handling Rekognition response: %s", err)
        raise


def rekog_image_categorise(rekog_client, image_bytes):

    try:
        rekognition_response = rekog_client.detect_labels(
            Image={"Bytes": image_bytes},
            MaxLabels=10,
            MinConfidence=75,
        )

        # Print labels detected
        labels = [label["Name"] for label in rekognition_response["Labels"]]
        LOG.info("Labels detected: <%s>", labels)

        return rekognition_response

    except Exception as err:
        LOG.error("Error processing image from S3: <%s>", err)
        raise
