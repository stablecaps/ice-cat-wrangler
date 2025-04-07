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


class AWSRequestSigner:
    """
    Handles AWS Signature Version 4 signing for API requests.

    This class is responsible for signing requests to AWS services using
    the Signature Version 4 signing process.
    """

    def __init__(self, method, endpoint, debug=False):
        """Initializes the AWSRequestSigner with the specified secrets file.

        Args:
            secretsfile (str): The name of the secrets file to load environment variables from.

        Raises:
            SystemExit: If the environment variables are not set up properly.
        """

        self.method = method
        self.service = os.environ["SERVICE"]
        self.region = os.environ["AWS_REGION"]
        self.host = os.environ["API_HOST"]
        self.endpoint = endpoint
        self.access_key = os.environ["AWS_ACCESS_KEY_ID"]
        self.secret_key = os.environ["AWS_SECRET_ACCESS_KEY"]

        self.algorithm = "AWS4-HMAC-SHA256"
        self.datetime_obj = datetime.datetime.now(datetime.timezone.utc)
        self.amzdate = self.datetime_obj.strftime("%Y%m%dT%H%M%SZ")
        self.datestamp = self.datetime_obj.strftime("%Y%m%d")
        #
        self.debug = debug

        if self.debug:
            print("self.method", self.method)
            print("self.endpoint", self.endpoint)
            print("self.service", self.service)
            print("self.region", self.region)
            print("self.host", self.host)
            print("self.access_key", self.access_key)
            print("self.secret_key", self.secret_key)
            print("self.algorithm", self.algorithm)
            print("self.amzdate", self.amzdate)
            print("self.datestamp", self.datestamp)

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
            f"{hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()}"
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
            f"SignedHeaders={signed_headers}, Signature={signature}"
        )

    def get_auth_headers(self):
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
        if self.debug:
            print("Canonical Request:", canonical_request)
            print("String to Sign:", string_to_sign)
            print("Signature Key:", signing_key)
            print("Signature:", signature)
            print("Authorization Header:", authorization_header)
            print("Headers:", headers)

        return headers
