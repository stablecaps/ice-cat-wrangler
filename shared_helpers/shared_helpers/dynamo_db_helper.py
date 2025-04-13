import logging

from botocore.exceptions import ClientError

# TODO: check logs propagate into dynamodb
# use without __name__ as this module will propagate logs to lambda root logger to enable LogCollectorHandler
LOG = logging.getLogger()


class DynamoDBHelper:
    """Helper class for interacting with DynamoDB.

    This class provides methods to write and update items in a DynamoDB table,
    as well as utilities for converting Python dictionaries to DynamoDB item formats.
    """

    def __init__(self, dyndb_client, table_name, required_keys):
        """Initializes the DynamoDBHelper class.

        Args:
            dyndb_client (boto3.client): The DynamoDB client instance.
            table_name (str): The name of the DynamoDB table.
            required_keys (list): A list of required keys that must be present in the item_dict.
        """
        self.dyndb_client = dyndb_client
        self.table_name = table_name
        self.required_keys = required_keys

        # ice-cat-wrangler key types
        self.attribute_types = {
            "img_fprint": "S",
            "batch_id": "N",
            "client_id": "S",
            "s3img_key": "S",
            "file_name": "S",
            "op_status": "S",
            "rek_resp": "S",
            "rek_iscat": "BOOL",
            "logs": "S",
            "current_date": "S",
            "upload_ts": "N",
            "rek_ts": "N",
            "ttl": "N",
        }

    def convert_value_to_dyndb_type(self, key, value):
        """Converts a Python value to a DynamoDB-compatible type.

        Args:
            key (str): The attribute key.
            value (Any): The value to be converted.

        Returns:
            dict: A dictionary representing the DynamoDB-compatible value.

        Raises:
            ValueError: If the key is not found in `attribute_types` or if the value
                cannot be converted to the expected type.
        """
        if key not in self.attribute_types:
            LOG.error("Key: <%s> not found in attribute_types dict", key)
            raise ValueError("Key: <%s> not found in attribute_types dict", key)

        attr_type = self.attribute_types[key]

        # Convert the value based on the attribute type
        if attr_type == "S":  # String
            return {"S": str(value)}
        elif attr_type == "N":  # Assume all numbers are integers
            try:
                return {"N": str(int(value))}  # Convert to stringified integer
            except ValueError:
                LOG.error("Invalid number value for key: %s", key)
                raise ValueError("Invalid number value for key: %s", key)
        elif attr_type == "BOOL":  # Ensure booleans are converted to True/False
            if isinstance(value, str):
                if value.lower() not in ["true", "false"]:
                    LOG.error("Invalid boolean string for key: %s", key)
                    raise ValueError("Invalid boolean string for key: %s", key)
            else:
                LOG.error("Boolean value not represented as a string for key: %s", key)
                raise ValueError(
                    "Boolean value not represented as a string for key: %s", key
                )
            return {"S": value}
        elif attr_type == "M":  # Map (JSON)
            return {"M": value}  # Assume value is already a dictionary
        elif attr_type == "NULL":  # Null
            return {"NULL": True}
        else:
            LOG.error("Unsupported attribute type for key: %s", key)
            raise ValueError(f"Unsupported attribute type for key: {key}")

    def convert_pydict_to_dyndb_item(self, item_dict):
        """Converts a Python dictionary to a DynamoDB item format.

        Args:
            item_dict (dict): The Python dictionary to be converted.

        Returns:
            dict: A dictionary in DynamoDB item format.

        Raises:
            ValueError: If any required key is missing or if a value cannot be converted.
        """
        # Check for required keys
        for key in self.required_keys:
            if key not in item_dict or item_dict[key] is None:
                LOG.error("Missing required key: %s", key)
                raise ValueError("Missing required key: %s", key)

        # Convert item_dict to DynamoDB item format
        dyndb_item = {}
        for key, value in item_dict.items():
            dyndb_item[key] = self.convert_value_to_dyndb_type(key, value)

        return dyndb_item

    def write_item(self, item_dict):
        """Writes an item to the DynamoDB table.

        Args:
            item_dict (dict): The item to be written to the table.

        Returns:
            dict: The response from the DynamoDB `put_item` operation.

        Raises:
            RuntimeError: If the `put_item` operation fails.
        """
        # TODO: Preprocess the `rek_resp` field if it exists
        # if "rek_resp" in item_dict:
        #     item_dict["rek_resp"] = DynamoDBHelper.preprocess_dynamodb_dict(item_dict["rek_resp"])

        dyndb_item = self.convert_pydict_to_dyndb_item(item_dict)

        LOG.info("DynamoDB item to write: %s", dyndb_item)

        try:
            # The database will overwrite an existing item with the same primary key
            response = self.dyndb_client.put_item(
                TableName=self.table_name, Item=dyndb_item
            )
            LOG.info("Successfully wrote item to DynamoDB: %s", item_dict)
            return response
        except ClientError as err:
            LOG.error("Failed to write item to DynamoDB: %s", err)
            raise RuntimeError(f"Failed to write item to DynamoDB: {err}") from err

    def update_item(self, item_dict):
        """Updates an item in the DynamoDB table.

        Args:
            item_dict (dict): The item to be updated. Must include the primary key attributes
                (`batch_id` and `img_fprint`) and any other attributes to update.

        Returns:
            dict: The response from the DynamoDB `update_item` operation.

        Raises:
            RuntimeError: If the `update_item` operation fails.
        """
        # Extract and convert the primary key attributes
        key = {
            "batch_id": self.convert_value_to_dyndb_type(
                "batch_id", item_dict.pop("batch_id")
            ),
            "img_fprint": self.convert_value_to_dyndb_type(
                "img_fprint", item_dict.pop("img_fprint")
            ),
        }

        # Build the UpdateExpression and ExpressionAttributeValues
        update_expression = "SET " + ", ".join(f"#{k} = :{k}" for k in item_dict.keys())

        expression_attribute_names = {f"#{k}": k for k in item_dict.keys()}

        expression_attribute_values = {
            f":{k}": self.convert_value_to_dyndb_type(k, v)
            for k, v in item_dict.items()
        }

        try:
            response = self.dyndb_client.update_item(
                TableName=self.table_name,
                Key=key,
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_attribute_names,
                ExpressionAttributeValues=expression_attribute_values,
                ReturnValues="ALL_NEW",
            )
            LOG.info(
                "Successfully updated item in DynamoDB: %s", response["Attributes"]
            )
            return response
        except ClientError as err:
            LOG.error("Failed to update item in DynamoDB: %s", err)
            raise RuntimeError(
                f"Failed to update item in table {self.table_name}"
            ) from err
