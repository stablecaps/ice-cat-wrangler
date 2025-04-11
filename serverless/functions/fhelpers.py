import logging
import os
import sys
from datetime import datetime

from functions.global_context import global_context

from shared_helpers.boto3_helpers import check_bucket_exists, safeget

LOG = logging.getLogger()

dyndb_ttl = os.getenv("dynamoDBTTL")


def validate_s3bucket(s3_client):
    s3bucket_env_list = (
        os.getenv("s3bucketSource"),
        os.getenv("s3bucketDest"),
        os.getenv("s3bucketFail"),
    )
    if None in s3bucket_env_list:
        LOG.critical("env vars are unset in bucket_env_list: <%s>", s3bucket_env_list)
        sys.exit(42)

    for s3bucket in s3bucket_env_list:
        check_bucket_exists(s3_client=s3_client, bucket_name=s3bucket)

    return s3bucket_env_list


def get_s3_key_from_event(event):
    record_list = event.get("Records")
    if record_list is None:
        LOG.critical("record_list not set. Exiting")
        sys.exit(42)
    s3_key = safeget(record_list[0], "s3", "object", "key")
    if s3_key is None:
        LOG.critical("s3_key not set. Exiting")
        sys.exit(42)
    return s3_key


def convert_time_string_to_epoch(time_string, format_string="%a, %d %b %Y %H:%M:%S %Z"):
    """
    Convert a time string in a format like "Fri, 11 Apr 2025 02:20:18 GMT" to epoch time.

    Args:
        time_string (str): The time string to convert.
        format_string (str): The format of the time string. Default is "%a, %d %b %Y %H:%M:%S %Z".

    Returns:
        int: The epoch time.
    """

    # Parse the input string into a datetime object
    dt_object = datetime.strptime(time_string, format_string)

    # Convert the datetime object to epoch time
    epoch_time = int(dt_object.timestamp())

    return epoch_time


def gen_item_dict1_from_s3key(s3_key, s3_bucket):
    """
    Extract key-value pairs from the S3 key format:

    without debug:
        "{file_hash}/{self.client_id}/{batch_id}/{current_date}/{epoch_timestamp}.png"
        0               1              2            3                4
    with debug:
        "{file_hash}/{self.client_id}/{batch_id}/{current_date}/{epoch_timestamp}-debug.png"
        0               1              2            3                4

    Args:
        s3_key (str): The S3 key to parse.

    Returns:
        dict: A dictionary with extracted key-value pairs.
    """
    try:
        parts = s3_key.split("/")
        if len(parts) != 5:
            raise ValueError("S3 key does not match the expected format.")

        #
        file_hash = parts[0]
        client_id = parts[1]
        batch_id = parts[2].replace("batch-", "")
        current_date = parts[3]
        epoch_timestamp_isdebug_check = parts[4].split(".")[0].split("-")

        epoch_timestamp = epoch_timestamp_isdebug_check[0]

        is_debug = False
        if len(epoch_timestamp_isdebug_check) == 2:
            is_debug = True
        global_context["is_debug"] = is_debug
        LOG.debug("is_debug set to: %s", global_context["is_debug"])

        # set shared context (for atexit logging)
        global_context["batch_id"] = batch_id
        global_context["img_fprint"] = file_hash

        return {
            "batch_id": batch_id,
            "img_fprint": file_hash,
            "client_id": client_id,
            "s3img_key": f"{s3_bucket}/{s3_key}",
            "op_status": "pending",
            "current_date": current_date,
            "upload_ts": epoch_timestamp,
            "ttl": dyndb_ttl,
        }
    except Exception as err:
        LOG.error("Failed to extract values from S3 key: %s", err)
        raise ValueError("Failed to extract values from S3 key: %s" % err)


def gen_item_dict2_from_rek_resp(rekog_results):
    """
    Create item_dict2 for updating DynamoDB with Rekognition results.

    Args:
        rekog_results (dict): The response from Rekognition, including rekog_resp, rek_match, and rek_ts.
        s3_key (str): The S3 key of the object.
        s3_bucket (str): The S3 bucket name.

    Returns:
        dict: A dictionary representing item_dict2.
    """
    try:

        # Extract batch_id and img_fprint from global_context
        batch_id = global_context.get("batch_id")
        img_fprint = global_context.get("img_fprint")

        # Extract Rekognition response details
        # TODO: rename rekog_resp to rek_labels in db schema
        rekog_resp = rekog_results.get("rekog_resp")
        rek_match = rekog_results.get("rek_match", None)

        rek_long_time_string = safeget(
            rekog_resp, "ResponseMetadata", "HTTPHeaders", "date"
        )
        rek_ts = convert_time_string_to_epoch(
            time_string=rek_long_time_string, format_string="%a, %d %b %Y %H:%M:%S %Z"
        )
        LOG.info("rek_ts: %s", rek_ts)

        # TODO: fix this - add empty dict for now
        rekog_labels = {
            "TODO": {"placeholder": {"S": "empty dict for now"}}
        }  # rekog_resp.get("Labels")

        rek_status_code = safeget(rekog_resp, "ResponseMetadata", "HTTPStatusCode")
        op_status = "success" if rek_status_code == 200 else "fail"

        # Construct item_dict2
        item_dict2 = {
            "batch_id": batch_id,
            "img_fprint": img_fprint,
            "op_status": op_status,
            # "rek_resp": TODO: rekog_labels, # re-enable this when rekog_labels is fixed
            "rek_iscat": rek_match,
            "rek_ts": rek_ts,
        }

        LOG.info("Created item_dict2: %s", item_dict2)
        return item_dict2

    except Exception as err:
        LOG.error("Failed to create item_dict2: %s", err)
        return {}


# item_dict = {
#     "batch_id": 12345, # s3path[2]
#     "img_fprint": "unique_image_hash", # s3path[0]
#     "client_id": "client123", # s3path[1]
#     "s3img_key": "s3://bucket-name/path/to/image.jpg", # s3bucket + s3path
#     "file_name": "image.jpg", # we can't get this yet
#     "op_status": "success", # pending, success, fail
#     "rek_resp": {"Labels": [{"Name": "Cat", "Confidence": 95}]}, # rekognition response
#     "rek_iscat": True, # rekognition response
#     "logs": {"debug": "Processed successfully"}, # logs (only if debug is supplied)
#     "current_date": "2023-01-01-HH", # s3path[3]
#     "upload_ts": 1672531200, # s3path[4]
#     "rek_ts": 1672531300, # rekognition timestamp
#     "ttl": 1675132800, # dyndb_ttl
# }
