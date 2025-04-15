"""
Module: test_copy_s3_object

This module contains unit tests for the `copy_s3_object` function in the
`shared_helpers.boto3_helpers` module. The `copy_s3_object` function is responsible
for copying objects between S3 buckets and handling various scenarios such as
non-existent buckets, missing object keys, and insufficient permissions.

The tests in this module ensure that:
- Objects are successfully copied between S3 buckets with the correct parameters.
- Default and custom ACL values are applied correctly.
- Proper logging is performed for successful and failed copy operations.
- Appropriate exceptions are raised for different error scenarios, including:
  - Non-existent source or destination buckets.
  - Missing object keys.
  - Insufficient permissions for source or destination buckets.

Dependencies:
- pytest: For test execution and assertions.
- mocker: For mocking dependencies and AWS client interactions.
- botocore.exceptions.ClientError: For simulating AWS client errors.
- shared_helpers.boto3_helpers.copy_s3_object: The function under test.

Test Cases:
- `test_successful_copy`: Verifies that an object is successfully copied between buckets.
- `test_default_acl_used`: Ensures the default ACL is applied when no custom ACL is provided.
- `test_successful_copy_logs_info`: Confirms that a successful copy operation logs an info message.
- `test_returns_none_on_success`: Ensures the function returns `None` on successful copy.
- `test_custom_acl_parameter`: Verifies that a custom ACL value is passed correctly.
- `test_nonexistent_source_bucket`: Handles the case where the source bucket does not exist.
- `test_nonexistent_destination_bucket`: Handles the case where the destination bucket does not exist.
- `test_nonexistent_object_key`: Handles the case where the object key does not exist.
- `test_insufficient_permissions_source`: Handles insufficient permissions for the source bucket.
- `test_insufficient_permissions_destination`: Handles insufficient permissions for the destination bucket.
"""

import pytest
from botocore.exceptions import ClientError

from shared_helpers.boto3_helpers import DEFAULT_S3_ACL, copy_s3_object


