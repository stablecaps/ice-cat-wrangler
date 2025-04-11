import atexit
import base64
import json
import logging
import os
import sys

from botocore.exceptions import ClientError
from functions.data import required_dyndb_keys
from functions.fhelpers import gen_item_dict1_from_s3key, gen_item_dict2_from_rek_resp
from functions.global_context import global_context

from shared_helpers.boto3_helpers import (
    DynamoDBHelper,
    check_bucket_exists,
    gen_boto3_client,
    get_filebytes_from_s3,
    move_s3_object_based_on_rekog_response,
    rekog_image_categorise,
    safeget,
)


# Adds logs to the log_collector
class LogCollectorHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.logs = []

    def emit(self, record):
        log_entry = self.format(record)
        self.logs.append(log_entry)


LOG = logging.getLogger()
LOG.setLevel(logging.INFO)
log_collector = LogCollectorHandler()
LOG.addHandler(log_collector)


# create boto3 session clients
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


def write_logs_to_dynamodb():

    # Retrieve batch_id and img_fprint from global context
    # TODOD op_status may not be fail
    item_dict = {
        "batch_id": global_context["batch_id"],
        "img_fprint": global_context["img_fprint"],
        "op_status": "fail",
        "logs": log_collector.logs,
    }
    LOG.info("Writing logs to DynamoDB atexit...")
    dynamodb_helper.write_item(
        item_dict=item_dict,
    )


# use atexit to call write_logs_to_dynamodb function if program exits if is_debug = True
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


    events need to be written into the dynamodb databse at various points where an error could occure
        1. when the s3 event is triggered
        2. when the rekognition response is received
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

    s3_key = safeget(record_list[0], "s3", "object", "key")
    LOG.info("s3_key: <%s>", s3_key)
    if s3_key is None:
        LOG.critical("s3_key not set. Exiting")
        sys.exit(42)

    # db1. write item to dynamodb after getting the object key
    item_dict1 = gen_item_dict1_from_s3key(s3_key=s3_key, s3_bucket=s3bucket_source)

    dynamodb_helper.write_item(
        item_dict=item_dict1,
    )

    ### 2.  Process image file from s3
    file_bytes = get_filebytes_from_s3(
        s3_client=s3_client,
        bucket_name=s3bucket_source,
        s3_key=s3_key,
    )

    # 3. submit image to rekognition
    rekog_results = rekog_image_categorise(
        rekog_client=rekog_client, image_bytes=file_bytes, label_pattern="cat"
    )

    rekog_resp = rekog_results.get("rekog_resp")
    LOG.info("rekog_resp: <%s>", rekog_resp)

    # rek_ts = int(rekog_results.get("rek_ts"))
    # rek_match = rekog_results.get("rek_match")
    # rek_status_code = safeget(rekog_resp, "ResponseMetadata", "HTTPStatusCode")

    # db2. update item in dynamodb with rekognition response
    item_dict2 = gen_item_dict2_from_rek_resp(rekog_results=rekog_results)

    dynamodb_helper.update_item(
        item_dict=item_dict2,
    )

    # 4. handle rekognition response by moving image to appropriate s3 bucket (success/fail)
    move_success = move_s3_object_based_on_rekog_response(
        s3_client=s3_client,
        op_status=item_dict2.get("op_status"),
        s3bucket_source=s3bucket_source,
        s3bucket_dest=s3bucket_dest,
        s3bucket_fail=s3bucket_fail,
        s3_key=s3_key,
    )
    # db3. update item in dynamodb with renamed s3+key
    s3img_key = (f"{s3bucket_fail}/{s3_key}",)
    op_status = "fail"
    if move_success:
        s3img_key = f"{s3bucket_dest}/{s3_key}"
        op_status = "success"

    item_dict3 = {
        "batch_id": global_context.get("batch_id"),
        "img_fprint": global_context.get("img_fprint"),
        "s3img_key": f"{s3bucket_dest}/{s3_key}",
    }

    if not move_success:
        item_dict3["op_status"] = "fail"

    dynamodb_helper.update_item(
        item_dict=item_dict3,
    )
