"""
Module: fhelpers

This module contains helper functions for processing S3 events, generating metadata,
and interacting with AWS Rekognition and DynamoDB. It includes utilities for validating
S3 buckets, extracting metadata from S3 keys, converting data to JSON, and handling
Rekognition responses.

Functions:
    - validate_s3bucket(s3_client): Validates the existence of S3 buckets specified in environment variables.
    - get_s3_key_from_event(event): Extracts the S3 key from an S3 event.
    - convert_time_string_to_epoch(time_string, format_string): Converts a time string to epoch time.
    - convert_to_json(data): Converts a Python object to a JSON string.
    - gen_item_dict1_from_s3key(s3_key, s3_bucket): Generates a dictionary of metadata from an S3 key.
    - gen_item_dict2_from_rek_resp(rekog_results): Generates a dictionary for updating DynamoDB with
        Rekognition results.

Dependencies:
    - AWS Services: S3, DynamoDB, Rekognition
    - Shared Helpers: boto3_helpers (e.g., `check_bucket_exists`, `safeget`)
    - Global Context: `global_context` for shared state management

Environment Variables:
    - dynamoDBTTL: The TTL (Time-to-Live) value for DynamoDB records.
    - s3bucketSource: The name of the source S3 bucket.
    - s3bucketDest: The name of the destination S3 bucket.
    - s3bucketFail: The name of the failure S3 bucket.

Usage:
    This module is used in AWS Lambda functions to process S3 events, extract metadata,
    and interact with AWS services. It provides utility functions for common tasks such
    as validating S3 buckets, parsing S3 keys, and handling Rekognition responses.

Example:
    # Validate S3 buckets
    s3bucket_source, s3bucket_dest, s3bucket_fail = validate_s3bucket(s3_client)

    # Extract S3 key from event
    s3_key = get_s3_key_from_event(event)

    # Generate metadata from S3 key
    item_dict1 = gen_item_dict1_from_s3key(s3_key, s3bucket_source)

    # Process Rekognition response
    item_dict2 = gen_item_dict2_from_rek_resp(rekog_results)

Error Handling:
    - Logs critical errors and exits the program if required environment variables are unset
      or S3 buckets do not exist.
    - Handles serialization errors when converting data to JSON.
    - Logs and raises exceptions for invalid S3 keys or Rekognition responses.

"""

import sys

sys.path.insert(0, "modules")
import json
import logging
import os
from datetime import datetime, timezone

import pytz
from functions.global_context import global_context

from shared_helpers.boto3_helpers import check_bucket_exists, safeget

LOG = logging.getLogger()

dyndb_ttl = os.getenv("dynamoDBTTL")


def validate_s3bucket(s3_client):
    """
    Validate the existence of S3 buckets specified in environment variables.

    This function checks if the source, destination, and failure S3 buckets exist.
    If any of the buckets are not set in the environment variables or do not exist,
    the function logs a critical error and exits the program.

    Args:
        s3_client (boto3.client): The S3 client used to check bucket existence.

    Returns:
        tuple: A tuple containing the names of the source, destination, and failure S3 buckets.

    Raises:
        SystemExit: If any of the required environment variables are unset or the buckets do not exist.
    """
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
    """
    Extract the S3 key from an S3 event.

    This function retrieves the S3 object key from the event data passed to the Lambda function.
    If the event does not contain the required information, the function logs a critical error
    and exits the program.

    Args:
        event (dict): The event data passed to the Lambda function.

    Returns:
        str: The S3 object key.

    Raises:
        SystemExit: If the event does not contain the required S3 key information.
    """
    record_list = event.get("Records")
    if record_list is None:
        LOG.critical("record_list not set. Exiting")
        sys.exit(42)
    s3_key = safeget(record_list[0], "s3", "object", "key")
    if s3_key is None:
        LOG.critical("s3_key not set. Exiting")
        sys.exit(42)
    return s3_key


# def convert_time_string_to_epoch(time_string, format_string="%a, %d %b %Y %H:%M:%S %Z"):
#     """
#     Convert a time string to epoch time.

#     This function parses a time string in a specified format and converts it to epoch time.

#     Args:
#         time_string (str): The time string to convert.
#         format_string (str): The format of the time string. Default is "%a, %d %b %Y %H:%M:%S %Z".

#     Returns:
#         int: The epoch time.

#     Raises:
#         ValueError: If the time string does not match the specified format.
#     """
#     dt_object = datetime.strptime(time_string, format_string)

#     epoch_time = int(dt_object.timestamp())


