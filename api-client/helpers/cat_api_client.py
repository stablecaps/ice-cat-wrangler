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

from client_dynamodb_helper import ClientDynamoDBHelper
from helpers.boto3_bulk_s3_uploader import BulkS3Uploader
from helpers.boto3_clients import dyndb_client
from helpers.general import read_batch_file, write_batch_file
from rich import print
from rich.console import Console
from rich.table import Table


class CatAPIClient:
    """
    Handles AWS Signature Version 4 signing for API requests as well as boto3 requests to dynamodb & s3.

    This class is responsible for signing requests to AWS services using
    the Signature Version 4 signing process.
    """

    def __init__(
        self,
        action,
        img_path=None,
        folder_path=None,
        batch_id=None,
        batch_file=None,
        img_fprint=None,
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
        self.folder_path = folder_path
        self.img_fprint = img_fprint
        self.batch_id = batch_id
        self.batch_file = batch_file
        self.client_id = client_id
        self.debug = debug
        self.func_image_analyser_name = os.getenv("FUNC_IMAGE_ANALYSER_NAME")
        self.s3bucket_source = os.getenv("S3BUCKET_SOURCE")
        self.dynamodb_table_name = os.getenv("DYNAMODB_TABLE_NAME")

        if action == "bulkanalyse":
            self.bulkanalyse()
        elif action == "result":
            self.result()
        elif action == "bulkresults":
            self.bulk_results()
        else:
            raise ValueError(
                "Invalid action. Choose 'bulkanalyse', 'result', or 'bulkresults'."
            )

        return

    @staticmethod
    def display_rek_iscat_table(iscat_results):
        """
        Displays multiple rows of rek_iscat, batch_id, and img_fprint values in a formatted table.

        Args:
            iscat_results (list of dict): A list of dictionaries, where each dictionary contains:
                - rek_iscat (bool): The rekognition result indicating if the image contains a cat.
                - batch_id (str): The batch ID associated with the image.
                - img_fprint (str): The image fingerprint hash.
        """

        table = Table(title="Rekognition Results")

        table.add_column("rek_iscat", justify="left", style="green")
        table.add_column("batch_id", justify="left", style="magenta")
        table.add_column("img_fprint", justify="left", style="yellow")
        table.add_column("og_file", justify="left", style="cyan", no_wrap=False)
        table.add_column("s3_key short", justify="left", style="blue", no_wrap=False)

        # Add rows for each result in the list
        for result_dict in iscat_results:
            s3img_key = result_dict.get("s3img_key", None)

            s3_key_short_last = "N/A"
            if s3img_key:
                s3_key_split = s3img_key.split("/")
                s3_key_short_last = "/".join(s3_key_split[2:])

            # Conditionally format rek_iscat color
            rek_iscat = result_dict.get("rek_iscat", "N/A")
            # print("rek_iscat:", rek_iscat, type(rek_iscat))

            if rek_iscat == "N/A":
                rek_iscat_color = "red"
            elif rek_iscat.lower() == "true":
                rek_iscat_color = "green"
            elif rek_iscat.lower() == "false":
                rek_iscat_color = "red"
            else:
                rek_iscat_color = "yellow"

            table.add_row(
                f"[{rek_iscat_color}]{rek_iscat}[/]",
                str(result_dict.get("batch_id", "N/A")),
                result_dict.get("img_fprint", "N/A"),
                result_dict.get("original_file_name", "N/A"),
                s3_key_short_last,
            )

        console = Console()
        console.print(table)

    def bulkanalyse(self):
        """Uploads images in a folder to S3 and logs metadata for each upload."""
        s3_uploader = BulkS3Uploader(
            folder_path=self.folder_path,
            s3bucket_source=self.s3bucket_source,
            client_id=self.client_id,
            debug=self.debug,
        )
        s3_uploader.process_files()

    def result(self):

        dynamodb_helper = ClientDynamoDBHelper(
            dyndb_client=dyndb_client,
            table_name=self.dynamodb_table_name,
            debug=self.debug,
        )

        item = dynamodb_helper.get_item(
            batch_id=self.batch_id, img_fprint=self.img_fprint
        )
        if self.debug:
            print("Retrieved item:", item)

        rek_iscat = item.get("rek_iscat", "N/A")

        iscat_results = [
            {
                "rek_iscat": rek_iscat,
                "batch_id": self.batch_id,
                "img_fprint": self.img_fprint,
                "s3_key": item.get("s3_key", "N/A"),
            }
        ]

        # print("* ", rek_iscat, self.batch_id, self.img_fprint)
        CatAPIClient.display_rek_iscat_table(iscat_results=iscat_results)

    def bulk_results(self):
        batch_file_json = read_batch_file(batch_file_path=self.batch_file)

        if self.debug:
            print("batch_file_json:", batch_file_json)

        dynamodb_helper = ClientDynamoDBHelper(
            dyndb_client=dyndb_client,
            table_name=self.dynamodb_table_name,
            debug=self.debug,
        )
        batch_results = dynamodb_helper.get_multiple_items(
            batch_records=batch_file_json
        )

        # write the upload records to a results log file
        write_batch_file(
            filepath=f"{self.batch_file.replace('.json', '-results.json')}",
            batch_records=batch_results,
        )
        CatAPIClient.display_rek_iscat_table(iscat_results=batch_results)
