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
    """Check whether environment variables have been correctly loaded."""

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
    def __init__(self, secretsfile):

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
        self.datetime_obj = datetime.datetime.now(datetime.UTC)
        self.amzdate = self.datetime_obj.strftime("%Y%m%dT%H%M%SZ")
        self.datestamp = self.datetime_obj.strftime("%Y%m%d")

    @staticmethod
    def construct_secrets_path(secret_filename):
        root_dir = os.path.dirname(os.path.abspath(__file__))
        dotenv_path = root_dir + "/config/" + secret_filename
        return dotenv_path

    def create_canonical_request(self):
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
        credential_scope = f"{self.datestamp}/{self.region}/{self.service}/aws4_request"
        string_to_sign = (
            f"{self.algorithm}\n{self.amzdate}\n{credential_scope}\n"
            + hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()
        )
        return string_to_sign, credential_scope

    def sign(self, key, msg):
        return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

    def get_signature_key(self):
        kdate = self.sign(("AWS4" + self.secret_key).encode("utf-8"), self.datestamp)
        kregion = self.sign(kdate, self.region)
        kservice = self.sign(kregion, self.service)
        ksigning = self.sign(kservice, "aws4_request")
        return ksigning

    def create_authorization_header(self, credential_scope, signed_headers, signature):
        return (
            f"{self.algorithm} Credential={self.access_key}/{credential_scope}, "
            + f"SignedHeaders={signed_headers}, Signature={signature}"
        )

    def make_request(self):
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

    signer = AWSRequestSigner(secretsfile="dev_conf_secrets")
    response_text = signer.make_request()
    print(response_text)
