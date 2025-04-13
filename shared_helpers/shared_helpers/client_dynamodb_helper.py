"""
client_dynamodb_helper.py

This module provides a helper class for interacting with AWS DynamoDB. It includes methods for fetching
single and multiple items from a DynamoDB table.

Classes:
    - ClientDynamoDBHelper: A helper class for DynamoDB operations.

Dependencies:
    - Python 3.12 or higher
    - `boto3` for AWS DynamoDB interactions
    - `botocore.exceptions.ClientError` for handling AWS client errors
    - `rich` for enhanced console output
"""

from botocore.exceptions import ClientError
from rich import print as rich_print


class ClientDynamoDBHelper:
    """
    A helper class for interacting with AWS DynamoDB.

    This class provides methods to fetch single and multiple items from a DynamoDB table.
    """

    def __init__(self, dyndb_client, table_name, debug=False):
        """
        Initializes the DynamoDBHelper.

        Args:
            dyndb_client (boto3.client): A boto3 DynamoDB client instance.
            table_name (str): The name of the DynamoDB table.
            debug (bool): Whether to enable debug output.
        """
        self.table_name = table_name
        self.debug = debug
        self.dynamodb_client = dyndb_client

    def get_item(self, batch_id, img_fprint):
        """
        Fetches a single item from the DynamoDB table.

        Args:
            batch_id (str): The batch ID of the item to fetch.
            img_fprint (str): The image fingerprint of the item to fetch.

        Returns:
            dict or None: A dictionary representing the item if found, otherwise None.

        Raises:
            ClientError: If there is an error querying DynamoDB.
        """
        rich_print(
            f"Fetching item from table '{self.table_name}' with batch_id='{batch_id}'"
            " and img_fprint='{img_fprint}'"
        )
        try:

            if self.debug:
                # TODO: sort this
                rich_print(
                    f"Getting item info for batch_id: {batch_id} and img_fprint: {img_fprint}"
                )

            response = self.dynamodb_client.get_item(
                TableName=self.table_name,
                Key={
                    "batch_id": {"N": str(batch_id)},
                    "img_fprint": {"S": img_fprint},
                },
            )

            item = response.get("Item", None)

            if self.debug:
                rich_print(f"Retrieved item: {item}")

            # Convert the DynamoDB item format to a standard Python dictionary
            # print({k: list(v.values())[0] for k, v in response["Item"].items()}[rek_iscat])
            # import sys
            # sys.exit(42)

            # return {k: list(v.values())[0] for k, v in item.items()} if item else None
            return (
                {k: list(v.values())[0] for k, v in response["Item"].items()}
                if item
                else None
            )

        except ClientError as e:
            rich_print(
                f"Error fetching item from DynamoDB: {e.response['Error']['Message']}"
            )
            raise

    def get_multiple_items(self, batch_records):
        """
        Fetches multiple items from DynamoDB based on batch records.

        Args:
            batch_records (list): A list of dictionaries containing batch_id and img_fprint.

        Returns:
            list: A list of dictionaries representing the retrieved items.
        """
        results_list = []

        for record in batch_records:
            batch_id = record.get("batch_id")
            img_fprint = record.get("img_fprint")

            if not batch_id or not img_fprint:
                print(
                    f"Skipping record due to missing batch_id or img_fprint: {record}"
                )
                continue

            # Normalize batch_id
            try:
                batch_id = str(int(batch_id.replace("batch-", "")))
            except ValueError:
                print(f"Invalid batch_id format: {batch_id}")
                continue

            # Fetch the item using the helper method
            try:
                item = self.get_item(batch_id, img_fprint)
                if item:
                    # Add additional identifying info
                    item["original_file_name"] = record.get("original_file_name", "N/A")
                    results_list.append(item)
                else:
                    print(
                        f"No record found for batch_id={batch_id}, img_fprint={img_fprint}"
                    )
            except ClientError as err:
                print(
                    f"Error querying DynamoDB for batch_id={batch_id}, img_fprint={img_fprint}: {err}"
                )
                continue

        return results_list
