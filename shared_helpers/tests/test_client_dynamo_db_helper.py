"""
Module: test_client_dynamo_db_helper

This module contains unit tests for the `ClientDynamoDBHelper` class in the
`shared_helpers.client_dynamodb_helper` module. The `ClientDynamoDBHelper` class
provides helper methods for interacting with DynamoDB, including fetching and
updating items.

The tests in this module ensure that:
- Items are correctly fetched from DynamoDB using valid primary keys.
- Batch records are processed correctly, including normalization of `batch_id`.
- DynamoDB item formats are properly converted to standard Python dictionaries.
- Debug output is handled correctly when the debug flag is enabled.
- Missing or invalid batch records are skipped with appropriate error handling.
- Exceptions such as `ClientError` are handled gracefully.

Dependencies:
- pytest: For test execution and assertions.
- mocker: For mocking dependencies and DynamoDB client interactions.
- botocore.exceptions.ClientError: For simulating DynamoDB client errors.
- shared_helpers.client_dynamodb_helper.ClientDynamoDBHelper: The class under test.
"""

import pytest
from botocore.exceptions import ClientError

from shared_helpers.client_dynamodb_helper import ClientDynamoDBHelper


class TestClientDynamoDBHelper:
    """
    Test suite for the `ClientDynamoDBHelper` class.
    """

    # Successfully fetches a single item from DynamoDB with valid batch_id and img_fprint
    def test_get_item_success(self, mocker):
        """
        Test that a single item is successfully fetched from DynamoDB using valid
        `batch_id` and `img_fprint`.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The `get_item` method of the DynamoDB client is called with the correct parameters.
            - The returned item is correctly converted to a Python dictionary.
        """
        # Arrange
        mock_dyndb_client = mocker.Mock()
        mock_response = {
            "Item": {
                "batch_id": {"N": "123"},
                "img_fprint": {"S": "abc123"},
                "metadata": {"S": "test_data"},
            }
        }
        mock_dyndb_client.get_item.return_value = mock_response

        helper = ClientDynamoDBHelper(mock_dyndb_client, "test-table")

        # Act
        result = helper.get_item("123", "abc123")

        # Assert
        mock_dyndb_client.get_item.assert_called_once_with(
            TableName="test-table",
            Key={"batch_id": {"N": "123"}, "img_fprint": {"S": "abc123"}},
        )
        assert result == {
            "batch_id": "123",
            "img_fprint": "abc123",
            "metadata": "test_data",
        }

    # Successfully fetches multiple items from DynamoDB with valid batch records
    def test_get_multiple_items_success(self, mocker):
        """
        Test that multiple items are successfully fetched from DynamoDB using valid
        batch records.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The `get_item` method is called for each valid batch record.
            - The returned items are correctly converted and include additional metadata.
        """
        # Arrange
        mock_dyndb_client = mocker.Mock()
        mock_response1 = {
            "Item": {
                "batch_id": {"N": "123"},
                "img_fprint": {"S": "abc123"},
                "metadata": {"S": "test_data1"},
            }
        }
        mock_response2 = {
            "Item": {
                "batch_id": {"N": "456"},
                "img_fprint": {"S": "def456"},
                "metadata": {"S": "test_data2"},
            }
        }

        # Configure the mock to return different responses for different calls
        mock_dyndb_client.get_item.side_effect = [mock_response1, mock_response2]

        helper = ClientDynamoDBHelper(mock_dyndb_client, "test-table")
        batch_records = [
            {
                "batch_id": "batch-123",
                "img_fprint": "abc123",
                "original_file_name": "file1.jpg",
            },
            {
                "batch_id": "batch-456",
                "img_fprint": "def456",
                "original_file_name": "file2.jpg",
            },
        ]

        # Act
        results = helper.get_multiple_items(batch_records)

        # Assert
        assert len(results) == 2
        assert results[0] == {
            "batch_id": "123",
            "img_fprint": "abc123",
            "metadata": "test_data1",
            "original_file_name": "file1.jpg",
        }
        assert results[1] == {
            "batch_id": "456",
            "img_fprint": "def456",
            "metadata": "test_data2",
            "original_file_name": "file2.jpg",
        }

    # Properly converts DynamoDB item format to standard Python dictionary
    def test_dynamodb_format_conversion(self, mocker):
        """
        Test that DynamoDB item formats are correctly converted to standard Python
        dictionaries.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The returned dictionary contains the expected keys and values.
        """
        # Arrange
        mock_dyndb_client = mocker.Mock()
        mock_response = {
            "Item": {
                "batch_id": {"N": "123"},
                "img_fprint": {"S": "abc123"},
                "is_valid": {"BOOL": True},
                "count": {"N": "42"},
                "tags": {"SS": ["tag1", "tag2"]},
            }
        }
        mock_dyndb_client.get_item.return_value = mock_response

        helper = ClientDynamoDBHelper(mock_dyndb_client, "test-table")

        # Act
        result = helper.get_item("123", "abc123")

        # Assert
        assert result == {
            "batch_id": "123",
            "img_fprint": "abc123",
            "is_valid": True,
            "count": "42",
            "tags": ["tag1", "tag2"],
        }

    # Correctly handles debug output when debug flag is set to True
    def test_debug_output(self, mocker):
        """
        Test that debug output is correctly handled when the debug flag is enabled.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - Debug messages are printed using `rich_print`.
            - The debug messages include information about the fetched item.
        """
        # Arrange
        mock_dyndb_client = mocker.Mock()
        mock_response = {
            "Item": {"batch_id": {"N": "123"}, "img_fprint": {"S": "abc123"}}
        }
        mock_dyndb_client.get_item.return_value = mock_response

        # Mock rich_print to verify it's called with debug messages
        mock_rich_print = mocker.patch(
            "shared_helpers.client_dynamodb_helper.rich_print"
        )

        helper = ClientDynamoDBHelper(mock_dyndb_client, "test-table", debug=True)

        # Act
        helper.get_item("123", "abc123")

        # Assert
        # Verify rich_print was called with debug messages
        assert (
            mock_rich_print.call_count >= 3
        )  # At least 3 calls: initial message, debug message, and item retrieved

        # Verify the debug messages were printed
        debug_message_call = mock_rich_print.mock_calls[1]
        assert "Getting item info for batch_id: 123" in str(debug_message_call)

        item_debug_call = mock_rich_print.mock_calls[2]
        assert "Retrieved item:" in str(item_debug_call)

    # Properly normalizes batch_id by removing 'batch-' prefix and converting to string
    def test_batch_id_normalization(self, mocker):
        """
        Test that `batch_id` is correctly normalized by removing the `batch-` prefix
        and converting it to a string.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The `batch_id` is normalized before being used in the DynamoDB query.
        """
        # Arrange
        mock_dyndb_client = mocker.Mock()
        mock_response = {
            "Item": {
                "batch_id": {"N": "123"},
                "img_fprint": {"S": "abc123"},
                "metadata": {"S": "test_data"},
            }
        }
        mock_dyndb_client.get_item.return_value = mock_response

        helper = ClientDynamoDBHelper(mock_dyndb_client, "test-table")
        batch_records = [{"batch_id": "batch-123", "img_fprint": "abc123"}]

        # Act
        results = helper.get_multiple_items(batch_records)

        # Assert
        mock_dyndb_client.get_item.assert_called_once_with(
            TableName="test-table",
            Key={
                "batch_id": {"N": "123"},  # Normalized from "batch-123"
                "img_fprint": {"S": "abc123"},
            },
        )
        assert len(results) == 1

    # Handles case when item is not found in DynamoDB (returns None)
    def test_item_not_found(self, mocker):
        """
        Test that the `get_item` method returns `None` when the item is not found
        in DynamoDB.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The function returns `None` when the DynamoDB response does not contain an `Item` key.
        """
        # Arrange
        mock_dyndb_client = mocker.Mock()
        # Response without an Item key indicates no item was found
        mock_response = {}
        mock_dyndb_client.get_item.return_value = mock_response

        helper = ClientDynamoDBHelper(mock_dyndb_client, "test-table")

        # Act
        result = helper.get_item("123", "abc123")

        # Assert
        assert result is None
        mock_dyndb_client.get_item.assert_called_once_with(
            TableName="test-table",
            Key={"batch_id": {"N": "123"}, "img_fprint": {"S": "abc123"}},
        )

    # Handles ClientError exceptions when querying DynamoDB
    def test_client_error_handling(self, mocker):
        """
        Test that `ClientError` exceptions are handled gracefully when querying DynamoDB.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - A `ClientError` is raised when the DynamoDB client encounters an error.
            - An appropriate error message is printed.
        """
        # Arrange
        mock_dyndb_client = mocker.Mock()
        error_response = {
            "Error": {"Code": "ResourceNotFoundException", "Message": "Table not found"}
        }
        mock_dyndb_client.get_item.side_effect = ClientError(error_response, "GetItem")

        mock_rich_print = mocker.patch(
            "shared_helpers.client_dynamodb_helper.rich_print"
        )

        helper = ClientDynamoDBHelper(mock_dyndb_client, "test-table")

        # Act & Assert
        with pytest.raises(ClientError):
            helper.get_item("123", "abc123")

        # Verify error message was printed
        error_message_call = mock_rich_print.mock_calls[1]
        assert "Error fetching item from DynamoDB" in str(error_message_call)

    # Handles missing batch_id or img_fprint in batch records
    def test_missing_keys_in_batch_records(self, mocker):
        """
        Test that batch records with missing `batch_id` or `img_fprint` are skipped
        with appropriate error messages.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - Records with missing keys are skipped.
            - Error messages are printed for invalid records.
        """
        # Arrange
        mock_dyndb_client = mocker.Mock()
        mock_print = mocker.patch("builtins.print")

        helper = ClientDynamoDBHelper(mock_dyndb_client, "test-table")
        batch_records = [
            {"img_fprint": "abc123"},  # Missing batch_id
            {"batch_id": "batch-456"},  # Missing img_fprint
            {"batch_id": "batch-789", "img_fprint": "ghi789"},  # Complete record
        ]

        # Configure mock for the valid record
        mock_response = {
            "Item": {
                "batch_id": {"N": "789"},
                "img_fprint": {"S": "ghi789"},
                "metadata": {"S": "test_data"},
            }
        }
        mock_dyndb_client.get_item.return_value = mock_response

        # Act
        results = helper.get_multiple_items(batch_records)

        # Assert
        assert len(results) == 1  # Only one valid record should be processed
        assert mock_print.call_count >= 2  # Two error messages for invalid records

        # Verify the error messages
        for call_args in mock_print.call_args_list:
            args = call_args[0][0]
            if "Skipping record due to missing batch_id or img_fprint" in args:
                assert True
                break
        else:
            assert False, "Expected error message not found"

    # Handles invalid batch_id format in batch records
    def test_invalid_batch_id_format(self, mocker):
        """
        Test that batch records with invalid `batch_id` formats are skipped with
        appropriate error messages.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - Records with invalid `batch_id` formats are skipped.
            - Error messages are printed for invalid formats.
        """
        # Arrange
        mock_dyndb_client = mocker.Mock()
        mock_print = mocker.patch("builtins.print")

        helper = ClientDynamoDBHelper(mock_dyndb_client, "test-table")
        batch_records = [
            {"batch_id": "invalid-format", "img_fprint": "abc123"},  # Invalid format
            {"batch_id": "batch-456", "img_fprint": "def456"},  # Valid format
        ]

        # Configure mock for the valid record
        mock_response = {
            "Item": {
                "batch_id": {"N": "456"},
                "img_fprint": {"S": "def456"},
                "metadata": {"S": "test_data"},
            }
        }
        mock_dyndb_client.get_item.return_value = mock_response

        # Act
        results = helper.get_multiple_items(batch_records)

        # Assert
        assert len(results) == 1  # Only the valid record should be processed

        # Verify error message was printed for invalid format
        invalid_format_message_found = False
        for call_args in mock_print.call_args_list:
            args = call_args[0][0]
            if "Invalid batch_id format: invalid-format" in args:
                invalid_format_message_found = True
                break

        assert (
            invalid_format_message_found
        ), "Error message for invalid batch_id format not found"

    # Processes batch records with missing original_file_name by setting default value 'N/A'
    def test_missing_original_file_name(self, mocker):
        """
        Test that batch records with missing `original_file_name` are processed
        by setting a default value of "N/A".

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The `original_file_name` field is set to "N/A" for records where it is missing.
        """
        # Arrange
        mock_dyndb_client = mocker.Mock()
        mock_response = {
            "Item": {
                "batch_id": {"N": "123"},
                "img_fprint": {"S": "abc123"},
                "metadata": {"S": "test_data"},
            }
        }
        mock_dyndb_client.get_item.return_value = mock_response

        helper = ClientDynamoDBHelper(mock_dyndb_client, "test-table")
        batch_records = [
            {
                "batch_id": "batch-123",
                "img_fprint": "abc123",
            }  # Missing original_file_name
        ]

        # Act
        results = helper.get_multiple_items(batch_records)

        # Assert
        assert len(results) == 1
        assert results[0]["original_file_name"] == "N/A"  # Default value should be set
        assert results[0]["batch_id"] == "123"
        assert results[0]["img_fprint"] == "abc123"
        assert results[0]["metadata"] == "test_data"