class TestCopyS3Object:
    """
    Test suite for the `copy_s3_object` function.
    """

    # Successfully copy an object from source bucket to destination bucket
    def test_successful_copy(self, mocker):
        """
        Test that an object is successfully copied from the source bucket to the destination bucket.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The `copy_object` method of the S3 client is called with the correct parameters.
        """
        # Arrange
        mock_s3_client = mocker.Mock()
        source_bucket = "source-bucket"
        dest_bucket = "dest-bucket"
        s3_key = "test/object.txt"

        # Act
        copy_s3_object(mock_s3_client, source_bucket, dest_bucket, s3_key)

        # Assert
        mock_s3_client.copy_object.assert_called_once_with(
            CopySource={"Bucket": source_bucket, "Key": s3_key},
            Bucket=dest_bucket,
            Key=s3_key,
            ACL=DEFAULT_S3_ACL,
        )

    # Use default ACL value when not explicitly provided
    def test_default_acl_used(self, mocker):
        """
        Test that the default ACL value is used when no custom ACL is provided.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The `ACL` parameter in the `copy_object` call matches the default ACL value.
        """
        # Arrange
        mock_s3_client = mocker.Mock()
        source_bucket = "source-bucket"
        dest_bucket = "dest-bucket"
        s3_key = "test/object.txt"

        # Act
        copy_s3_object(mock_s3_client, source_bucket, dest_bucket, s3_key)

        # Assert
        mock_s3_client.copy_object.assert_called_once()
        call_kwargs = mock_s3_client.copy_object.call_args[1]
        assert call_kwargs["ACL"] == DEFAULT_S3_ACL

    # Log successful copy operation with appropriate message
    def test_successful_copy_logs_info(self, mocker):
        """
        Test that a successful copy operation logs an info message.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - An info log message is generated with the correct details of the copy operation.
        """
        # Arrange
        mock_s3_client = mocker.Mock()
        source_bucket = "source-bucket"
        dest_bucket = "dest-bucket"
        s3_key = "test/object.txt"
        mock_logger = mocker.patch("shared_helpers.boto3_helpers.LOG")

        # Act
        copy_s3_object(mock_s3_client, source_bucket, dest_bucket, s3_key)

        # Assert
        mock_logger.info.assert_called_once_with(
            "Object <%s> copied from <%s> to %s", s3_key, source_bucket, dest_bucket
        )

    # Return None when copy operation succeeds
    def test_returns_none_on_success(self, mocker):
        """
        Test that the function returns `None` when the copy operation succeeds.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The function returns `None` on successful copy.
        """
        # Arrange
        mock_s3_client = mocker.Mock()
        source_bucket = "source-bucket"
        dest_bucket = "dest-bucket"
        s3_key = "test/object.txt"

        # Act
        result = copy_s3_object(mock_s3_client, source_bucket, dest_bucket, s3_key)

        # Assert
        assert result is None

    # Pass custom ACL parameter to override default value
    def test_custom_acl_parameter(self, mocker):
        """
        Test that a custom ACL value is passed correctly to the `copy_object` method.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The `ACL` parameter in the `copy_object` call matches the custom ACL value.
        """
        # Arrange
        mock_s3_client = mocker.Mock()
        source_bucket = "source-bucket"
        dest_bucket = "dest-bucket"
        s3_key = "test/object.txt"
        custom_acl = "public-read"

        # Act
        copy_s3_object(
            mock_s3_client, source_bucket, dest_bucket, s3_key, acl=custom_acl
        )

        # Assert
        mock_s3_client.copy_object.assert_called_once_with(
            CopySource={"Bucket": source_bucket, "Key": s3_key},
            Bucket=dest_bucket,
            Key=s3_key,
            ACL=custom_acl,
        )

    # Handle non-existent source bucket
    def test_nonexistent_source_bucket(self, mocker):
        """
        Test that a `ClientError` is raised when the source bucket does not exist.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - A `ClientError` is raised with the expected error message.
            - An error log message is generated indicating the failure.
        """
        # Arrange
        mock_s3_client = mocker.Mock()
        source_bucket = "nonexistent-source"
        dest_bucket = "dest-bucket"
        s3_key = "test/object.txt"

        error_response = {
            "Error": {
                "Code": "NoSuchBucket",
                "Message": "The specified bucket does not exist",
            }
        }
        mock_s3_client.copy_object.side_effect = ClientError(
            error_response, "CopyObject"
        )
        mock_logger = mocker.patch("shared_helpers.boto3_helpers.LOG")

        # Act & Assert
        with pytest.raises(ClientError):
            copy_s3_object(mock_s3_client, source_bucket, dest_bucket, s3_key)

        mock_logger.error.assert_called_once()

    # Handle non-existent destination bucket
    def test_nonexistent_destination_bucket(self, mocker):
        """
        Test that a `ClientError` is raised when the destination bucket does not exist.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - A `ClientError` is raised with the expected error message.
            - An error log message is generated indicating the failure.
        """
        # Arrange
        mock_s3_client = mocker.Mock()
        source_bucket = "source-bucket"
        dest_bucket = "nonexistent-dest"
        s3_key = "test/object.txt"

        error_response = {
            "Error": {
                "Code": "NoSuchBucket",
                "Message": "The specified bucket does not exist",
            }
        }
        mock_s3_client.copy_object.side_effect = ClientError(
            error_response, "CopyObject"
        )
        mock_logger = mocker.patch("shared_helpers.boto3_helpers.LOG")

        # Act & Assert
        with pytest.raises(ClientError):
            copy_s3_object(mock_s3_client, source_bucket, dest_bucket, s3_key)

        mock_logger.error.assert_called_once_with(
            "Error copying object <%s> from <%s> to %s: %s",
            s3_key,
            source_bucket,
            dest_bucket,
            mock_s3_client.copy_object.side_effect,
        )

    # Handle non-existent object key
    def test_nonexistent_object_key(self, mocker):
        """
        Test that a `ClientError` is raised when the object key does not exist.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - A `ClientError` is raised with the expected error message.
            - An error log message is generated indicating the failure.
        """
        # Arrange
        mock_s3_client = mocker.Mock()
        source_bucket = "source-bucket"
        dest_bucket = "dest-bucket"
        s3_key = "nonexistent/key.txt"

        error_response = {
            "Error": {
                "Code": "NoSuchKey",
                "Message": "The specified key does not exist",
            }
        }
        mock_s3_client.copy_object.side_effect = ClientError(
            error_response, "CopyObject"
        )
        mock_logger = mocker.patch("shared_helpers.boto3_helpers.LOG")

        # Act & Assert
        with pytest.raises(ClientError):
            copy_s3_object(mock_s3_client, source_bucket, dest_bucket, s3_key)

        mock_logger.error.assert_called_once()

    # Handle insufficient permissions for source bucket
    def test_insufficient_permissions_source(self, mocker):
        """
        Test that a `ClientError` is raised when there are insufficient permissions for the source bucket.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - A `ClientError` is raised with the expected error message.
            - An error log message is generated indicating the failure.
        """
        # Arrange
        mock_s3_client = mocker.Mock()
        source_bucket = "source-bucket"
        dest_bucket = "dest-bucket"
        s3_key = "test/object.txt"

        error_response = {"Error": {"Code": "AccessDenied", "Message": "Access Denied"}}
        mock_s3_client.copy_object.side_effect = ClientError(
            error_response, "CopyObject"
        )
        mock_logger = mocker.patch("shared_helpers.boto3_helpers.LOG")

        # Act & Assert
        with pytest.raises(ClientError):
            copy_s3_object(mock_s3_client, source_bucket, dest_bucket, s3_key)

        mock_logger.error.assert_called_once_with(
            "Error copying object <%s> from <%s> to %s: %s",
            s3_key,
            source_bucket,
            dest_bucket,
            mock_s3_client.copy_object.side_effect,
        )

    # Handle insufficient permissions for destination bucket
    def test_insufficient_permissions_destination(self, mocker):
        """
        Test that a `ClientError` is raised when there are insufficient permissions for the destination bucket.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - A `ClientError` is raised with the expected error message.
            - An error log message is generated indicating the failure.
        """
        # Arrange
        mock_s3_client = mocker.Mock()
        source_bucket = "source-bucket"
        dest_bucket = "restricted-dest"
        s3_key = "test/object.txt"

        error_response = {"Error": {"Code": "AccessDenied", "Message": "Access Denied"}}
        mock_s3_client.copy_object.side_effect = ClientError(
            error_response, "CopyObject"
        )
        mock_logger = mocker.patch("shared_helpers.boto3_helpers.LOG")

        # Act & Assert
        with pytest.raises(ClientError):
            copy_s3_object(mock_s3_client, source_bucket, dest_bucket, s3_key)

        mock_logger.error.assert_called_once()
        mock_s3_client.copy_object.assert_called_once()
