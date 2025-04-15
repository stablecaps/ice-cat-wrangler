"""
Module: test_get_filebytes_from_s3

This module contains unit tests for the `get_filebytes_from_s3` function in the
`shared_helpers.boto3_helpers` module. The `get_filebytes_from_s3` function is responsible
for retrieving the content of a file from an S3 bucket as bytes using a provided boto3 client.

The tests in this module ensure that:
- The function successfully retrieves file bytes from S3 when valid parameters are provided.
- The function correctly uses the provided S3 client to make the `get_object` call.
- The function handles various edge cases, such as empty bucket names or keys, nonexistent objects, and insufficient permissions.
- The function handles exceptions such as `ClientError` and unexpected errors gracefully.
- The function works correctly with different file types and sizes, including large files.

Dependencies:
- pytest: For test execution and assertions.
- pytest-mock: For mocking dependencies and S3 client behavior.
- botocore.exceptions: For simulating AWS client errors.
- shared_helpers.boto3_helpers.get_filebytes_from_s3: The function under test.

Test Cases:
- `test_successful_retrieval_of_file_bytes`: Verifies that the function retrieves file bytes when valid parameters are provided.
- `test_returns_correct_byte_content`: Ensures the function returns the correct byte content of the requested S3 object.
- `test_uses_provided_s3_client`: Verifies that the function correctly uses the provided S3 client to make the `get_object` call.
- `test_extracts_content_from_response_body`: Ensures the function extracts and returns the file content from the response body.
- `test_handles_and_reraises_client_error`: Verifies that the function handles and re-raises `ClientError` with appropriate logging.
- `test_handles_and_reraises_unexpected_exceptions`: Ensures the function handles and re-raises unexpected exceptions with appropriate logging.
- `test_empty_bucket_name`: Verifies the function's behavior when the `bucket_name` is an empty string.
- `test_empty_s3_key`: Verifies the function's behavior when the `s3_key` is an empty string.
- `test_nonexistent_s3_object`: Ensures the function handles the case where the requested S3 object does not exist.
- `test_insufficient_permissions`: Verifies the function's behavior when the user lacks permissions to access the S3 object.
- `test_large_file_handling`: Ensures the function handles large files appropriately.
- `test_performance_with_various_file_types`: Verifies the function's performance with different file types (e.g., text, binary).
"""

import pytest
from botocore.exceptions import ClientError

from shared_helpers.boto3_helpers import get_filebytes_from_s3


