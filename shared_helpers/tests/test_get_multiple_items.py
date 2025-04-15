"""
Module: test_get_multiple_items

This module contains unit tests for the `get_multiple_items` method in the
`ClientDynamoDBHelper` class from the `shared_helpers.client_dynamodb_helper` module.
The `get_multiple_items` method is responsible for retrieving multiple items from a
DynamoDB table based on a list of batch records.

The tests in this module ensure that:
- The method successfully retrieves multiple items when valid batch records are provided.
- The method correctly normalizes `batch_id` values and uses them in DynamoDB queries.
- The method adds the `original_file_name` field from input records to the returned items.
- The method handles cases where no records match or all records are skipped.
- The method processes each record independently, continuing even if some records fail.
- The method handles edge cases such as empty input lists, missing fields, invalid `batch_id` formats, and exceptions like `ClientError`.

Dependencies:
- pytest: For test execution and assertions.
- pytest-mock: For mocking dependencies and DynamoDB client behavior.
- botocore.exceptions: For simulating AWS client errors.
- shared_helpers.client_dynamodb_helper.ClientDynamoDBHelper: The class under test.

Test Cases:
- `test_retrieves_multiple_items_successfully`: Verifies that the method retrieves multiple items when valid batch records are provided.
- `test_normalizes_batch_id_correctly`: Ensures the method correctly normalizes `batch_id` values by removing prefixes and converting them to strings.
- `test_adds_original_file_name_to_returned_item`: Verifies that the `original_file_name` field is added to the returned items.
- `test_returns_empty_list_when_no_records_match`: Ensures the method returns an empty list when no records match or all are skipped.
- `test_processes_records_independently`: Verifies that the method processes each record independently, continuing even if some records fail.
- `test_handles_empty_batch_records`: Ensures the method handles an empty input list gracefully by returning an empty list.
- `test_skips_records_with_missing_fields`: Verifies that the method skips records with missing `batch_id` or `img_fprint` fields.
- `test_handles_invalid_batch_id_format`: Ensures the method skips records with invalid `batch_id` formats that cannot be normalized.
- `test_continues_after_client_error`: Verifies that the method continues processing remaining records when a `ClientError` occurs for one record.
- `test_handles_none_from_get_item`: Ensures the method handles cases where `get_item` returns `None` for a record.
"""

from botocore.exceptions import ClientError

from shared_helpers.client_dynamodb_helper import ClientDynamoDBHelper


