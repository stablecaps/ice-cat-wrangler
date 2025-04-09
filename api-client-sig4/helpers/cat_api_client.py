#!/usr/bin/env python3.12

"""
AWS Request Signer Client

This module provides functionality to sign AWS API requests using the AWS Signature Version 4 signing process.
It includes a class `AWSRequestSigner` that handles the signing process and a command-line interface for making
signed requests to AWS services.

Classes:
    AWSRequestSigner: Handles AWS Signature Version 4 signing for API requests.

Functions:
    check_env_variables(dotenv_path): Verifies that all required environment variables are loaded from a dotenv file.

Usage:
    Run the script from the command line with the required arguments:

    Example:
        $ python client.py --secretsfile dev_conf_secrets

    The `--secretsfile` argument specifies the name of the secrets file (located in the `config` folder)
    to load environment variables from.

Dependencies:
    - Python 3.12 or higher
    - `requests` library for making HTTP requests
    - `python-dotenv` library for loading environment variables from a `.env` file
    - `rich` library for enhanced console output
"""

import os
import random
import sys

import requests
from helpers.aws_request_signer import AWSRequestSigner
from helpers.boto3_helpers import upload_local_image_blocking
from rich import print


class CatAPIClient:
    """
    Handles AWS Signature Version 4 signing for API requests.

    This class is responsible for signing requests to AWS services using
    the Signature Version 4 signing process.
    """

    def __init__(
        self,
        action,
        img_path=None,
        folder=None,
        result_id=None,
        client_id=None,
        debug=False,
    ):
        """Initializes the AWSRequestSigner with the specified secrets file.

        Args:
            secretsfile (str): The name of the secrets file to load environment variables from.

        Raises:
            SystemExit: If the environment variables are not set up properly.
        """

        self.host = os.getenv("API_HOST")
        self.img_path = img_path
        self.result_id = result_id
        self.debug = debug
        self.func_image_analyser_name = os.getenv("FUNC_IMAGE_ANALYSER_NAME")

        if action == "analyse":
            self.method = "POST"
            self.endpoint = os.getenv("ANALYSE_ENDPOINT")
        elif action == "results":
            self.method = "GET"
            self.endpoint = f"{os.getenv('RESULTS_ENDPOINT')}/{self.result_id}"
        elif action == "bulkanalyse":
            print(f"Bulk analyse not implemented yet")

            sys.exit(0)
            # self.method = "POST"
            # self.endpoint = os.getenv("BULK_ANALYSE_ENDPOINT")
        else:
            raise ValueError("Invalid action. Choose 'analyse' or 'results'.")

        args = AWSRequestSigner(method=self.method, endpoint=self.endpoint)
        self.headers = args.get_auth_headers()

    def make_request(self):
        """Makes a signed request to the AWS API.

        Returns:
            str: The response text from the API.

        Raises:
            requests.exceptions.RequestException: If the request fails.
        """

        # TODO: this may fail aws sig4 signing as signer also uses url - deal with later
        request_url = (
            f"https://{self.host}{self.endpoint}"
            if self.method == "GET"
            else f"https://{self.host}{self.endpoint}"
        )
        print(f"\nMaking request to: {request_url}")

        if self.method == "POST":
            upload_local_image_blocking(
                img_path=self.img_path, function_name=self.func_image_analyser_name
            )
            return
        elif self.method == "GET":
            response = requests.get(request_url, headers=self.headers, timeout=5)
        else:
            raise ValueError("Invalid HTTP method. Choose 'GET' or 'POST'.")

        response.raise_for_status()

        print("\nresponse_text", response.text)
        print("\nresponse.status_code", response.status_code)

        return
