"""
cat_api_client.py

This module provides the `CatAPIClient` class, which facilitates interactions with AWS services such as
DynamoDB and S3. It supports operations like bulk image uploads, retrieving results, and processing batch
files.

Classes:
    - CatAPIClient: Manages operations for bulk uploads, result retrieval, and batch processing.

Functions:
    - gen_batch_file_path: Generates a file path for batch logs.
    - read_batch_file: Reads a batch file and returns its contents as a dictionary.
    - write_batch_file: Writes batch metadata to a file.
    - get_rek_iscat_color: Determines the color for displaying Rekognition results.
    - rich_display_table: Displays data in a formatted table using the `rich` library.

Usage:
    Import the `CatAPIClient` class and use it to perform operations like bulk uploads or retrieving results.

    Example:
        from helpers.cat_api_client import CatAPIClient

        client = CatAPIClient(
            action="bulkanalyse",
            folder_path="path/to/images",
            client_id="client123",
            debug=True
        )
        client.execute_action("bulkanalyse")

Dependencies:
    - Python 3.12 or higher
    - `boto3` for AWS interactions
    - `rich` for enhanced console output
    - Custom helper modules for S3, DynamoDB, and general utilities
"""

import json
import os

from client_dynamodb_helper import ClientDynamoDBHelper
from helpers.boto3_bulk_s3_uploader import BulkS3Uploader
from helpers.boto3_clients import dyndb_client
from helpers.general import gen_batch_file_path, read_batch_file, write_batch_file
from helpers.rich_printer import get_rek_iscat_color, rich_display_table
from rich import print


class CatAPIClient:
    """
    Manages operations for interacting with AWS services such as DynamoDB and S3.

    This class provides methods for bulk uploading images to S3, retrieving results from DynamoDB,
    and processing batch files.

    Attributes:
        img_path (str): Path to the image file.
        folder_path (str): Path to the folder containing images.
        img_fprint (str): Image fingerprint hash.
        batch_id (str): Batch ID for the operation.
        batch_file (str): Path to the batch file.
        client_id (str): Client ID for the operation.
        debug (bool): Whether debug mode is enabled.
        host (str): The API host URL.
        func_image_analyser_name (str): Name of the AWS Lambda function for image analysis.
        s3bucket_source (str): Name of the S3 bucket for uploads.
        dynamodb_table_name (str): Name of the DynamoDB table for storing results.
    """

    def __init__(self, action, **kwargs):
        """
        Initializes the CatAPIClient with the specified parameters.

        Args:
            action (str): The action to execute ('bulkanalyse', 'result', or 'bulkresults').
            **kwargs: Additional keyword arguments for initialization.
        """
        self.initialise_client(**kwargs)
        self.execute_action(action)

    def initialise_client(self, **kwargs):
        """
        Initializes instance variables and validates environment variables.

        Args:
            **kwargs: Keyword arguments for initialization. Supported keys:
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
        """
        Executes the specified action by dispatching to the appropriate method.

        Args:
            action (str): The action to execute ('bulkanalyse', 'result', or 'bulkresults').

        Raises:
            ValueError: If the specified action is invalid.
        """
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

    @staticmethod
    def display_rek_iscat_table(iscat_results):
        """
        Displays Rekognition results in a formatted table.

        Args:
            iscat_results (list of dict): List of Rekognition results to display.
        """
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

    def write_debug_logs(self, dynamodb_results):
        """
        Writes debug logs to a file if debug mode is enabled.

        Args:
            dynamodb_results (list of dict): A list of DynamoDB result dictionaries.
        """

        if self.debug:
            debug_log_file = self.batch_file.replace(".json", "-debug-logs.json")
            print(f"Writing debug logs to file: {debug_log_file}")

            # deserialize debug logs from the DynamoDB results
            deserialized_logs = None
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

    def bulkanalyse(self):
        """
        Uploads images in a folder to S3 and logs metadata for each upload.
        """
        s3_uploader = BulkS3Uploader(
            folder_path=self.folder_path,
            s3bucket_source=self.s3bucket_source,
            client_id=self.client_id,
            debug=self.debug,
        )
        s3_uploader.process_files()

    def result(self):
        """
        Fetches and displays results for a specific batch ID and image fingerprint.
        """
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

        item_list = []
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

            CatAPIClient.display_rek_iscat_table(iscat_results=iscat_results)

            # print debug logs to file
            item_list.append(item)
            self.write_debug_logs(dynamodb_results=item_list)

    def bulk_results(self):
        """
        Processes a batch file and retrieves results from DynamoDB.
        """
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
        self.write_debug_logs(dynamodb_results=batch_results)

        CatAPIClient.display_rek_iscat_table(iscat_results=batch_results)
