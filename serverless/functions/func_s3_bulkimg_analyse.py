import base64
import json
import logging
import os
import sys

from botocore.exceptions import ClientError

from shared_helpers.boto3_helpers import check_bucket_exists, gen_boto3_client

LOG = logging.getLogger()
LOG.setLevel(logging.INFO)


# TODO: add these functions into shared lib


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


# boto3 clients
s3_client = gen_boto3_client("s3", "eu-west-1")
rekog_client = gen_boto3_client("rekognition", "eu-west-1")


# def upload_image(self, file_path, batch_id):
#     """
#     Processes a single file by uploading it to S3 and generating metadata.

#     Args:
#         file_path (str): The path to the file to upload.
#         batch_id (str): The unique batch ID for the upload session.

#     Returns:
#         dict: Metadata for the uploaded file, or None if the upload failed.
#     """

#     try:
#         print("Uploading {file_path} to s3://{self.s3bucket_source}/{s3_key}")
#         self.s3_client.upload_file(file_path, self.s3bucket_source, s3_key)

#         return
#         # # uploaded file metadata
#         # return {
#         #     "client_id": self.client_id,
#         #     "batch_id": batch_id,
#         #     "s3bucket_source": self.s3bucket_source,
#         #     "s3_key": s3_key,
#         #     "original_file_name": file_name,
#         #     "upload_time": current_date,
#         #     "file_image_hash": file_hash,
#         #     "epoch_timestamp": epoch_timestamp,
#         # }
#     except ClientError as err:
#         print("Error uploading {file_path} to S3: {err}")
#         return None


#############################################################


def get_filebytes_from_s3(bucket_name, object_key):
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


def rekog_image_categorise(image_bytes):

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


def run(event, context):
    """
    Main lambda entrypoint & logic

    0. user -> uploads image to s3bucketSource -> this.lambda
        1. submits image to rekognition (write DynDB record)
        2. gets rekognition response (update DynDB)
        3. success -> moves image to s3bucketDest (update DynDB)
        4. failure -> moves image to s3bucketFail (update DynDB)
    """

    LOG.info("event: <%s> - <%s>", type(event), event)

    ### read env vars
    s3bucket_env_list = (
        os.getenv("s3bucketSource"),
        os.getenv("s3bucketDest"),
        os.getenv("s3bucketFail"),
    )
    s3bucket_source, s3bucket_dest, s3bucket_fail = s3bucket_env_list

    ### Sanity check
    if None in s3bucket_env_list:
        LOG.critical("env vars are unset in bucket_env_list: <%s>", s3bucket_env_list)
        sys.exit(42)

    for s3bucket in s3bucket_env_list:
        check_bucket_exists(bucket_name=s3bucket)

    # 1. get object key from event
    record_list = event.get("Records")
    if record_list is None:
        LOG.critical("record_list not set. Exiting")
        sys.exit(42)
    object_key = safeget(record_list[0], "s3", "object", "key")
    LOG.info("object_key: <%s>", object_key)
    if object_key is None:
        LOG.critical("object_key not set. Exiting")
        sys.exit(42)

    ### Process image file from s3
    file_bytes = get_filebytes_from_s3(
        bucket_name=s3bucket_source,
        object_key=object_key,
    )

    # 1. submit image to rekognition
    rekog_resp = rekog_image_categorise(image_bytes=file_bytes)
    LOG.info("rekog_resp: <%s>", rekog_resp)

    # lambda_response = {"statusCode": 200, "body": json.dumps(s3_resp)}
    # labels = [label["Name"] for label in s3_resp["Labels"]]
    # print("Labels found:")
    # print(labels)

    ### Copy image with sanitised exif data to destination bucket
    # s3_client.put_object(
    #     ACL="bucket-owner-full-control",
    #     Body=my_image.get_file(),
    #     Bucket=s3bucket_dest,
    #     Key=object_key,
    # )
    sys.exit(42)
    try:
        copy_source = {"Bucket": s3bucket_source, "Key": object_key}
        s3_client.copy_object(
            CopySource=copy_source,
            Bucket=s3bucket_dest,
            Key=object_key,
            ACL="bucket-owner-full-control",
        )
        print("Object {object_key} copied from {s3bucket_source} to {s3bucket_dest}")

        s3_client.delete_object(Bucket=s3bucket_source, Key=object_key)
        print("Object {object_key} deleted from {s3bucket_source}")

    except ClientError as e:
        print("Error moving object {object_key}: {e}")
        raise

    LOG.info(
        "SUCCESS Copying s3 object <%s> from <%s> to <%s>",
        object_key,
        s3bucket_source,
        s3bucket_dest,
    )
