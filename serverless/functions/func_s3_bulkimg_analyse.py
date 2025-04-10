import base64
import json
import logging
import os
import sys

import boto3
from botocore.exceptions import ClientError

from shared_helpers.boto3_helpers import gen_boto3_client, gen_boto3_session

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


# def gen_boto3_session():
#     """Creates and returns a Boto3 session using environment variables.

#     Returns:
#         boto3.Session: A Boto3 session object.
#     """
#     return boto3.Session(
#         aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
#         aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
#         aws_session_token=os.getenv("AWS_SESSION_TOKEN"),
#         region_name=os.getenv("AWS_REGION"),
#     )


# def gen_boto3_client(service_name, aws_region="eu-west-1"):
#     """Creates and returns a Boto3 client for a specified AWS service.

#     Args:
#         service_name (str): The name of the AWS service (e.g., 's3', 'lambda').

#     Returns:
#         boto3.Client: A Boto3 client object for the specified service.
#     """
#     session = gen_boto3_session()
#     return session.client(service_name, aws_region)


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

    def upload_image(self, file_path, batch_id):
        """
        Processes a single file by uploading it to S3 and generating metadata.

        Args:
            file_path (str): The path to the file to upload.
            batch_id (str): The unique batch ID for the upload session.

        Returns:
            dict: Metadata for the uploaded file, or None if the upload failed.
        """

        try:
            print(f"Uploading {file_path} to s3://{self.s3bucket_source}/{s3_key}")
            self.s3_client.upload_file(file_path, self.s3bucket_source, s3_key)

            return
            # # uploaded file metadata
            # return {
            #     "client_id": self.client_id,
            #     "batch_id": batch_id,
            #     "s3bucket_source": self.s3bucket_source,
            #     "s3_key": s3_key,
            #     "original_file_name": file_name,
            #     "upload_time": current_date,
            #     "file_image_hash": file_hash,
            #     "epoch_timestamp": epoch_timestamp,
            # }
        except ClientError as err:
            print(f"Error uploading {file_path} to S3: {err}")
            return None


#############################################################


def process_image_from_s3(bucket_name, object_key):
    """
    Retrieve an image from S3, encode it in base64, and submit it to Rekognition.

    Args:
        bucket_name (str): The name of the S3 bucket.
        object_key (str): The key of the object in the S3 bucket.

    Returns:
        dict: The response from Rekognition.
    """
    # Initialize S3 and Rekognition clients
    s3_client = boto3.client("s3")
    rekognition_client = boto3.client("rekognition")

    try:
        # Step 1: Retrieve the image from S3
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        image_content = response["Body"].read()

        # Step 2: Base64 encode the image
        base64_image = base64.b64encode(image_content).decode("utf-8")

        # Step 3: Submit the image to Rekognition
        rekognition_response = rekognition_client.detect_labels(
            Image={"Bytes": image_content},
            MaxLabels=10,  # Adjust the number of labels as needed
            MinConfidence=75,  # Adjust the confidence threshold as needed
        )

        # Print the labels detected
        labels = [label["Name"] for label in rekognition_response["Labels"]]
        print("Labels detected:", labels)

        return rekognition_response

    except Exception as e:
        print(f"Error processing image from S3: {e}")
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

    ### Setup boto3
    s3_client = gen_boto3_client("s3", "eu-west-1")

    ### read env vars
    s3bucket_env_list = (
        os.getenv("s3bucketSource"),
        os.getenv("s3bucketDest"),
        os.getenv("s3bucketFail"),
    )
    s3bucket_source, s3bucket_dest, s3bucket_fail = s3bucket_env_list

    print(f"lambaRoleArn: {os.getenv('lambaRoleArn')}")

    ### Sanity check
    if None in s3bucket_env_list:
        LOG.critical("env vars are unset in bucket_env_list: <%s>", s3bucket_env_list)
        sys.exit(42)

    for s3bucket in s3bucket_env_list:
        check_bucket_exists(bucket_name=s3bucket)

    # TODO: sort out if record_list is None
    record_list = event.get("Records")
    object_key = safeget(record_list[0], "s3", "object", "key")
    LOG.info("object_key: <%s>", object_key)
    if object_key is None:
        LOG.critical("object_key not set. Exiting")
        sys.exit(42)

    ### Process image file from s3
    response = s3_client.get_object(Bucket=s3bucket_source, Key=object_key)

    LOG.info("response: %s", response)

    # 1. submit image to rekognition
    rekog_resp = rekognition.detect_labels(Image={"Bytes": image})
    lambda_response = {"statusCode": 200, "body": json.dumps(response)}
    labels = [label["Name"] for label in response["Labels"]]
    print("Labels found:")
    print(labels)

    # my_image = read_img_2memory(get_obj_resp=response)
    # log_image_data(img=my_image, label="exif data pass0")

    # ### initial exif data delete
    # my_image.delete_all()

    # exif_data_list = log_image_data(img=my_image, label="exif data pass1")

    # ### Mop any exif data that failed to delete with delete_all
    # if len(exif_data_list) > 0:
    #     for exif_tag in exif_data_list:
    #         my_image.delete(exif_tag)
    #     log_image_data(img=my_image, label="exif data pass2")

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
        print(f"Object {object_key} copied from {s3bucket_source} to {s3bucket_dest}")

        s3_client.delete_object(Bucket=s3bucket_source, Key=object_key)
        print(f"Object {object_key} deleted from {s3bucket_source}")

    except ClientError as e:
        print(f"Error moving object {object_key}: {e}")
        raise

    LOG.info(
        "SUCCESS Copying s3 object <%s> from <%s> to <%s>",
        object_key,
        s3bucket_source,
        s3bucket_dest,
    )
