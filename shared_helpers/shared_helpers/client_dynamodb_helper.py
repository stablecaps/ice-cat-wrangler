from botocore.exceptions import ClientError
from rich import print as rich_print


class ClientDynamoDBHelper:
    """
    Client helper class for interacting with DynamoDB.
    Provides methods to get items from a DynamoDB table using a client.
    """

    def __init__(self, dyndb_client, table_name, debug=False):
        """
        Initializes the DynamoDBHelper.

        Args:
            table_name (str): The name of the DynamoDB table.
            debug (bool): Whether to enable debug output.
        """
        self.table_name = table_name
        self.debug = debug
        self.dynamodb_client = dyndb_client

    def get_item(self, batch_id, img_fprint):
        """
        Retrieves an item from the DynamoDB table using the primary key and sort key.

        Args:
            batch_id (str): The primary key value.
            img_fprint (str): The sort key value.

        Returns:
            dict: The retrieved item, or None if not found.

        Raises:
            ClientError: If there is an error during the DynamoDB operation.
        """

        rich_print(
            f"Fetching item from table '{self.table_name}' with batch_id='{batch_id}' and img_fprint='{img_fprint}'"
        )
        try:

            if self.debug:
                # TODO: sort this
                rich_print(
                    f"Getting logging info for batch_id: {batch_id} and img_fprint: {img_fprint}"
                )

            response = self.dynamodb_client.get_item(
                TableName=self.table_name,
                Key={
                    "batch_id": {"N": str(batch_id)},
                    "img_fprint": {"S": img_fprint},
                },
            )

            item = response.get("Item", None)

            rich_print(f"Retrieved item: {item}")

            # Convert the DynamoDB item format to a standard Python dictionary
            return {k: list(v.values())[0] for k, v in item.items()} if item else None

        except ClientError as e:
            rich_print(
                f"Error fetching item from DynamoDB: {e.response['Error']['Message']}"
            )
            raise

    def get_multiple_items(self, batch_records):
        """
        Queries DynamoDB for related records based on batch_id and img_fprint.

        Args:
            batch_records (list of dict): List of dictionaries containing `batch_id` and `img_fprint`.

        Returns:
            list of dict: A list of dictionaries containing the queried DynamoDB records.

        Raises:
            Exception: If there is an error querying DynamoDB.
        """
        results = []

        for record in batch_records:
            # print("record", record)

            batch_id = str(int(record.get("batch_id").replace("batch-", "")))
            img_fprint = record.get("img_fprint")
            if not batch_id or not img_fprint:
                print(
                    f"Skipping record due to missing batch_id or img_fprint: {record}"
                )
                continue

            try:
                response = self.dynamodb_client.get_item(
                    TableName=self.table_name,
                    Key={
                        "batch_id": {"N": batch_id},
                        "img_fprint": {"S": img_fprint},
                    },
                )

                # Check if the item exists in the response
                if "Item" in response:
                    item = {k: list(v.values())[0] for k, v in response["Item"].items()}
                    results.append(item)
                else:
                    print(
                        f"No record found for batch_id={batch_id}, img_fprint={img_fprint}"
                    )

            except ClientError as err:
                print(
                    f"Error querying DynamoDB for batch_id={batch_id}, img_fprint={img_fprint}: {err}"
                )
                continue

        return results
