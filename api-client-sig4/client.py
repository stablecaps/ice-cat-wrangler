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
from dotenv import load_dotenv
from rich import print

secret_vars = [
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "AWS_REGION",
    "METHOD",
    "SERVICE",
    "API_HOST",
    "API_ENDPOINT",
]


def check_env_variables(dotenv_path):
    """Check whether environment variables have been correctly loaded.

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

    if not os.path.isfile(dotenv_path):
        print("No secret file found at dotenv_path: %s", dotenv_path)
        sys.exit(1)

    # load env variables
    load_dotenv(dotenv_path, override=True)

    # check to see if env variables are available to app
    passed = True
    for secret in secret_vars:
        if secret not in os.environ:
            print("Environment secret not set: %s", secret)
            passed = False

    return passed


class AWSRequestSigner:
    """
    Handles AWS Signature Version 4 signing for API requests.

    This class is responsible for signing requests to AWS services using
    the Signature Version 4 signing process.
    """

    def __init__(self, secretsfile):
        """Initializes the AWSRequestSigner with the specified secrets file.

        Args:
            secretsfile (str): The name of the secrets file to load environment variables from.

        Raises:
            SystemExit: If the environment variables are not set up properly.
        """
        dotenv_path = AWSRequestSigner.construct_secrets_path(
            secret_filename=secretsfile
        )
        has_env_vars = check_env_variables(dotenv_path=dotenv_path)
        if not has_env_vars:
            print("\nEnv variables not set up properly. Exiting...")
            sys.exit(1)

        print("All environment secrets set correctly")

        self.method = os.environ["METHOD"]
        self.service = os.environ["SERVICE"]
        self.region = os.environ["AWS_REGION"]
        self.host = os.environ["API_HOST"]
        self.endpoint = os.environ["API_ENDPOINT"]
        self.access_key = os.environ["AWS_ACCESS_KEY_ID"]
        self.secret_key = os.environ["AWS_SECRET_ACCESS_KEY"]

        self.algorithm = "AWS4-HMAC-SHA256"
        self.datetime_obj = datetime.datetime.now(datetime.timezone.utc)
        self.amzdate = self.datetime_obj.strftime("%Y%m%dT%H%M%SZ")
        self.datestamp = self.datetime_obj.strftime("%Y%m%d")

    @staticmethod
    def construct_secrets_path(secret_filename):
        """Constructs the full path to the secrets file.

        Args:
            secret_filename (str): The name of the secrets file.

        Returns:
            str: The full path to the secrets file.
        """
        root_dir = os.path.dirname(os.path.abspath(__file__))
        dotenv_path = root_dir + "/config/" + secret_filename
        return dotenv_path

    def create_canonical_request(self):
        """Creates the canonical request for AWS Signature Version 4.

        Returns:
            tuple: A tuple containing the canonical request (str) and signed headers (str).
        """
        canonical_uri = self.endpoint
        canonical_querystring = ""
        canonical_headers = f"host:{self.host}\n"
        signed_headers = "host"
        payload_hash = hashlib.sha256("".encode("utf-8")).hexdigest()
        canonical_request = (
            f"{self.method}\n{canonical_uri}\n{canonical_querystring}\n"
            f"{canonical_headers}\n{signed_headers}\n{payload_hash}"
        )
        return canonical_request, signed_headers

    def create_string_to_sign(self, canonical_request):
        """Creates the string to sign for AWS Signature Version 4.

        Args:
            canonical_request (str): The canonical request string.

        Returns:
            tuple: A tuple containing the string to sign (str) and the credential scope (str).
        """
        credential_scope = f"{self.datestamp}/{self.region}/{self.service}/aws4_request"
        string_to_sign = (
            f"{self.algorithm}\n{self.amzdate}\n{credential_scope}\n"
            + hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()
        )
        return string_to_sign, credential_scope

    def sign(self, key, msg):
        """Signs a message with the given key using HMAC-SHA256.

        Args:
            key (bytes): The signing key.
            msg (str): The message to sign.

        Returns:
            bytes: The HMAC-SHA256 signature.
        """
        return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

    def get_signature_key(self):
        """Generates the signing key for AWS Signature Version 4.

        Returns:
            bytes: The signing key.
        """
        kdate = self.sign(("AWS4" + self.secret_key).encode("utf-8"), self.datestamp)
        kregion = self.sign(kdate, self.region)
        kservice = self.sign(kregion, self.service)
        ksigning = self.sign(kservice, "aws4_request")
        return ksigning

    def create_authorization_header(self, credential_scope, signed_headers, signature):
        """Creates the Authorization header for the request.

        Args:
            credential_scope (str): The credential scope string.
            signed_headers (str): The signed headers string.
            signature (str): The computed signature.

        Returns:
            str: The Authorization header.
        """
        return (
            f"{self.algorithm} Credential={self.access_key}/{credential_scope}, "
            + f"SignedHeaders={signed_headers}, Signature={signature}"
        )

    def make_request(self):
        """Makes a signed request to the AWS API.

        Returns:
            str: The response text from the API.

        Raises:
            requests.exceptions.RequestException: If the request fails.
        """
        canonical_request, signed_headers = self.create_canonical_request()
        string_to_sign, credential_scope = self.create_string_to_sign(canonical_request)
        signing_key = self.get_signature_key()
        signature = hmac.new(
            signing_key, string_to_sign.encode("utf-8"), hashlib.sha256
        ).hexdigest()
        authorization_header = self.create_authorization_header(
            credential_scope, signed_headers, signature
        )

        headers = {
            "Host": self.host,
            "x-amz-date": self.amzdate,
            "Authorization": authorization_header,
        }

        request_url = f"https://{self.host}{self.endpoint}"
        response = requests.get(request_url, headers=headers, timeout=5)
        response.raise_for_status()
        return response.text


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="AWS Request Signer Client",
        usage=".e.g: /client.py --secretsfile dev_conf_secrets",
    )
    parser.add_argument(
        "--secretsfile",
        type=str,
        required=True,
        help="Secrets file name to load environment variables from. Should be in config folder. e.g. dev_conf_secrets",
    )
    args = parser.parse_args()

    signer = AWSRequestSigner(secretsfile=args.secretsfile)
    response_text = signer.make_request()
    print(response_text)
