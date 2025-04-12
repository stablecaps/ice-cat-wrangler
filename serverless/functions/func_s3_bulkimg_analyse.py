import atexit
import logging
import os

from dynamo_db_helper.py import DynamoDBHelper
from functions.data import required_dyndb_keys
from functions.fhelpers import (
    convert_to_json,
    gen_item_dict1_from_s3key,
    gen_item_dict2_from_rek_resp,
    get_s3_key_from_event,
    validate_s3bucket,
)
from functions.global_context import global_context

from shared_helpers.boto3_helpers import (  # check_bucket_exists,
    DynamoDBHelper,
    gen_boto3_client,
    get_filebytes_from_s3,
    move_s3_object_based_on_rekog_response,
    rekog_image_categorise,
    safeget,
)


######################################################################
# Adds logs to the log_collector
class LogCollectorHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.logs = []

    def emit(self, record):
        log_entry = self.format(record)
        self.logs.append(log_entry)


LOG = logging.getLogger()
LOG.setLevel(logging.DEBUG)
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
def write_logs_to_dynamodb():

    # Retrieve batch_id and img_fprint from global context
    # will notwork if global_context pk & sk is None
    batch_id = global_context.get("batch_id")
    img_fprint = global_context.get("img_fprint")
    if batch_id is None or img_fprint is None:
        LOG.error("batch_id not set. Exiting")
        return

    LOG.debug("Collected logs: %s", log_collector.logs)

    item_dict = {
        "batch_id": batch_id,
        "img_fprint": img_fprint,
        "logs": convert_to_json(data=log_collector.logs),
    }

    LOG.info("Writing logs to DynamoDB atexit: %s", item_dict)
    dynamodb_helper.write_item(
        item_dict=item_dict,
    )


# use atexit to call write_logs_to_dynamodb function if program exits & writes logs if is_debug = True
def register_atexit_if_debug():
    is_debug = global_context.get("is_debug", False)
    if is_debug:
        LOG.info("Debug mode is enabled. Registering atexit function.")
        atexit.register(write_logs_to_dynamodb)


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

    # Note: failures in step 0 & 1 will show op_status as pending as we cannot write to db without pk & sk
    # Step 0: Validate S3 buckets
    s3bucket_source, s3bucket_dest, s3bucket_fail = validate_s3bucket(
        s3_client=s3_client
    )

    # Step 1: Get S3 key from event
    s3_key = get_s3_key_from_event(event=event)

    try:
        # Step 2: Write initial item to DynamoDB
        item_dict1 = gen_item_dict1_from_s3key(s3_key=s3_key, s3_bucket=s3bucket_source)

        item_dict_if_fail = {
            "batch_id": item_dict1.get("batch_id"),
            "img_fprint": item_dict1.get("img_fprint"),
            "op_status": "fail",
        }

        dynamodb_helper.write_item(item_dict=item_dict1)

        # Register atexit after determining debug mode
        register_atexit_if_debug()

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

        LOG.info("Finished processing image from S3.")

    except Exception as err:
        # Catch any failure and update DynamoDB with failure status
        LOG.critical("Processing failed: %s", err)
        if item_dict_if_fail:
            item_dict_if_fail["s3img_key"] = f"{s3bucket_source}/{s3_key}"
        dynamodb_helper.update_item(item_dict=item_dict_if_fail)
        # raise  - TODO: Re-raise the exception to allow lambda to handle retries. need additional ifra like SQS DLQ