class TestGetMultipleItems:
    """
    Test suite for the `get_multiple_items` method in the `ClientDynamoDBHelper` class.
    """

    # Successfully retrieves multiple items when all records have valid batch_id and img_fprint
    def test_retrieves_multiple_items_successfully(self, mocker):
        """
        Test that the method successfully retrieves multiple items when valid batch records are provided.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The returned list contains the expected number of items.
            - Each returned item includes the expected data and `original_file_name`.
        """
        # Arrange
        mock_dynamodb_client = mocker.Mock()
        helper = ClientDynamoDBHelper(
            dyndb_client=mock_dynamodb_client, table_name="test-table"
        )

        # Mock get_item to return test data
        mocker.patch.object(
            helper, "get_item", side_effect=[{"key1": "value1"}, {"key2": "value2"}]
        )

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
        result = helper.get_multiple_items(batch_records)

        # Assert
        assert len(result) == 2
        assert result[0]["key1"] == "value1"
        assert result[0]["original_file_name"] == "file1.jpg"
        assert result[1]["key2"] == "value2"
        assert result[1]["original_file_name"] == "file2.jpg"

    # Correctly normalizes batch_id by removing 'batch-' prefix and converting to string
    def test_normalizes_batch_id_correctly(self, mocker):
        """
        Test that the method correctly normalizes `batch_id` values by removing the 'batch-' prefix and converting them to strings.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The `get_item` method is called with the normalized `batch_id` value.
        """
        # Arrange
        mock_dynamodb_client = mocker.Mock()
        helper = ClientDynamoDBHelper(
            dyndb_client=mock_dynamodb_client, table_name="test-table"
        )

        # Mock get_item method
        get_item_mock = mocker.patch.object(
            helper, "get_item", return_value={"data": "test"}
        )

        batch_records = [{"batch_id": "batch-123", "img_fprint": "abc123"}]

        # Act
        helper.get_multiple_items(batch_records)

        # Assert
        get_item_mock.assert_called_once_with("123", "abc123")

    # Adds original_file_name from input record to returned item
    def test_adds_original_file_name_to_returned_item(self, mocker):
        """
        Test that the method adds the `original_file_name` field from the input record to the returned item.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The returned item includes the `original_file_name` field with the correct value.
        """
        # Arrange
        mock_dynamodb_client = mocker.Mock()
        helper = ClientDynamoDBHelper(
            dyndb_client=mock_dynamodb_client, table_name="test-table"
        )

        # Mock get_item to return test data
        mocker.patch.object(
            helper, "get_item", return_value={"item_data": "test_value"}
        )

        batch_records = [
            {
                "batch_id": "batch-123",
                "img_fprint": "abc123",
                "original_file_name": "test_image.jpg",
            }
        ]

        # Act
        result = helper.get_multiple_items(batch_records)

        # Assert
        assert len(result) == 1
        assert result[0]["original_file_name"] == "test_image.jpg"
        assert result[0]["item_data"] == "test_value"

    # Returns empty list when no records match or all are skipped
    def test_returns_empty_list_when_no_records_match(self, mocker):
        """
        Test that the method returns an empty list when no records match or all records are skipped.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The returned list is empty.
        """
        # Arrange
        mock_dynamodb_client = mocker.Mock()
        helper = ClientDynamoDBHelper(
            dyndb_client=mock_dynamodb_client, table_name="test-table"
        )

        # Mock get_item to return None (no match)
        mocker.patch.object(helper, "get_item", return_value=None)

        batch_records = [
            {"batch_id": "batch-123", "img_fprint": "abc123"},
            {"batch_id": "batch-456", "img_fprint": "def456"},
        ]

        # Act
        result = helper.get_multiple_items(batch_records)

        # Assert
        assert result == []

    # Processes each record independently, continuing even if some fail
    def test_processes_records_independently(self, mocker):
        """
        Test that the method processes each record independently, continuing even if some records fail.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The returned list contains only the successfully processed records.
        """
        # Arrange
        mock_dynamodb_client = mocker.Mock()
        helper = ClientDynamoDBHelper(
            dyndb_client=mock_dynamodb_client, table_name="test-table"
        )

        # Mock get_item to return data for first record and None for second
        mocker.patch.object(
            helper,
            "get_item",
            side_effect=[{"data": "record1"}, None, {"data": "record3"}],
        )

        batch_records = [
            {"batch_id": "batch-123", "img_fprint": "abc123"},
            {"batch_id": "batch-456", "img_fprint": "def456"},
            {"batch_id": "batch-789", "img_fprint": "ghi789"},
        ]

        # Act
        result = helper.get_multiple_items(batch_records)

        # Assert
        assert len(result) == 2
        assert result[0]["data"] == "record1"
        assert result[1]["data"] == "record3"

    # Handles empty batch_records list
    def test_handles_empty_batch_records(self, mocker):
        """
        Test that the method handles an empty input list gracefully by returning an empty list.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The returned list is empty.
            - The `get_item` method is not called.
        """
        # Arrange
        mock_dynamodb_client = mocker.Mock()
        helper = ClientDynamoDBHelper(
            dyndb_client=mock_dynamodb_client, table_name="test-table"
        )

        # Mock get_item (should not be called)
        get_item_mock = mocker.patch.object(helper, "get_item")

        # Act
        result = helper.get_multiple_items([])

        # Assert
        assert result == []
        get_item_mock.assert_not_called()

    # Skips records with missing batch_id or img_fprint
    def test_skips_records_with_missing_fields(self, mocker):
        """
        Test that the method skips records with missing `batch_id` or `img_fprint` fields.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The `get_item` method is not called for records with missing fields.
            - The returned list contains only the successfully processed records.
        """
        # Arrange
        mock_dynamodb_client = mocker.Mock()
        helper = ClientDynamoDBHelper(
            dyndb_client=mock_dynamodb_client, table_name="test-table"
        )

        # Mock get_item
        get_item_mock = mocker.patch.object(
            helper, "get_item", return_value={"data": "test"}
        )

        batch_records = [
            {"img_fprint": "abc123"},  # Missing batch_id
            {"batch_id": "batch-456"},  # Missing img_fprint
            {"batch_id": "batch-789", "img_fprint": "ghi789"},  # Complete record
        ]

        # Act
        result = helper.get_multiple_items(batch_records)

        # Assert
        assert len(result) == 1
        get_item_mock.assert_called_once_with("789", "ghi789")

    # Handles invalid batch_id format that can't be converted to integer
    def test_handles_invalid_batch_id_format(self, mocker):
        """
        Test that the method skips records with invalid `batch_id` formats that cannot be normalized.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The `get_item` method is not called for records with invalid `batch_id` formats.
            - The returned list contains only the successfully processed records.
        """
        # Arrange
        mock_dynamodb_client = mocker.Mock()
        helper = ClientDynamoDBHelper(
            dyndb_client=mock_dynamodb_client, table_name="test-table"
        )

        # Mock get_item (should not be called for invalid batch_id)
        get_item_mock = mocker.patch.object(
            helper, "get_item", return_value={"data": "test"}
        )

        batch_records = [
            {"batch_id": "invalid-format", "img_fprint": "abc123"},  # Invalid format
            {"batch_id": "batch-456", "img_fprint": "def456"},  # Valid format
        ]

        # Act
        result = helper.get_multiple_items(batch_records)

        # Assert
        assert len(result) == 1
        get_item_mock.assert_called_once_with("456", "def456")

    # Continues processing remaining records when ClientError occurs for one record
    def test_continues_after_client_error(self, mocker):
        """
        Test that the method continues processing remaining records when a `ClientError` occurs for one record.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The returned list contains only the successfully processed records.
        """
        # Arrange
        mock_dynamodb_client = mocker.Mock()
        helper = ClientDynamoDBHelper(
            dyndb_client=mock_dynamodb_client, table_name="test-table"
        )

        # Mock get_item to raise ClientError for first record but succeed for second
        mocker.patch.object(
            helper,
            "get_item",
            side_effect=[
                ClientError({"Error": {"Message": "Test error"}}, "operation"),
                {"data": "success"},
            ],
        )

        batch_records = [
            {"batch_id": "batch-123", "img_fprint": "abc123"},
            {"batch_id": "batch-456", "img_fprint": "def456"},
        ]

        # Act
        result = helper.get_multiple_items(batch_records)

        # Assert
        assert len(result) == 1
        assert result[0]["data"] == "success"

    # Handles case when get_item returns None for a record
    def test_handles_none_from_get_item(self, mocker):
        """
        Test that the method handles cases where `get_item` returns `None` for a record.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The returned list contains only the successfully processed records.
        """
        # Arrange
        mock_dynamodb_client = mocker.Mock()
        helper = ClientDynamoDBHelper(
            dyndb_client=mock_dynamodb_client, table_name="test-table"
        )

        # Mock get_item to return None for the first record and data for the second
        mocker.patch.object(helper, "get_item", side_effect=[None, {"data": "record2"}])

        batch_records = [
            {"batch_id": "batch-123", "img_fprint": "abc123"},
            {"batch_id": "batch-456", "img_fprint": "def456"},
        ]

        # Act
        result = helper.get_multiple_items(batch_records)

        # Assert
        assert len(result) == 1
        assert result[0]["data"] == "record2"