#     return epoch_time
def convert_time_string_to_epoch(time_string, format_string="%a, %d %b %Y %H:%M:%S %Z"):
    """
    Convert a time string to epoch time.

    Args:
        time_string (str): The time string to convert.
        format_string (str): The format of the time string. Default is "%a, %d %b %Y %H:%M:%S %Z".

    Returns:
        int: The epoch time.

    Raises:
        ValueError: If the time string does not match the specified format.
    """
    try:
        # Parse the time string into a naive datetime object
        dt_object = datetime.strptime(time_string, format_string)

        # Handle timezone-aware strings
        if "GMT" in time_string:
            tz = pytz.timezone("GMT")
            dt_object = tz.localize(dt_object)
        # TODO: EST timezone not handled properly - investigate
        elif "EST" in time_string:
            tz = pytz.timezone("US/Eastern")
            dt_object = tz.localize(dt_object)
        else:
            # Assume naive datetime objects are in UTC
            dt_object = dt_object.replace(tzinfo=timezone.utc)

        # Convert to epoch time
        return int(dt_object.timestamp())
    except Exception as err:
        raise ValueError(f"Error converting time string to epoch: {err}")


def convert_to_json(data):
    """
    Convert any supported Python data type to a JSON string.

    Args:
        data: The data to convert. Can be a primitive type, complex type, or nested structure.

    Returns:
        str: The JSON string representation of the data.
    """
    try:
        json_string = json.dumps(data, indent=4)
        return json_string
    except TypeError as err:
        print(f"Error: Data type not serializable to JSON. {err}")
        return None


def gen_item_dict1_from_s3key(s3_key, s3_bucket):
    """
    Generate a dictionary of metadata from an S3 key.

    This function parses an S3 key to extract metadata such as file hash, client ID,
    batch ID, current date, and upload timestamp. It also updates the global context
    with the extracted batch ID and file hash.

    without debug:
        "{file_hash}/{self.client_id}/{batch_id}/{current_date}/{epoch_timestamp}.png"
        0               1              2            3                4
    with debug:
        "{file_hash}/{self.client_id}/{batch_id}/{current_date}/{epoch_timestamp}-debug.png"
        0               1              2            3                4

    Args:

    Args:
        s3_key (str): The S3 key to parse.
        s3_bucket (str): The name of the S3 bucket.

    Returns:
        dict: A dictionary containing metadata extracted from the S3 key.

    Raises:
        ValueError: If the S3 key does not match the expected format.
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
        LOG.info(
            "in gen_item_dict1_from_s3key() is_debug set to: %s with type <%s>",
            global_context["is_debug"],
            type(global_context["is_debug"]),
        )

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
        raise ValueError(f"Failed to extract values from S3 key: <{err}>") from err


def gen_item_dict2_from_rek_resp(rekog_results):
    """
    Generate a dictionary for updating DynamoDB with Rekognition results.

    This function processes the Rekognition response to extract relevant metadata,
    such as operation status, Rekognition labels, and timestamps. It also retrieves
    the batch ID and file hash from the global context.

    Args:
        rekog_results (dict): The response from Rekognition, including rekog_resp, rek_match, and rek_ts.

    Returns:
        dict: A dictionary containing metadata for updating DynamoDB.

    Raises:
        Exception: If there is an error while processing the Rekognition response.
    """
    try:

        # Extract batch_id and img_fprint from global_context
        batch_id = global_context.get("batch_id")
        img_fprint = global_context.get("img_fprint")

        # Extract Rekognition response details
        # TODO: rename rekog_resp to rek_labels in db schema
        rekog_resp = rekog_results.get("rekog_resp")
        if not rekog_resp:
            LOG.error("Missing rekog_resp in Rekognition results")
            return {}

        rek_match = rekog_results.get("rek_match", None)

        rek_long_time_string = safeget(
            rekog_resp, "ResponseMetadata", "HTTPHeaders", "date"
        )
        rek_ts = convert_time_string_to_epoch(
            time_string=rek_long_time_string, format_string="%a, %d %b %Y %H:%M:%S %Z"
        )
        LOG.info("rek_ts: %s", rek_ts)

        # TODO: fix this - add empty dict for now For Map type in dynamodb
        # rekog_labels = {
        #     "TODO": {"placeholder": {"S": "empty dict for now"}}
        # }  # rekog_resp.get("Labels")

        rek_status_code = safeget(rekog_resp, "ResponseMetadata", "HTTPStatusCode")
        op_status = "success" if rek_status_code == 200 else "fail"

        # Construct item_dict2
        item_dict2 = {
            "batch_id": batch_id,
            "img_fprint": img_fprint,
            "op_status": op_status,
            "rek_resp": convert_to_json(
                data=rekog_resp
            ),  # TODO: rekog_labels, # re-enable this when rekog_labels is fixed
            "rek_iscat": rek_match,
            "rek_ts": rek_ts,
        }

        LOG.info("Created item_dict2: %s", item_dict2)
        return item_dict2

    except Exception as err:
        LOG.error("Failed to create item_dict2: %s", err)
        return {}
