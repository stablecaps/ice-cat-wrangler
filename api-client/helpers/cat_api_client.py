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
from helpers.general import gen_batch_file_path, read_batch_file, write_batch_file
from helpers.rich_printer import get_rek_iscat_color, rich_display_table
from rich import print


class CatAPIClient:
    """
    Handles AWS Signature Version 4 signing for API requests as well as boto3 requests to DynamoDB & S3.
    """

    def __init__(self, action, **kwargs):
        """
        initialises the CatAPIClient with the specified parameters.

        Args:
            action (str): The action to execute ('bulkanalyse', 'result', or 'bulkresults').
            **kwargs: Additional keyword arguments for initialisation.
        """
        self.initialise_client(**kwargs)
        self.execute_action(action)

    def initialise_client(self, **kwargs):
        """
        initialises instance variables and validates environment variables.

        Args:
            **kwargs: Keyword arguments for initialisation. Supported keys:
                - img_path (str, optional): Path to the image file.
                - folder_path (str, optional): Path to the folder containing images.
                - batch_id (str, optional): Batch ID for the operation.
                - batch_file (str, optional): Path to the batch file.
                - img_fprint (str, optional): Image fingerprint hash.
                - client_id (str, optional): Client ID for the operation.
                - debug (bool, optional): Whether to enable debug mode.

        Raises:
            EnvironmentError: If required environment variables are missing.
        """
        # Instance variables
        self.img_path = kwargs.get("img_path")
        self.folder_path = kwargs.get("folder_path")
        self.img_fprint = kwargs.get("img_fprint")
        self.batch_id = kwargs.get("batch_id")
        self.batch_file = kwargs.get("batch_file")
        self.client_id = kwargs.get("client_id")
        self.debug = kwargs.get("debug", False)

        # Environment variables
        self.host = os.getenv("API_HOST")
        self.func_image_analyser_name = os.getenv("FUNC_IMAGE_ANALYSER_NAME")
        self.s3bucket_source = os.getenv("S3BUCKET_SOURCE")
        self.dynamodb_table_name = os.getenv("DYNAMODB_TABLE_NAME")

        # Generate batch file path if not provided
        if self.batch_file is None:
            self.batch_file = gen_batch_file_path(
                client_id=self.client_id, batch_id=self.batch_id
            )
        if self.debug:
            print("initialised batch_file:", self.batch_file)

    def execute_action(self, action):
        actions = {
            "bulkanalyse": self.bulkanalyse,
            "result": self.result,
            "bulkresults": self.bulk_results,
        }
        if action in actions:
            actions[action]()
        else:
            raise ValueError(
                "Invalid action. Choose 'bulkanalyse', 'result', or 'bulkresults'."
            )

    # @staticmethod
    # def display_rek_iscat_table(iscat_results):
    #     """
    #     Displays multiple rows of rek_iscat, batch_id, and img_fprint values in a formatted table.

    #     Args:
    #         iscat_results (list of dict): A list of dictionaries, where each dictionary contains:
    #             - rek_iscat (bool): The rekognition result indicating if the image contains a cat.
    #             - batch_id (str): The batch ID associated with the image.
    #             - img_fprint (str): The image fingerprint hash.
    #     """

    #     table = Table(title="Rekognition Results")

    #     table.add_column("rek_iscat", justify="left", style="green")
    #     table.add_column("batch_id", justify="left", style="magenta")
    #     table.add_column("img_fprint", justify="left", style="yellow")
    #     table.add_column("og_file", justify="left", style="cyan", no_wrap=False)
    #     table.add_column("s3_key short", justify="left", style="blue", no_wrap=False)

    #     # Add rows for each result in the list
    #     for result_dict in iscat_results:
    #         s3img_key = result_dict.get("s3img_key", None)

    #         s3_key_short_last = "N/A"
    #         if s3img_key:
    #             s3_key_split = s3img_key.split("/")
    #             s3_key_short_last = "/".join(s3_key_split[2:])

    #         # Conditionally format rek_iscat color
    #         rek_iscat = result_dict.get("rek_iscat", "N/A")
    #         # print("rek_iscat:", rek_iscat, type(rek_iscat))

    #         if rek_iscat == "N/A":
    #             rek_iscat_color = "red"
    #         elif rek_iscat.lower() == "true":
    #             rek_iscat_color = "green"
    #         elif rek_iscat.lower() == "false":
    #             rek_iscat_color = "red"
    #         else:
    #             rek_iscat_color = "yellow"

    #         table.add_row(
    #             f"[{rek_iscat_color}]{rek_iscat}[/]",
    #             str(result_dict.get("batch_id", "N/A")),
    #             result_dict.get("img_fprint", "N/A"),
    #             result_dict.get("original_file_name", "N/A"),
    #             s3_key_short_last,
    #         )

    #     console = Console()
    #     console.print(table)

    @staticmethod
    def display_rek_iscat_table(iscat_results):
        # Define table columns
        columns = [
            {"header": "rek_iscat", "key": "rek_iscat", "style": "green"},
            {"header": "batch_id", "key": "batch_id", "style": "magenta"},
            {"header": "img_fprint", "key": "img_fprint", "style": "yellow"},
            {"header": "og_file", "key": "original_file_name", "style": "cyan"},
            {"header": "s3_key short", "key": "s3img_key", "style": "blue"},
        ]

        # Add color formatting for rek_iscat
        for result in iscat_results:
            rek_iscat = result.get("rek_iscat", "N/A")
            result["rek_iscat"] = f"[{get_rek_iscat_color(rek_iscat)}]{rek_iscat}[/]"

        rich_display_table(
            data=iscat_results, title="Rekognition Results", columns=columns
        )

    def bulkanalyse(self):
        """Uploads images in a folder to S3 and logs metadata for each upload."""
        s3_uploader = BulkS3Uploader(
            folder_path=self.folder_path,
            s3bucket_source=self.s3bucket_source,
            client_id=self.client_id,
            debug=self.debug,
        )
        s3_uploader.process_files()

    # @staticmethod
    def write_debug_logs_to_file(self, dynamodb_results):
        """
        Writes debug logs to a file if debug mode is enabled.

        Args:
            batch_file (str): The base batch file name (used to generate the debug log file name).
            dynamodb_results (list of dict): A list of DynamoDB result dictionaries.
            debug (bool): Whether debug mode is enabled.
        """
        import json

        if self.debug:
            debug_log_file = self.batch_file.replace(".json", "-debug-logs.json")
            print(f"Writing debug logs to file: {debug_log_file}")

            # deserialize debug logs from the DynamoDB results
            for item in dynamodb_results:
                logs = item.get("logs", None)
                if logs is not None:
                    try:
                        deserialized_logs = json.loads(logs)
                    except json.JSONDecodeError:
                        print(f"Failed to decode logs for item: {item}")
                        continue

            if deserialized_logs:
                write_batch_file(
                    filepath=debug_log_file,
                    batch_records=deserialized_logs,
                )
                print(f"Debug logs successfully written to: {debug_log_file}")
            else:
                print("No valid debug logs found in the provided DynamoDB results.")

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

        if item:
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
            CatAPIClient.rich_display_table(iscat_results=iscat_results)

            # print debug logs to file
            self.write_debug_logs_to_file(dynamodb_results=[item])

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

        # write the dynamodb records to a results log file
        write_batch_file(
            filepath=f"{self.batch_file.replace('.json', '-results.json')}",
            batch_records=batch_results,
        )

        # print debug logs to file
        self.write_debug_logs_to_file(dynamodb_results=batch_results)

        CatAPIClient.display_rek_iscat_table(iscat_results=batch_results)
