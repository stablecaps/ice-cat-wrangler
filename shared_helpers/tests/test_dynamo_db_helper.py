"""
Module: test_dynamo_db_helper

This module contains unit tests for the `DynamoDBHelper` class in the
`shared_helpers.dynamo_db_helper` module. The `DynamoDBHelper` class provides
helper methods for interacting with DynamoDB, including writing, updating, and
converting items to DynamoDB-compatible formats.

The tests in this module ensure that:
- The `DynamoDBHelper` class is initialized correctly with valid parameters.
- Items are successfully written to and updated in DynamoDB.
- Python dictionaries are correctly converted to DynamoDB-compatible formats.
- Missing or invalid keys in item dictionaries are handled gracefully.
- Exceptions such as `ClientError` are handled appropriately.
- Logging is performed for successful and failed operations.

Dependencies:
- pytest: For test execution and assertions.
- mocker: For mocking dependencies and DynamoDB client interactions.
- boto3: For creating DynamoDB clients.
- botocore.exceptions.ClientError: For simulating DynamoDB client errors.
- shared_helpers.dynamo_db_helper.DynamoDBHelper: The class under test.

Test Cases:
- `test_init_with_valid_parameters`: Verifies that the `DynamoDBHelper` class is initialized correctly.
- `test_convert_pydict_to_dyndb_item_with_required_keys`: Ensures Python dictionaries are converted to DynamoDB items.
- `test_write_item_success`: Verifies that items are successfully written to DynamoDB.
- `test_update_item_success`: Ensures that existing items are updated in DynamoDB.
- `test_convert_value_to_dyndb_type_different_types`: Tests conversion of various value types to DynamoDB-compatible formats.
- `test_convert_pydict_missing_required_keys`: Handles missing required keys in item dictionaries.
- `test_convert_value_invalid_number`: Handles invalid number values during conversion.
- `test_convert_value_invalid_boolean`: Handles invalid boolean values during conversion.
- `test_convert_value_key_not_in_attribute_types`: Handles unknown keys during conversion.
- `test_write_item_client_error`: Handles `ClientError` exceptions during write operations.
- `test_update_item_missing_primary_key`: Handles missing primary key attributes during update operations.
- `test_logging_on_successful_update`: Verifies logging for successful updates.
- `test_update_item_expression_building`: Ensures `update_item` builds correct expressions and attributes.
- `test_write_item_overwrites_existing`: Verifies that `write_item` overwrites existing items with the same primary key.
"""

import boto3
import pytest
from botocore.exceptions import ClientError

from shared_helpers.dynamo_db_helper import DynamoDBHelper


