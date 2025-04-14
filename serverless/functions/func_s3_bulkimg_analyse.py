"""
Module: func_s3_bulkimg_analyse

This module contains the main logic for processing images uploaded to an S3 bucket.
It integrates with AWS Rekognition for image analysis, DynamoDB for storing metadata,
and S3 for managing image files. The module is designed to be used as an AWS Lambda
function triggered by S3 events.

Functions:
    - run(event, context): Main entry point for the Lambda function. Processes an image
      uploaded to an S3 bucket by analyzing it with Rekognition, updating DynamoDB,
      and moving the image to the appropriate S3 bucket based on the analysis result.

    - write_debug_logs_to_dynamodb(): Writes debug logs to DynamoDB if the global
      context indicates debug mode is enabled.

Classes:
    - LogCollectorHandler: Custom logging handler that collects log messages into a
      list for later use, such as writing to DynamoDB.

Dependencies:
    - AWS Services: S3, Rekognition, DynamoDB
    - Shared Helpers: boto3_helpers, dynamo_db_helper
    - Local Helpers: fhelpers, global_context

Environment Variables:
    - AWS_REGION: The AWS region where the Lambda function is deployed.
    - dynamoDBTableName: The name of the DynamoDB table used for storing metadata.
    - dynamoDBTTL: The TTL (Time-to-Live) value for DynamoDB records.

Usage:
    This module is triggered by an S3 event when an image is uploaded to the source
    bucket. It performs the following steps:
        1. Validates the source, destination, and failure S3 buckets.
        2. Writes an initial record to DynamoDB.
        3. Retrieves the image bytes from the source S3 bucket.
        4. Submits the image to AWS Rekognition for analysis.
        5. Updates DynamoDB with the Rekognition response.
        6. Moves the image to the destination or failure S3 bucket based on the analysis.
        7. Updates DynamoDB with the final S3 key and operation status.

Error Handling:
    - Catches exceptions during processing and updates DynamoDB with a failure status.
    - Logs critical errors and writes debug logs to DynamoDB if debug mode is enabled.
    - Includes TODOs for implementing retries and integrating with SQS Dead Letter Queues (DLQs).

TODOs:
    - Implement retries for failed S3 object moves.
    - Re-raise exceptions to allow Lambda retries, requiring additional infrastructure
      like SQS DLQs.

"""

import logging
import os

from functions.data import required_dyndb_keys
from functions.fhelpers import (
    convert_to_json,
    gen_item_dict1_from_s3key,
    gen_item_dict2_from_rek_resp,
    get_s3_key_from_event,
    validate_s3bucket,
)
from functions.global_context import global_context

from shared_helpers.boto3_helpers import (
    gen_boto3_client,
    get_filebytes_from_s3,
    move_s3_object_based_on_rekog_response,
    rekog_image_categorise,
)
from shared_helpers.dynamo_db_helper import DynamoDBHelper


######################################################################
# Adds logs to the log_collector
class LogCollectorHandler(logging.Handler):
    """
    A custom logging handler that collects log messages into a list.

    This handler is used to store log messages in memory, allowing them to be
    accessed later for purposes such as writing to DynamoDB or debugging.

    Attributes:
        logs (list): A list that stores formatted log messages.
    """

    def __init__(self):
        """
        Initializes the LogCollectorHandler instance.

        Sets up an empty list to store log messages.
        """
        super().__init__()
        self.logs = []

    def emit(self, record):
        """
        Processes a log record and appends the formatted log message to the logs list.

        Args:
            record (logging.LogRecord): The log record to be processed.
        """
        log_entry = self.format(record)
        self.logs.append(log_entry)


LOG = logging.getLogger()
LOG.setLevel(logging.INFO)
log_collector = LogCollectorHandler()
LOG.addHandler(log_collector)


######################################################################
# create boto3 session clients & get vars
aws_region = os.getenv("AWS_REGION")
s3_client = gen_boto3_client("s3", aws_region)
rekog_client = gen_boto3_client("rekognition", aws_region)
dyndb_client = gen_boto3_client("dynamodb", aws_region)
#
dyndb_table_name = os.getenv("dynamoDBTableName")
dyndb_ttl = os.getenv("dynamoDBTTL")

LOG.info("aws_region: <%s>", aws_region)
LOG.info("dyndb_table_name: <%s>", dyndb_table_name)
LOG.info("dyndb_ttl: <%s>", dyndb_ttl)

# Initialize the helper
dynamodb_helper = DynamoDBHelper(
    dyndb_client=dyndb_client,
    table_name=dyndb_table_name,
    required_keys=required_dyndb_keys,
)


######################################################################
def write_debug_logs_to_dynamodb():
    """
    Writes debug logs to DynamoDB if debug mode is enabled.

    This function retrieves the `batch_id` and `img_fprint` from the global context
    and writes the collected logs to DynamoDB. If the required keys are not present
    in the global context, the function logs an error and exits.

    Raises:
        Exception: If there is an error while writing logs to DynamoDB.

    Logs:
        - Logs the collected debug logs and the status of the DynamoDB update operation.
    """
    LOG.info("in write_debug_logs_to_dynamodb()")

    if global_context.get("is_debug", False):
        try:
            # Retrieve batch_id and img_fprint from global context
            # will notwork if global_context pk & sk is None
            batch_id = global_context.get("batch_id")
            img_fprint = global_context.get("img_fprint")
            if batch_id is None or img_fprint is None:
                LOG.error("batch_id not set. Exiting")
                return

            # LOG.info("Collected logs: %s", log_collector.logs)

            item_dict = {
                "batch_id": batch_id,
                "img_fprint": img_fprint,
                "logs": convert_to_json(data=log_collector.logs),
            }

            LOG.info("Writing logs to DynamoDB atexit: %s", item_dict)

            dynamodb_helper.update_item(
                item_dict=item_dict,
            )

        except Exception as err:
            LOG.error("Failed to write logs to DynamoDB: %s", err)


