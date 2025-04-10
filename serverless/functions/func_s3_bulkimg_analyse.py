import base64
import json
import logging
import os
import sys

from botocore.exceptions import ClientError

from shared_helpers.boto3_helpers import (
    check_bucket_exists,
    gen_boto3_client,
    get_filebytes_from_s3,
    move_s3_object_based_on_rekog_response,
    rekog_image_categorise,
    safeget,
)

LOG = logging.getLogger()
LOG.setLevel(logging.INFO)


# for path in sys.path:
#     LOG.info("sys paths: %s", path)

# LOG.info("sys shared_helpers: <%s>", "/opt/python/lib/python3.12/site-packages/shared_helpers")


# create boto3 session clients
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
        check_bucket_exists(s3_client=s3_client, bucket_name=s3bucket)

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

    ### 2.  Process image file from s3
    file_bytes = get_filebytes_from_s3(
        s3_client=s3_client,
        bucket_name=s3bucket_source,
        object_key=object_key,
    )

    # 3. submit image to rekognition
    rekog_resp = rekog_image_categorise(
        rekog_client=rekog_client, image_bytes=file_bytes
    )
    LOG.info("rekog_resp: <%s>", rekog_resp)

    # 4. handle rekognition response by moving image to appropriate s3 bucket (success/fail)
    move_s3_object_based_on_rekog_response(
        s3_client=s3_client,
        rekog_resp=rekog_resp,
        s3bucket_source=s3bucket_source,
        s3bucket_dest=s3bucket_dest,
        s3bucket_fail=s3bucket_fail,
        object_key=object_key,
    )

    # lambda_response = {"statusCode": 200, "body": json.dumps(s3_resp)}
    # labels = [label["Name"] for label in s3_resp["Labels"]]
    # print("Labels found:")
    # print(labels)
