import logging
import os

from functions.global_context import global_context

LOG = logging.getLogger()

dyndb_ttl = os.getenv("dynamoDBTTL")


def extract_s3_key_values(s3_key, s3_bucket):
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
            "batch_id": int(batch_id),
            "img_fprint": file_hash,
            "client_id": client_id,
            "s3img_key": f"{s3_bucket}/{s3_key}",
            "op_status": "pending",
            "current_date": current_date,
            "upload_ts": int(epoch_timestamp),
            "ttl": dyndb_ttl,
        }
    except Exception as err:
        LOG.error("Failed to extract values from S3 key: %s", err)
        return {}


item_dict = {
    "batch_id": None,  # s3path[2]
    "img_fprint": "unique_image_hash",  # s3path[0]
    "client_id": "client123",  # s3path[1]
    "s3img_key": "bucket-name/path/to/image.jpg",  # s3bucket + s3path
    "file_name": "image.jpg",  # we can't get this yet
    "op_status": "success",  # pending, success, fail
    "rek_resp": {"Labels": [{"Name": "Cat", "Confidence": 95}]},  # rekognition response
    "rek_iscat": True,  # rekognition response
    "logs": {"debug": "Processed successfully"},  # logs (only if debug is supplied)
    "current_date": "2023-01-01-HH",  # s3path[3]
    "upload_ts": 1672531200,  # s3path[4]
    "rek_ts": 1672531300,  # rekognition timestamp
    "ttl": dyndb_ttl,  # dyndb_ttl
}

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
