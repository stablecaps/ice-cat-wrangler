import base64
import json
import logging
import sys

import boto3
from botocore.exceptions import ClientError

# def image_analyse(event, context):
#     body = {
#         "message": "Go Serverless v4.0! Your function executed successfully!"
#     }

#     return {"statusCode": 200, "body": json.dumps(body)}


# Instantiate logger
logger = logging.getLogger(__name__)
logger.setLevel("INFO")

# connect to the Rekognition client
rekognition = boto3.client("rekognition")


def image_analyse(event, context):

    logger.info("Event: %s", event)
    logger.info("Context: %s", context)
    logger.info("Function ARN: %s", context.invoked_function_arn)
    logger.info("Function name: %s", context.function_name)
    logger.info("Function version: %s", context.function_version)

    try:
        image = None
        if "S3Bucket" in event and "S3Object" in event:
            s3 = boto3.resource("s3")
            s3_object = s3.Object(event["S3Bucket"], event["S3Object"])
            image = s3_object.get()["Body"].read()

        elif "image" in event:
            image_bytes = event["image"].encode("utf-8")
            img_b64decoded = base64.b64decode(image_bytes)
            image = img_b64decoded

        elif image is None:
            raise ValueError("Missing image, check image or bucket path.")

        else:
            raise ValueError(
                "Only base 64 encoded image bytes or S3Object are supported."
            )

        response = rekognition.detect_labels(Image={"Bytes": image})
        lambda_response = {"statusCode": 200, "body": json.dumps(response)}
        labels = [label["Name"] for label in response["Labels"]]
        print("Labels found:")
        print(labels)

    except ClientError as client_err:

        error_message = (
            "Couldn't analyze image: " + client_err.response["Error"]["Message"]
        )

        lambda_response = {
            "statusCode": 400,
            "body": {
                "Error": client_err.response["Error"]["Code"],
                "ErrorMessage": error_message,
            },
        }
        logger.error(
            "Error function %s: %s", context.invoked_function_arn, error_message
        )

    except ValueError as val_error:

        lambda_response = {
            "statusCode": 400,
            "body": {"Error": "ValueError", "ErrorMessage": format(val_error)},
        }
        logger.error(
            "Error function %s: %s", context.invoked_function_arn, format(val_error)
        )

    return lambda_response


# https://docs.aws.amazon.com/rekognition/latest/dg/lambda-s3-tutorial-python.html
