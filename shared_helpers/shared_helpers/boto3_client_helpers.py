import base64
import json
import sys

from boto3_helpers import gen_boto3_client
from botocore.exceptions import ClientError
from rich import print as rich_print


def fetch_values_from_ssm(ssm_client, ssm_keys):
    """
    Fetches environment variables from AWS SSM Parameter Store.

    Args:
        ssm_keys (list): A list of SSM parameter keys to fetch.

    Returns:
        dict: A dictionary containing the fetched environment variables.

    Raises:
        SystemExit: If any of the specified SSM keys are missing or invalid,
        or if there is an error fetching parameters from SSM.
    """

    ssm_vars = {}

    try:
        response = ssm_client.get_parameters(Names=ssm_keys, WithDecryption=True)
        # Store successfully fetched parameters
        for param in response["Parameters"]:
            ssm_vars[param["Name"]] = param["Value"]

        missing_keys = response.get("InvalidParameters", [])
        if missing_keys:
            rich_print(
                f"Warning: The following SSM keys are missing or invalid: {missing_keys}"
            )
            sys.exit(42)

    except ClientError as err:
        rich_print(f"Error fetching parameters from SSM: {err}")
        sys.exit(1)

    return ssm_vars


def upload_local_image_2rekog_blocking(img_path, function_name):
    """
    Uploads a local image to an AWS Lambda function and processes the response.

    Args:
        img_path (str): The file path of the image to upload.
        function_name (str): The name of the AWS Lambda function to invoke.

    Returns:
        None

    Raises:
        SystemExit: If the Lambda function returns a non-200 status code.
    """

    lambda_client = gen_boto3_client("lambda", "eu-west-1")
    rich_print(f"Uploading local image {img_path}.")

    with open(img_path, "rb") as image_file:
        image_bytes = image_file.read()
        data = base64.b64encode(image_bytes).decode("utf8")

        rich_print("Image data size:", len(data))
        rich_print("Image data (truncated):", data[:50], "...")

        lambda_payload = json.dumps({"image": data})

        # Invoke the Lambda function with the event payload
        response = lambda_client.invoke(
            FunctionName=function_name, Payload=(lambda_payload)
        )
        rich_print("\nsubmit status code", response["StatusCode"])

        rekog_decoded = json.loads(response["Payload"].read().decode())

        if rekog_decoded["statusCode"] != 200:
            print("\nrekog_decoded", rekog_decoded)
            sys.exit(42)

        rich_print("\nrekog_decoded", rekog_decoded["body"])
        rich_print("\nrekog_decoded", rekog_decoded["statusCode"])

        return