class TestDynamoDBHelper:
    """
    Test suite for the `DynamoDBHelper` class.
    """

    # Successfully initialize DynamoDBHelper with valid client, table name and required keys
    def test_init_with_valid_parameters(self):
        """
        Test that the `DynamoDBHelper` class is initialized correctly with valid parameters.

        Asserts:
            - The `dynamodb_client`, `table_name`, and `required_keys` attributes are set correctly.
            - The `attribute_types` dictionary contains expected keys.
        """
        # Arrange
        dyndb_client = boto3.client("dynamodb")
        table_name = "test_table"
        required_keys = ["batch_id", "img_fprint"]

        # Act
        helper = DynamoDBHelper(dyndb_client, table_name, required_keys)

        # Assert
        assert helper.dyndb_client == dyndb_client
        assert helper.table_name == table_name
        assert helper.required_keys == required_keys
        assert "img_fprint" in helper.attribute_types
        assert "batch_id" in helper.attribute_types

    # Convert Python dictionary to DynamoDB item format with all required keys present
    def test_convert_pydict_to_dyndb_item_with_required_keys(self):
        """
        Test that a Python dictionary is correctly converted to a DynamoDB item format
        when all required keys are present.

        Asserts:
            - The resulting DynamoDB item contains all required keys.
            - The values are correctly converted to DynamoDB-compatible formats.
        """
        # Arrange
        dyndb_client = boto3.client("dynamodb")
        helper = DynamoDBHelper(dyndb_client, "test_table", ["batch_id", "img_fprint"])
        item_dict = {"batch_id": 123, "img_fprint": "abc123", "client_id": "client_1"}

        # Act
        result = helper.convert_pydict_to_dyndb_item(item_dict)

        # Assert
        assert "batch_id" in result
        assert "img_fprint" in result
        assert "client_id" in result
        assert result["batch_id"] == {"N": "123"}
        assert result["img_fprint"] == {"S": "abc123"}
        assert result["client_id"] == {"S": "client_1"}

    # Write item to DynamoDB table successfully
    def test_write_item_success(self, mocker):
        """
        Test that an item is successfully written to DynamoDB.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The `put_item` method of the DynamoDB client is called with the correct parameters.
            - The response contains a successful HTTP status code.
        """
        # Arrange
        mock_client = mocker.Mock()
        mock_client.put_item.return_value = {
            "ResponseMetadata": {"HTTPStatusCode": 200}
        }

        helper = DynamoDBHelper(mock_client, "test_table", ["batch_id", "img_fprint"])
        item_dict = {"batch_id": 123, "img_fprint": "abc123", "client_id": "client_1"}

        # Act
        response = helper.write_item(item_dict)

        # Assert
        mock_client.put_item.assert_called_once()
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200

    # Update existing item in DynamoDB table with valid key attributes
    def test_update_item_success(self, mocker):
        """
        Test that an existing item is successfully updated in DynamoDB.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The `update_item` method of the DynamoDB client is called with the correct parameters.
            - The response contains a successful HTTP status code.
        """
        # Arrange
        mock_client = mocker.Mock()
        mock_client.update_item.return_value = {
            "Attributes": {"batch_id": {"N": "123"}, "img_fprint": {"S": "abc123"}},
            "ResponseMetadata": {"HTTPStatusCode": 200},
        }

        helper = DynamoDBHelper(mock_client, "test_table", ["batch_id", "img_fprint"])
        item_dict = {
            "batch_id": 123,
            "img_fprint": "abc123",
            "client_id": "updated_client",
        }

        # Act
        response = helper.update_item(item_dict)

        # Assert
        mock_client.update_item.assert_called_once()
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
        assert "Attributes" in response

    # Convert different value types (string, number, boolean) to DynamoDB-compatible format
    def test_convert_value_to_dyndb_type_different_types(self):
        """
        Test that different value types (string, number, boolean) are correctly converted
        to DynamoDB-compatible formats.

        Asserts:
            - String values are converted to type `S`.
            - Number values are converted to type `N`.
            - Boolean values are converted to type `S` (stored as strings in this implementation).
        """
        # Arrange
        dyndb_client = boto3.client("dynamodb")
        helper = DynamoDBHelper(dyndb_client, "test_table", ["batch_id", "img_fprint"])

        # Act & Assert
        # String type
        assert helper.convert_value_to_dyndb_type("client_id", "test_client") == {
            "S": "test_client"
        }

        # Number type
        assert helper.convert_value_to_dyndb_type("batch_id", 123) == {"N": "123"}

        # Boolean type (stored as string in this implementation)
        assert helper.convert_value_to_dyndb_type("rek_iscat", "true") == {"S": "true"}

    # Handle missing required keys in item_dict when converting to DynamoDB format
    def test_convert_pydict_missing_required_keys(self):
        """
        Test that a `ValueError` is raised when required keys are missing in the item dictionary.

        Asserts:
            - A `ValueError` is raised with the expected error message.
        """
        # Arrange
        dyndb_client = boto3.client("dynamodb")
        helper = DynamoDBHelper(dyndb_client, "test_table", ["batch_id", "img_fprint"])
        item_dict = {
            "batch_id": 123,
            # Missing img_fprint
            "client_id": "client_1",
        }

        # Act & Assert
        with pytest.raises(ValueError) as excinfo:
            helper.convert_pydict_to_dyndb_item(item_dict)

        assert "Missing required key" in str(excinfo.value)

    # Handle invalid number values that cannot be converted to integers
    def test_convert_value_invalid_number(self):
        """
        Test that a `ValueError` is raised when an invalid number value is provided for conversion.

        Asserts:
            - A `ValueError` is raised with the expected error message.
        """
        # Arrange
        dyndb_client = boto3.client("dynamodb")
        helper = DynamoDBHelper(dyndb_client, "test_table", ["batch_id", "img_fprint"])

        # Act & Assert
        with pytest.raises(ValueError) as excinfo:
            helper.convert_value_to_dyndb_type("batch_id", "not_a_number")

        assert "Invalid number value for key" in str(excinfo.value)

    # Handle invalid boolean values that are not "true" or "false" strings
    def test_convert_value_invalid_boolean(self):
        """
        Test that a `ValueError` is raised when an invalid boolean value is provided for conversion.

        Asserts:
            - A `ValueError` is raised with the expected error message.
        """
        # Arrange
        dyndb_client = boto3.client("dynamodb")
        helper = DynamoDBHelper(dyndb_client, "test_table", ["batch_id", "img_fprint"])

        # Act & Assert
        with pytest.raises(ValueError) as excinfo:
            helper.convert_value_to_dyndb_type("rek_iscat", "not_a_boolean")

        assert "Invalid boolean string for key" in str(excinfo.value)

    # Handle keys not found in attribute_types dictionary
    def test_convert_value_key_not_in_attribute_types(self):
        """
        Test that a `ValueError` is raised when a key is not found in the `attribute_types` dictionary.

        Asserts:
            - A `ValueError` is raised with the expected error message.
        """
        # Arrange
        dyndb_client = boto3.client("dynamodb")
        helper = DynamoDBHelper(dyndb_client, "test_table", ["batch_id", "img_fprint"])

        # Act & Assert
        with pytest.raises(ValueError) as excinfo:
            helper.convert_value_to_dyndb_type("unknown_key", "some_value")

        assert "not found in attribute_types dict" in str(excinfo.value)

    # Handle ClientError exceptions during write_item operation
    def test_write_item_client_error(self, mocker):
        """
        Test that a `RuntimeError` is raised when a `ClientError` occurs during a write operation.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - A `RuntimeError` is raised with the expected error message.
        """
        # Arrange
        mock_client = mocker.Mock()
        mock_client.put_item.side_effect = ClientError(
            {
                "Error": {
                    "Code": "ResourceNotFoundException",
                    "Message": "Table not found",
                }
            },
            "PutItem",
        )

        helper = DynamoDBHelper(mock_client, "test_table", ["batch_id", "img_fprint"])
        item_dict = {"batch_id": 123, "img_fprint": "abc123", "client_id": "client_1"}

        # Act & Assert
        with pytest.raises(RuntimeError) as excinfo:
            helper.write_item(item_dict)

        assert "Failed to write item to DynamoDB" in str(excinfo.value)

    # Handle case when primary key attributes are missing during update_item
    def test_update_item_missing_primary_key(self, mocker):
        """
        Test that a `KeyError` is raised when primary key attributes are missing during an update operation.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - A `KeyError` is raised with the expected error message.
        """
        # Arrange
        mock_dyndb_client = mocker.Mock()
        helper = DynamoDBHelper(
            mock_dyndb_client, "example_table", ["batch_id", "img_fprint"]
        )
        item_dict = {"client_id": "client_1"}  # Missing primary keys

        # Act & Assert
        with pytest.raises(KeyError):
            helper.update_item(item_dict)

    # Verify logging of errors and successful operations
    def test_logging_on_successful_update(self, mocker):
        """
        Test that a log message is generated for a successful update operation.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - A log message is generated with the details of the updated item.
        """
        # Arrange
        mock_dyndb_client = mocker.Mock()
        mock_logger = mocker.patch("shared_helpers.dynamo_db_helper.LOG")
        helper = DynamoDBHelper(
            mock_dyndb_client, "example_table", ["batch_id", "img_fprint"]
        )
        item_dict = {"batch_id": 123, "img_fprint": "abc123", "client_id": "client_1"}
        mock_dyndb_client.update_item.return_value = {"Attributes": item_dict}

        # Act
        response = helper.update_item(item_dict)

        # Assert
        assert response == {"Attributes": item_dict}
        mock_logger.info.assert_called_with(
            "Successfully updated item in DynamoDB: %s", item_dict
        )

    # Check that update_item correctly builds UpdateExpression and ExpressionAttributeValues
    def test_update_item_expression_building(self, mocker):
        """
        Test that the `update_item` method correctly builds the `UpdateExpression` and
        `ExpressionAttributeValues`.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The `UpdateExpression` is correctly constructed.
            - The `ExpressionAttributeValues` and `ExpressionAttributeNames` are correctly populated.
        """
        # Arrange
        mock_dyndb_client = mocker.Mock()
        helper = DynamoDBHelper(
            mock_dyndb_client, "example_table", ["batch_id", "img_fprint"]
        )
        item_dict = {
            "batch_id": 123,
            "img_fprint": "abc123",
            "client_id": "client_1",
            "file_name": "example.jpg",
        }

        # Mock the update_item response
        mock_dyndb_client.update_item.return_value = {
            "Attributes": {
                "batch_id": {"N": "123"},
                "img_fprint": {"S": "abc123"},
                "client_id": {"S": "client_1"},
                "file_name": {"S": "example.jpg"},
            }
        }

        # Act
        helper.update_item(item_dict)

        # Assert
        expected_update_expression = (
            "SET #client_id = :client_id, #file_name = :file_name"
        )
        expected_expression_attribute_names = {
            "#client_id": "client_id",
            "#file_name": "file_name",
        }
        expected_expression_attribute_values = {
            ":client_id": {"S": "client_1"},
            ":file_name": {"S": "example.jpg"},
        }

        mock_dyndb_client.update_item.assert_called_once_with(
            TableName="example_table",
            Key={"batch_id": {"N": "123"}, "img_fprint": {"S": "abc123"}},
            UpdateExpression=expected_update_expression,
            ExpressionAttributeNames=expected_expression_attribute_names,
            ExpressionAttributeValues=expected_expression_attribute_values,
            ReturnValues="ALL_NEW",
        )

    # Ensure write_item overwrites existing items with the same primary key
    def test_write_item_overwrites_existing(self, mocker):
        """
        Test that the `write_item` method overwrites existing items with the same primary key.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The `put_item` method of the DynamoDB client is called with the correct parameters.
        """
        # Arrange
        mock_dyndb_client = mocker.Mock()
        helper = DynamoDBHelper(
            mock_dyndb_client, "example_table", ["batch_id", "img_fprint"]
        )
        item_dict = {
            "batch_id": 123,
            "img_fprint": "abc123",
            "client_id": "client_1",
            "file_name": "example.jpg",
        }

        # Act
        helper.write_item(item_dict)

        # Assert
        expected_dyndb_item = {
            "batch_id": {"N": "123"},
            "img_fprint": {"S": "abc123"},
            "client_id": {"S": "client_1"},
            "file_name": {"S": "example.jpg"},
        }

        mock_dyndb_client.put_item.assert_called_once_with(
            TableName="example_table", Item=expected_dyndb_item
        )
