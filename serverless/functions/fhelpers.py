import logging
import os

from functions.global_context import global_context

from shared_helpers.boto3_helpers import (
    safeget,
)

LOG = logging.getLogger()

dyndb_ttl = os.getenv("dynamoDBTTL")


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
            global_context["is_debug"] = True

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
        return {}


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
        rekog_resp = rekog_results.get("rekog_resp", None)
        rek_match = rekog_results.get("rek_match", None)
        rek_ts = int(rekog_results.get("rek_ts", 0))

        rek_status_code = safeget(rekog_resp, "ResponseMetadata", "HTTPStatusCode")
        op_status = "success" if rek_status_code == 200 else "fail"

        # Construct item_dict2
        item_dict2 = {
            "batch_id": batch_id,
            "img_fprint": img_fprint,
            "op_status": op_status,
            "rek_resp": rekog_resp,
            "rek_iscat": rek_match,
            "rek_ts": rek_ts,
        }

        LOG.info("Created item_dict2: %s", item_dict2)
        return item_dict2

    except Exception as err:
        LOG.error("Failed to create item_dict2: %s", err)
        return {}


# item_dict = {
#     "batch_id": None,  # s3path[2]
#     "img_fprint": "unique_image_hash",  # s3path[0]
#     "client_id": "client123",  # s3path[1]
#     "s3img_key": "bucket-name/path/to/image.jpg",  # s3bucket + s3path
#     "file_name": "image.jpg",  # we can't get this yet
#     "op_status": "success",  # pending, success, fail
#     "rek_resp": {"Labels": [{"Name": "Cat", "Confidence": 95}]},  # rekognition response
#     "rek_iscat": True,  # rekognition response
#     "logs": {"debug": "Processed successfully"},  # logs (only if debug is supplied)
#     "current_date": "2023-01-01-HH",  # s3path[3]
#     "upload_ts": 1672531200,  # s3path[4]
#     "rek_ts": 1672531300,  # rekognition timestamp
#     "ttl": dyndb_ttl,  # dyndb_ttl
# }

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
