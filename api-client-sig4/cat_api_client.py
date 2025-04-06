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

import argparse
import datetime
import hashlib
import hmac
import os
import sys

import requests
from helpers.aws_request_signer import AWSRequestSigner
from helpers.config import check_env_variables, construct_secrets_path
from rich import print


class CatAPIClient:
    """
    Handles AWS Signature Version 4 signing for API requests.

    This class is responsible for signing requests to AWS services using
    the Signature Version 4 signing process.
    """

    def __init__(self, secretsfile, action, debug=False):
        """Initializes the AWSRequestSigner with the specified secrets file.

        Args:
            secretsfile (str): The name of the secrets file to load environment variables from.

        Raises:
            SystemExit: If the environment variables are not set up properly.
        """

        print("Loading environment variables from the specified secrets file")
        dotenv_path = construct_secrets_path(secret_filename=secretsfile)
        has_env_vars = check_env_variables(dotenv_path=dotenv_path)
        if not has_env_vars:
            print("\nEnv variables not set up properly. Exiting...")
            sys.exit(1)

        print("All environment secrets set correctly")

        self.host = os.getenv("API_HOST")
        self.debug = debug

        if action == "analyse":
            self.method = "POST"
            self.endpoint = os.getenv("ANALYSE_ENDPOINT")
        elif action == "results":
            self.method = "GET"
            self.endpoint = os.getenv("RESULTS_ENDPOINT")
        else:
            raise ValueError("Invalid action. Choose 'analyse' or 'results'.")

        ars = AWSRequestSigner(method=self.method, endpoint=self.endpoint)
        self.headers = ars.get_auth_headers()

    def make_request(self):
        """Makes a signed request to the AWS API.

        Returns:
            str: The response text from the API.

        Raises:
            requests.exceptions.RequestException: If the request fails.
        """

        request_url = f"https://{self.host}{self.endpoint}"
        print(f"\nMaking request to: {request_url}")

        if self.method == "POST":
            # Example payload for POST request
            payload = {"key": "value"}
            response = requests.post(
                request_url, headers=self.headers, json=payload, timeout=5
            )
        elif self.method == "GET":
            response = requests.get(request_url, headers=self.headers, timeout=5)
        else:
            raise ValueError("Invalid HTTP method. Choose 'GET' or 'POST'.")

        response.raise_for_status()

        print("\nresponse_text", response.text)
        print("\nresponse.status_code", response.status_code)

        return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Cat API Client",
        usage=".e.g: ./cat_api_client.py --secretsfile dev_conf_secrets --action [analyse, results]",
    )
    parser.add_argument(
        "--secretsfile",
        "-s",
        type=str,
        required=True,
        help="Secrets file name to load environment variables from. Should be in config folder. e.g. dev_conf_secrets",
    )

    parser.add_argument(
        "--debug",
        "-d",
        action="store_true",
        required=False,
        default=False,
        help="Debug mode. Set to True to enable debug output.",
    )

    parser.add_argument(
        "--action",
        "-a",
        type=str,
        required=True,
        choices=["analyse", "results"],
        help="Action to perform. Choose from: 'analyse' or 'results'.",
    )
    args = parser.parse_args()

    client = CatAPIClient(
        secretsfile=args.secretsfile, action=args.action, debug=args.debug
    )
    client.make_request()

    print("\nFinished request")
