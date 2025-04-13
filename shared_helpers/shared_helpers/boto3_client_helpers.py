"""
boto3_client_helpers.py

This module provides helper functions for interacting with AWS services using boto3. It includes utilities
for fetching parameters from AWS Systems Manager (SSM) Parameter Store.

Functions:
    - fetch_values_from_ssm: Fetches parameter values from AWS SSM Parameter Store.

Usage:
    Import the required function from this module to interact with AWS services.

    Example:
        from shared_helpers.boto3_client_helpers import fetch_values_from_ssm


        # Fetch values from SSM
        ssm_client = gen_boto3_client("ssm", "eu-west-1")
        ssm_keys = ["key1", "key2"]
        ssm_values = fetch_values_from_ssm(ssm_client, ssm_keys)
        print(ssm_values)


Dependencies:
    - Python 3.12 or higher
    - `boto3_helpers` for generating boto3 clients
    - `rich` for enhanced console output
"""

import sys

from botocore.exceptions import ClientError
from rich import print as rich_print


def fetch_values_from_ssm(ssm_client, ssm_keys):
    """
    Fetches parameter values from AWS SSM Parameter Store.

    Args:
        ssm_client (boto3.client): A boto3 client for AWS SSM.
        ssm_keys (list of str): A list of parameter names to fetch from SSM.

    Returns:
        dict: A dictionary containing the fetched parameter names and their values.

    Raises:
        SystemExit: If any of the specified SSM keys are missing or invalid, or if there is an error
        fetching parameters from SSM.
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