#############################################################
def run(event, context):
    """
    Main entry point for the Lambda function.

    This function processes an image uploaded to an S3 bucket by performing the following steps:
        1. Validates the source, destination, and failure S3 buckets.
        2. Retrieves the S3 key from the event.
        3. Writes an initial record to DynamoDB.
        4. Retrieves the image bytes from the source S3 bucket.
        5. Submits the image to AWS Rekognition for analysis.
        6. Updates DynamoDB with the Rekognition response.
        7. Moves the image to the destination or failure S3 bucket based on the analysis.
        8. Updates DynamoDB with the final S3 key and operation status.

    Args:
        event (dict): The event data passed to the Lambda function, typically containing
            information about the S3 object that triggered the function.
        context (object): The runtime context of the Lambda function, including metadata
            about the invocation, function, and execution environment.

    Raises:
        Exception: If any step in the processing pipeline fails, the exception is logged,
            and the function attempts to update DynamoDB with a failure status.

    Logs:
        - Logs the event data, Rekognition response, and DynamoDB updates.
        - Logs critical errors if processing fails.

    Notes:
        - If debug mode is enabled, debug logs are written to DynamoDB.
        - TODO: Implement retries for failed S3 object moves and integrate with SQS DLQs.
    """

    LOG.info("event: <%s> - <%s>", type(context), context)
    LOG.info("event: <%s> - <%s>", type(event), event)

    # Note: failures in step 0 & 1 will show op_status as pending as we cannot write to db without pk & sk
    # Step 0: Validate S3 buckets
    s3bucket_source, s3bucket_dest, s3bucket_fail = validate_s3bucket(
        s3_client=s3_client
    )

    # Step 1: Get S3 key from event
    s3_key = get_s3_key_from_event(event=event)

    item_dict_if_fail = {
        "batch_id": None,
        "img_fprint": None,
        "op_status": "fail",
        "s3img_key": None,
    }

    try:
        # Step 2: Write initial item to DynamoDB
        item_dict1 = gen_item_dict1_from_s3key(s3_key=s3_key, s3_bucket=s3bucket_source)

        item_dict_if_fail.update(
            {
                "batch_id": item_dict1.get("batch_id"),
                "img_fprint": item_dict1.get("img_fprint"),
            }
        )

        dynamodb_helper.write_item(item_dict=item_dict1)

        # Step 3: Retrieve file bytes from S3
        file_bytes = get_filebytes_from_s3(
            s3_client=s3_client,
            bucket_name=s3bucket_source,
            s3_key=s3_key,
        )

        # Step 4: Submit image to Rekognition
        rekog_results = rekog_image_categorise(
            rekog_client=rekog_client, image_bytes=file_bytes, label_pattern="cat"
        )

        rekog_resp = rekog_results.get("rekog_resp")
        LOG.info("rekog_resp: <%s>", rekog_resp)

        # Step 5: Update DynamoDB with Rekognition response
        item_dict2 = gen_item_dict2_from_rek_resp(rekog_results=rekog_results)
        LOG.info("item_dict2: <%s>", item_dict2)
        dynamodb_helper.update_item(item_dict=item_dict2)

        # Step 6: Handle Rekognition response by moving image to appropriate S3 bucket
        move_success = move_s3_object_based_on_rekog_response(
            s3_client=s3_client,
            op_status=item_dict2.get("op_status"),
            s3bucket_source=s3bucket_source,
            s3bucket_dest=s3bucket_dest,
            s3bucket_fail=s3bucket_fail,
            s3_key=s3_key,
        )

        # Step 7: Update DynamoDB with final S3 key and operation status
        # TODO: try move image to fail bucket if move fails
        s3img_key = (
            f"{s3bucket_dest}/{s3_key}" if move_success else f"{s3bucket_fail}/{s3_key}"
        )
        op_status = "success" if move_success else "fail"

        item_dict3 = {
            "batch_id": global_context.get("batch_id"),
            "img_fprint": global_context.get("img_fprint"),
            "s3img_key": s3img_key,
            "op_status": op_status,
        }
        LOG.info("item_dict3: <%s>", item_dict3)
        dynamodb_helper.update_item(item_dict=item_dict3)

    except Exception as err:
        # Catch any failure and update DynamoDB with failure status
        LOG.critical("Processing failed: %s", err)

        if item_dict_if_fail.get("batch_id"):
            item_dict_if_fail["s3img_key"] = f"{s3bucket_source}/{s3_key}"
            dynamodb_helper.update_item(item_dict=item_dict_if_fail)

        write_debug_logs_to_dynamodb()

        # TODO: Re-raise the exception to allow lambda to handle retries. need additional infra like SQS DLQ
        # raise
    finally:
        write_debug_logs_to_dynamodb()

        LOG.info("Finished processing image from S3.")
