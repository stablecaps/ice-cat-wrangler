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
from helpers.boto3_helpers import upload_local_image_blocking
from helpers.config import (
    check_env_variables,
    construct_secrets_path,
    load_environment_variables,
)
from rich import print


class CatAPIClient:
    """
    Handles AWS Signature Version 4 signing for API requests.

    This class is responsible for signing requests to AWS services using
    the Signature Version 4 signing process.
    """

    def __init__(self, action, img_path=None, result_id=None, debug=False):
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

        # TODO: this may fail aws sig4 signing as signer also uses url - deal with later
        request_url = (
            f"https://{self.host}{self.endpoint}/{self.result_id}"
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


class CLIArgs:
    """Setup arparse CLI options using dispatch pattern."""

    def __init__(self):
        help_banner = (
            "./cat_api_client.py --secretsfile dev_conf_secrets analyse --imgpath /path/to/image.jpg [--debug]\n"
            "./cat_api_client.py --secretsfile dev_conf_secrets results --resultid 120 [--debug]\n"
            "./cat_api_client.py --secretsfile ssm analyse --imgpath /path/to/image.jpg [--debug]\n"
        )

        parser = argparse.ArgumentParser(
            description="Cat API Client",
            usage=".e.g: ./cat_api_client.py {analyse|results} [<args>]",
        )

        parser.add_argument("command", choices=["analyse", "results"], help=help_banner)
        parser.add_argument(
            "--secretsfile",
            "-s",
            type=str,
            required=True,
            help="Secrets file name located in config folder to load environment variables from, or 'ssm' to fetch from AWS SSM Parameter Store.",
        )

        # parse_args defaults to [1:] for args, but you need to
        # exclude the rest of the args too, or validation will fail
        args = parser.parse_args(sys.argv[1:4])

        if not hasattr(CLIArgs, args.command):
            print("Unrecognized command")
            parser.print_help()
            sys.exit(42)

        # Load environment variables
        load_environment_variables(secretsfile=args.secretsfile)

        print("All environment secrets set correctly")

        getattr(self, args.command)()

    @staticmethod
    def analyse():

        parser = argparse.ArgumentParser(
            description="Upload local image to AWS Lambda analyse function",
        )

        parser.add_argument(
            "--imgpath",
            "-i",
            dest="img_path",
            type=str,
            required=True,
            help="Path to the local image to upload. e.g. /path/to/image.jpg",
        )

        parser.add_argument(
            "--debug",
            "-d",
            action="store_true",
            required=False,
            default=False,
            help="Debug mode. Set to True to enable debug output.",
        )

        args = parser.parse_args(sys.argv[4:])

        client = CatAPIClient(
            action="analyse", img_path=args.img_path, debug=args.debug
        )
        client.make_request()

    @staticmethod
    def results():

        parser = argparse.ArgumentParser(
            description="Get results from AWS Lambda results function",
        )

        parser.add_argument(
            "--resultid",
            "-r",
            dest="result_id",
            type=str,
            required=True,
            help="Result ID to get results for. e.g. 1234567890",
        )

        parser.add_argument(
            "--debug",
            "-d",
            action="store_true",
            required=False,
            default=False,
            help="Debug mode. Set to True to enable debug output.",
        )

        args = parser.parse_args(sys.argv[4:])

        client = CatAPIClient(
            action="results", img_path=None, result_id=args.result_id, debug=args.debug
        )
        client.make_request()


if __name__ == "__main__":

    CLIArgs()

    print("\nFinished")
