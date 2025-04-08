import json
import logging
import os
import sys

import boto3
from botocore.exceptions import ClientError

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


def gen_boto3_session():
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


def gen_boto3_client(service_name, aws_region="eu-west-1"):
    """Creates and returns a Boto3 client for a specified AWS service.

    Args:
        service_name (str): The name of the AWS service (e.g., 's3', 'lambda').

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
        print(f"Verified bucket {bucket_name} exists")
    except ClientError as err:
        error_code = err.response["Error"]["Code"]
        if error_code == "404":
            print(f"S3 bucket {bucket_name} does not exist")
        elif error_code == "403":
            print(f"Access denied to S3 bucket {bucket_name}")
        else:
            print(f"Failed to verify S3 bucket {bucket_name}: {err}")
        sys.exit(1)


#############################################################
def run(event, context):
    body = {"message": "Go Serverless v4.0! Your function executed successfully!"}

    LOG.info("s3bucketSource: %s", os.getenv("s3bucketSource"))
    LOG.info("s3bucketDest: %s", os.getenv("s3bucketDest"))
    LOG.info("s3bucketFail: %s", os.getenv("s3bucketFail"))
    LOG.info("event: <%s> - <%s>", type(event), event)

    return {"statusCode": 200, "body": json.dumps(body)}


# def run(event, context):
#     """
#     Main lambda entrypoint & logic.
#     """

#     LOG.info("event: <%s> - <%s>", type(event), event)

#     ### Setup boto3
#     s3_client = gen_boto3_client("s3", "eu-west-1")

#     ### read env vars
#     s3bucket_env_list = (
#         os.getenv("s3bucket_source"),
#         os.getenv("s3bucket_dest"),
#         os.getenv("s3bucket_fail"),
#     )
#     s3bucket_source, s3bucket_dest, s3bucket_fail = s3bucket_env_list

#     ### Sanity check
#     if None in s3bucket_env_list:
#         LOG.critical("env vars are unset in bucket_env_list: <%s>", s3bucket_env_list)
#         sys.exit(42)

#     for s3bucket in s3bucket_env_list:
#         check_bucket_exists(bucket_name=s3bucket)

#     # TODO: sort out if record_list is None
#     record_list = event.get("Records")
#     object_key = safeget(record_list[0], "s3", "object", "key")
#     LOG.info("object_key: <%s>", object_key)
#     if object_key is None:
#         LOG.critical("object_key not set. Exiting")
#         sys.exit(42)

#     ### Process new uploaded image file
#     response = s3_client.get_object(Bucket=s3bucket_source, Key=object_key)

#     LOG.info("response: %s", response)

#     # my_image = read_img_2memory(get_obj_resp=response)
#     # log_image_data(img=my_image, label="exif data pass0")

#     # ### initial exif data delete
#     # my_image.delete_all()

#     # exif_data_list = log_image_data(img=my_image, label="exif data pass1")

#     # ### Mop any exif data that failed to delete with delete_all
#     # if len(exif_data_list) > 0:
#     #     for exif_tag in exif_data_list:
#     #         my_image.delete(exif_tag)
#     #     log_image_data(img=my_image, label="exif data pass2")

#     ### Copy image with sanitised exif data to destination bucket
#     # s3_client.put_object(
#     #     ACL="bucket-owner-full-control",
#     #     Body=my_image.get_file(),
#     #     Bucket=s3bucket_dest,
#     #     Key=object_key,
#     # )

#     try:
#         copy_source = {"Bucket": s3bucket_source, "Key": object_key}
#         s3_client.copy_object(
#             CopySource=copy_source,
#             Bucket=s3bucket_dest,
#             Key=object_key,
#             ACL="bucket-owner-full-control",
#         )
#         print(f"Object {object_key} copied from {s3bucket_source} to {s3bucket_dest}")

#         s3_client.delete_object(Bucket=s3bucket_source, Key=object_key)
#         print(f"Object {object_key} deleted from {s3bucket_source}")

#     except ClientError as e:
#         print(f"Error moving object {object_key}: {e}")
#         raise

#     LOG.info(
#         "SUCCESS Copying s3 object <%s> from <%s> to <%s>",
#         object_key,
#         s3bucket_source,
#         s3bucket_dest,
#     )