class TestGetFilebytesFromS3:
    """
    Test suite for the `get_filebytes_from_s3` function.
    """

    # Successfully retrieves file bytes from S3 when valid parameters are provided
    def test_successful_retrieval_of_file_bytes(self, mocker):
        """
        Test that the function successfully retrieves file bytes from S3 when valid parameters are provided.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The `get_object` method of the S3 client is called with the correct arguments.
            - The returned content matches the expected file bytes.
        """
        # Arrange
        mock_s3_client = mocker.Mock()
        mock_response = {"Body": mocker.Mock()}
        mock_response["Body"].read.return_value = b"test file content"
        mock_s3_client.get_object.return_value = mock_response

        bucket_name = "test-bucket"
        s3_key = "test/file.txt"

        # Act

        result = get_filebytes_from_s3(mock_s3_client, bucket_name, s3_key)

        # Assert
        mock_s3_client.get_object.assert_called_once_with(
            Bucket=bucket_name, Key=s3_key
        )
        assert result == b"test file content"

    # Returns the correct byte content of the requested S3 object
    def test_returns_correct_byte_content(self, mocker):
        """
        Test that the function returns the correct byte content of the requested S3 object.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The returned content matches the expected byte content.
            - The returned content is of type `bytes`.
        """
        # Arrange
        mock_s3_client = mocker.Mock()
        expected_content = b"binary content \x00\x01\x02"
        mock_body = mocker.Mock()
        mock_body.read.return_value = expected_content
        mock_s3_client.get_object.return_value = {"Body": mock_body}

        # Act

        result = get_filebytes_from_s3(mock_s3_client, "bucket", "key")

        # Assert
        assert result == expected_content
        assert isinstance(result, bytes)

    # Properly uses the provided s3_client to make the get_object call
    def test_uses_provided_s3_client(self, mocker):
        """
        Test that the function properly uses the provided S3 client to make the `get_object` call.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The `get_object` method is called exactly once.
            - The `Bucket` and `Key` arguments in the call match the expected values.
        """
        # Arrange
        mock_s3_client = mocker.Mock()
        mock_response = {"Body": mocker.Mock()}
        mock_response["Body"].read.return_value = b"content"
        mock_s3_client.get_object.return_value = mock_response

        bucket_name = "test-bucket"
        s3_key = "test/file.txt"

        # Act

        get_filebytes_from_s3(mock_s3_client, bucket_name, s3_key)

        # Assert
        mock_s3_client.get_object.assert_called_once()
        call_args = mock_s3_client.get_object.call_args[1]
        assert call_args["Bucket"] == bucket_name
        assert call_args["Key"] == s3_key

    # Correctly extracts and returns the file content from the response Body
    def test_extracts_content_from_response_body(self, mocker):
        """
        Test that the function correctly extracts and returns the file content from the response body.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The `read` method of the response body is called exactly once.
            - The returned content matches the expected file bytes.
        """
        # Arrange
        mock_s3_client = mocker.Mock()
        mock_body = mocker.Mock()
        mock_body.read.return_value = b"extracted content"
        mock_s3_client.get_object.return_value = {"Body": mock_body}

        # Act

        result = get_filebytes_from_s3(mock_s3_client, "bucket", "key")

        # Assert
        mock_body.read.assert_called_once()
        assert result == b"extracted content"

    # Handles and re-raises ClientError with appropriate logging
    def test_handles_and_reraises_client_error(self, mocker):
        """
        Test that the function handles and re-raises `ClientError` with appropriate logging.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - A `ClientError` is raised with the expected error message.
            - The error is logged with the correct details.
        """
        # Arrange

        mock_s3_client = mocker.Mock()
        mock_error = ClientError(
            {"Error": {"Code": "NoSuchKey", "Message": "The object does not exist"}},
            "get_object",
        )
        mock_s3_client.get_object.side_effect = mock_error

        mock_logger = mocker.patch("shared_helpers.boto3_helpers.LOG")

        # Act & Assert

        with pytest.raises(ClientError) as excinfo:
            get_filebytes_from_s3(mock_s3_client, "bucket", "key")

        # Verify the same error is re-raised
        assert excinfo.value == mock_error

        # Verify logging
        mock_logger.error.assert_called_once_with(
            "ClientError while retrieving file <%s> from bucket <%s>: <%s>",
            "key",
            "bucket",
            mock_error,
        )

    # Handles and re-raises unexpected exceptions with appropriate logging
    def test_handles_and_reraises_unexpected_exceptions(self, mocker):
        """
        Test that the function handles and re-raises unexpected exceptions with appropriate logging.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The unexpected exception is raised with the expected error message.
            - The error is logged with the correct details.
        """
        # Arrange
        mock_s3_client = mocker.Mock()
        unexpected_error = ValueError("Unexpected error")
        mock_s3_client.get_object.side_effect = unexpected_error

        mock_logger = mocker.patch("shared_helpers.boto3_helpers.LOG")

        # Act & Assert

        with pytest.raises(ValueError) as excinfo:
            get_filebytes_from_s3(mock_s3_client, "bucket", "key")

        # Verify the same error is re-raised
        assert excinfo.value == unexpected_error

        # Verify logging
        mock_logger.error.assert_called_once_with(
            "Unexpected error while retrieving file <%s> from bucket <%s>: <%s>",
            "key",
            "bucket",
            unexpected_error,
        )

    # Behavior when bucket_name is empty string
    def test_empty_bucket_name(self, mocker):
        """
        Test the function's behavior when the `bucket_name` is an empty string.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - A `ClientError` is raised with the expected error message.
            - The error is logged with the correct details.
        """
        # Arrange

        mock_s3_client = mocker.Mock()
        mock_error = ClientError(
            {
                "Error": {
                    "Code": "InvalidBucketName",
                    "Message": "The specified bucket is not valid",
                }
            },
            "get_object",
        )
        mock_s3_client.get_object.side_effect = mock_error

        mock_logger = mocker.patch("shared_helpers.boto3_helpers.LOG")

        # Act & Assert

        with pytest.raises(ClientError) as excinfo:
            get_filebytes_from_s3(mock_s3_client, "", "key")

        # Verify the same error is re-raised
        assert excinfo.value == mock_error

        # Verify logging
        mock_logger.error.assert_called_once_with(
            "ClientError while retrieving file <%s> from bucket <%s>: <%s>",
            "key",
            "",
            mock_error,
        )

    # Behavior when s3_key is empty string
    def test_empty_s3_key(self, mocker):
        """
        Test the function's behavior when the `s3_key` is an empty string.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The `get_object` method is called with an empty `Key`.
            - The returned content is an empty byte string.
        """
        # Arrange
        mock_s3_client = mocker.Mock()
        mock_response = {"Body": mocker.Mock()}
        mock_response["Body"].read.return_value = b""  # Empty file content
        mock_s3_client.get_object.return_value = mock_response

        # Act

        result = get_filebytes_from_s3(mock_s3_client, "bucket", "")

        # Assert
        mock_s3_client.get_object.assert_called_once_with(Bucket="bucket", Key="")
        assert result == b""

    # Behavior when the S3 object doesn't exist
    def test_nonexistent_s3_object(self, mocker):
        """
        Test the function's behavior when the requested S3 object does not exist.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - A `ClientError` is raised with the expected error message.
            - The error is logged with the correct details.
        """
        # Arrange

        mock_s3_client = mocker.Mock()
        mock_error = ClientError(
            {
                "Error": {
                    "Code": "NoSuchKey",
                    "Message": "The specified key does not exist",
                }
            },
            "get_object",
        )
        mock_s3_client.get_object.side_effect = mock_error

        mock_logger = mocker.patch("shared_helpers.boto3_helpers.LOG")

        # Act & Assert

        with pytest.raises(ClientError) as excinfo:
            get_filebytes_from_s3(mock_s3_client, "bucket", "nonexistent-key")

        # Verify the same error is re-raised
        assert excinfo.value == mock_error

        # Verify logging
        mock_logger.error.assert_called_once_with(
            "ClientError while retrieving file <%s> from bucket <%s>: <%s>",
            "nonexistent-key",
            "bucket",
            mock_error,
        )

    # Behavior when the user lacks permissions to access the object
    def test_insufficient_permissions(self, mocker):
        """
        Test the function's behavior when the user lacks permissions to access the S3 object.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - A `ClientError` is raised with the expected error message.
            - The error is logged with the correct details.
        """
        # Arrange

        mock_s3_client = mocker.Mock()
        mock_error = ClientError(
            {"Error": {"Code": "AccessDenied", "Message": "Access Denied"}},
            "get_object",
        )
        mock_s3_client.get_object.side_effect = mock_error

        mock_logger = mocker.patch("shared_helpers.boto3_helpers.LOG")

        # Act & Assert

        with pytest.raises(ClientError) as excinfo:
            get_filebytes_from_s3(mock_s3_client, "bucket", "protected-key")

        # Verify the same error is re-raised
        assert excinfo.value == mock_error

        # Verify logging
        mock_logger.error.assert_called_once_with(
            "ClientError while retrieving file <%s> from bucket <%s>: <%s>",
            "protected-key",
            "bucket",
            mock_error,
        )

    # Handles large files appropriately
    def test_large_file_handling(self, mocker):
        """
        Test that the function handles large files appropriately.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The returned content matches the expected large file bytes.
        """
        # Mock the S3 client
        mock_s3_client = mocker.Mock()
        large_file_content = b"a" * 10**7  # 10 MB of data
        mock_s3_client.get_object.return_value = {
            "Body": mocker.Mock(read=mocker.Mock(return_value=large_file_content))
        }

        # Call the function
        result = get_filebytes_from_s3(mock_s3_client, "test-bucket", "large-file-key")

        # Assert the result is as expected
        assert result == large_file_content

    # Performance with different file types (text, binary, etc.)
    def test_performance_with_various_file_types(self, mocker):
        """
        Test the function's performance with different file types (e.g., text, binary).

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The returned content matches the expected file bytes for each file type.
        """
        # Mock the S3 client
        mock_s3_client = mocker.Mock()

        # Text file content
        text_content = b"Hello, World!"
        mock_s3_client.get_object.return_value = {
            "Body": mocker.Mock(read=mocker.Mock(return_value=text_content))
        }
        text_result = get_filebytes_from_s3(
            mock_s3_client, "test-bucket", "text-file-key"
        )
        assert text_result == text_content

        # Binary file content
        binary_content = b"\x00\x01\x02\x03"
        mock_s3_client.get_object.return_value = {
            "Body": mocker.Mock(read=mocker.Mock(return_value=binary_content))
        }
        binary_result = get_filebytes_from_s3(
            mock_s3_client, "test-bucket", "binary-file-key"
        )
        assert binary_result == binary_content
