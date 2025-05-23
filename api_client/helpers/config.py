"""
config.py

This module provides utilities for managing environment variables required by the application.
It supports loading environment variables from a `.env` file or fetching them from AWS SSM
Parameter Store. The module ensures that all required secrets are properly set up before
the application runs.

Functions:
    construct_secrets_path(secret_filename):
        Constructs the full path to the secrets file.

    check_env_variables(dotenv_path):
        Checks whether environment variables have been correctly loaded from a dotenv file.

    load_environment_variables(secretsfile):
        Loads environment variables from a dotenv file or AWS SSM Parameter Store.

Dependencies:
    - os
    - sys
    - dotenv.load_dotenv
    - rich.print
    - helpers.boto3_helpers.fetch_values_from_ssm
"""

import os
import sys

from boto3_client_helpers import fetch_values_from_ssm
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from helpers.boto3_clients import ssm_client
from rich import print

secret_vars = [
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "AWS_REGION",
    "FUNC_BULKIMG_ANALYSER_NAME",
    "S3BUCKET_SOURCE",
    "DYNAMODB_TABLE_NAME",
]

SSM_EXCLUDED_KEYS = ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]
SSM_PREFIX = "/stablecaps/dev/cat-wrangler"
ssm_keys = [
    f"{SSM_PREFIX}/{key}" for key in secret_vars if key not in SSM_EXCLUDED_KEYS
]


def construct_secrets_path(secret_filename):
    """
    Constructs the full path to the secrets file.

    Args:
        secret_filename (str): The name of the secrets file.

    Returns:
        str: The full path to the secrets file.

    Raises:
        SystemExit: If the secrets file does not exist.
    """
    root_dir = os.getcwd()
    dotenv_path = f"{root_dir}/config/{secret_filename}"

    if not os.path.isfile(dotenv_path):
        print(f"No secret file found at dotenv_path: {dotenv_path}")
        sys.exit(1)

    return dotenv_path


def check_env_variables():
    """
    Checks whether environment variables have been correctly loaded.

    This function verifies if the specified dotenv file exists and loads
    the environment variables from it. It then checks if all required
    secrets are set in the environment.

    Args:
        dotenv_path (str): The path to the dotenv file.

    Returns:
        bool: True if all required environment variables are set, False otherwise.

    Raises:
        SystemExit: If the dotenv file does not exist.

    Example:
        >>> check_env_variables("/path/to/.env")
    """

    # check to see if env variables are available to app
    passed = True
    for secret in secret_vars:
        if secret not in os.environ:
            print(f"Environment secret not set: {secret}")
            passed = False

    return passed


def load_environment_variables(secretsfile, debug=False):
    """
    Loads environment variables from a dotenv file or AWS SSM Parameter Store.

    If the `secretsfile` argument is "ssm", environment variables are fetched
    from AWS SSM Parameter Store. Otherwise, the specified dotenv file is used.

    Args:
        secretsfile (str): The secrets file name or "ssm" to fetch from SSM.

    Returns:
        None

    Raises:
        SystemExit: If environment variables are not set up properly.
    """
    try:
        if secretsfile == "ssm":
            print("\nFetching environment variables from AWS SSM Parameter Store...")
            env_vars = fetch_values_from_ssm(ssm_client, ssm_keys)

            # Set environment variables
            for key, value in env_vars.items():
                os.environ[key.split("/")[-1]] = value

        else:
            print(
                f"Loading environment variables from the specified secrets file: {secretsfile}"
            )
            dotenv_path = construct_secrets_path(secret_filename=secretsfile)
            load_dotenv(dotenv_path, override=True)

        has_env_vars = check_env_variables()
        if not has_env_vars:
            print("\nEnv variables not set up properly. Exiting...")
            sys.exit(1)

        if debug:
            print("\n Retrieved env vars")
            for key in secret_vars:
                print("**{key}**: ", os.environ[key])

        print("\nEnvironment variables loaded successfully.")
    except ClientError as err:
        print(f"Error fetching SSM parameters: {err}")
        raise SystemExit(1)
