"""
Module: test_check_bucket_exists

This module contains unit tests for the `check_bucket_exists` function in the
`shared_helpers.boto3_helpers` module. The `check_bucket_exists` function is responsible
for verifying the existence of an S3 bucket and handling various scenarios such as
non-existent buckets, access denial, and other errors.

The tests in this module ensure that:
- The function correctly verifies the existence of an S3 bucket.
- Proper logging is performed for successful and failed bucket checks.
- Appropriate exceptions are raised for different error scenarios, including:
  - Non-existent buckets (404 errors).
  - Access denial (403 errors).
  - Other ClientErrors and runtime issues.
- The function handles invalid parameters gracefully.

Dependencies:
- pytest: For test execution and assertions.
- mocker: For mocking dependencies and AWS client interactions.
- botocore.exceptions.ClientError: For simulating AWS client errors.
- shared_helpers.boto3_helpers.check_bucket_exists: The function under test.

Test Cases:
- `test_bucket_exists_success`: Verifies that the function correctly identifies an existing bucket.
- `test_logs_info_when_bucket_exists`: Ensures that an info log is generated when the bucket exists.
- `test_returns_none_when_bucket_exists`: Confirms that the function implicitly returns `None` for existing buckets.
- `test_boto3_client_interaction`: Validates that the function interacts with the boto3 client as expected.
- `test_bucket_does_not_exist`: Tests the behavior when the bucket does not exist (404 error).
- `test_access_denied_to_bucket`: Tests the behavior when access to the bucket is denied (403 error).
- `test_other_client_error`: Handles other ClientErrors with different error codes.
- `test_invalid_bucket_name`: Ensures the function raises an error for invalid or `None` bucket names.
- `test_invalid_s3_client`: Ensures the function raises an error for invalid or `None` S3 clients.
- `test_network_timeout`: Simulates network timeout or connection issues and verifies the behavior.
"""

import pytest
from botocore.exceptions import ClientError

from shared_helpers.boto3_helpers import check_bucket_exists


class TestCheckBucketExists:
    """
    Test suite for the `check_bucket_exists` function.
    """

    # Successfully verifies an existing bucket with proper permissions
    def test_bucket_exists_success(self, mocker):
        """
        Test that the function successfully verifies an existing bucket with proper permissions.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The S3 client's `head_bucket` method is called with the correct bucket name.
            - An info log is generated indicating the bucket exists.
            - The function returns `None` for existing buckets.
        """
        # Arrange
        mock_s3_client = mocker.Mock()
        mock_s3_client.head_bucket.return_value = {}
        bucket_name = "test-bucket"
        mock_log = mocker.patch("shared_helpers.boto3_helpers.LOG")

        # Act
        result = check_bucket_exists(mock_s3_client, bucket_name)

        # Assert
        mock_s3_client.head_bucket.assert_called_once_with(Bucket=bucket_name)
        mock_log.info.assert_called_once_with(
            "Verified bucket <%s> exists", bucket_name
        )
        assert result is None

    # Logs an info message when bucket exists
    def test_logs_info_when_bucket_exists(self, mocker):
        """
        Test that the function logs an info message when the bucket exists.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - An info log is generated with the correct bucket name.
        """
        # Arrange
        mock_s3_client = mocker.Mock()
        mock_s3_client.head_bucket.return_value = {}
        bucket_name = "test-bucket"
        mock_log = mocker.patch("shared_helpers.boto3_helpers.LOG")

        # Act
        check_bucket_exists(mock_s3_client, bucket_name)

        # Assert
        mock_log.info.assert_called_once_with(
            "Verified bucket <%s> exists", bucket_name
        )

    # Returns None when bucket exists (implicit return)
    def test_returns_none_when_bucket_exists(self, mocker):
        """
        Test that the function implicitly returns `None` when the bucket exists.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The function returns `None` for existing buckets.
        """
        # Arrange
        mock_s3_client = mocker.Mock()
        mock_s3_client.head_bucket.return_value = {}
        bucket_name = "test-bucket"
        mocker.patch("shared_helpers.boto3_helpers.LOG")

        # Act
        result = check_bucket_exists(mock_s3_client, bucket_name)

        # Assert
        assert result is None

    # Correctly handles the boto3 client interaction
    def test_boto3_client_interaction(self, mocker):
        """
        Test that the function correctly interacts with the boto3 client.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The S3 client's `head_bucket` method is called with the correct bucket name.
        """
        # Arrange
        mock_s3_client = mocker.Mock()
        mock_s3_client.head_bucket.return_value = {}
        bucket_name = "test-bucket"
        mocker.patch("shared_helpers.boto3_helpers.LOG")

        # Act
        check_bucket_exists(mock_s3_client, bucket_name)

        # Assert
        mock_s3_client.head_bucket.assert_called_once_with(Bucket=bucket_name)

    # Bucket does not exist (404 error)
    def test_bucket_does_not_exist(self, mocker):
        """
        Test that the function raises a `ValueError` when the bucket does not exist (404 error).

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - A `ValueError` is raised with the expected error message.
            - A critical log is generated indicating the bucket does not exist.
        """
        # Arrange
        mock_s3_client = mocker.Mock()
        bucket_name = "non-existent-bucket"
        error_response = {"Error": {"Code": "404"}}
        mock_s3_client.head_bucket.side_effect = ClientError(
            error_response, "HeadBucket"
        )
        mock_log = mocker.patch("shared_helpers.boto3_helpers.LOG")
        mocker.patch("shared_helpers.boto3_helpers.safeget", return_value="404")

        # Act & Assert
        with pytest.raises(ValueError) as excinfo:
            check_bucket_exists(mock_s3_client, bucket_name)

        assert f"S3 bucket <{bucket_name}> does not exist" in str(excinfo.value)
        mock_log.critical.assert_called_once_with(
            "S3 bucket <%s> does not exist", bucket_name
        )

    # Access denied to bucket (403 error)
    def test_access_denied_to_bucket(self, mocker):
        """
        Test that the function raises a `PermissionError` when access to the bucket is denied (403 error).

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - A `PermissionError` is raised with the expected error message.
            - A critical log is generated indicating access denial.
        """
        # Arrange
        mock_s3_client = mocker.Mock()
        bucket_name = "forbidden-bucket"
        error_response = {"Error": {"Code": "403"}}
        mock_s3_client.head_bucket.side_effect = ClientError(
            error_response, "HeadBucket"
        )
        mock_log = mocker.patch("shared_helpers.boto3_helpers.LOG")
        mocker.patch("shared_helpers.boto3_helpers.safeget", return_value="403")

        # Act & Assert
        with pytest.raises(PermissionError) as excinfo:
            check_bucket_exists(mock_s3_client, bucket_name)

        assert f"Access denied to S3 bucket <{bucket_name}>" in str(excinfo.value)
        mock_log.critical.assert_called_once_with(
            "Access denied to S3 bucket <%s>", bucket_name
        )

    # Other ClientError with different error code
    def test_other_client_error(self, mocker):
        """
        Test that the function raises a `RuntimeError` for other ClientErrors with different error codes.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - A `RuntimeError` is raised with the expected error message.
            - A critical log is generated indicating the failure.
        """
        # Arrange
        mock_s3_client = mocker.Mock()
        bucket_name = "error-bucket"
        error_response = {"Error": {"Code": "500"}}
        mock_error = ClientError(error_response, "HeadBucket")
        mock_s3_client.head_bucket.side_effect = mock_error
        mock_log = mocker.patch("shared_helpers.boto3_helpers.LOG")
        mocker.patch("shared_helpers.boto3_helpers.safeget", return_value="500")

        # Act & Assert
        with pytest.raises(RuntimeError) as excinfo:
            check_bucket_exists(mock_s3_client, bucket_name)

        assert f"Failed to verify S3 bucket <{bucket_name}>" in str(excinfo.value)
        mock_log.critical.assert_called_once_with(
            "Failed to verify S3 bucket <%s>: <%s>", bucket_name, mock_error
        )

    # Invalid or None bucket_name parameter
    def test_invalid_bucket_name(self, mocker):
        """
        Test that the function raises a `TypeError` for invalid or `None` bucket names.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - A `TypeError` is raised with the expected error message.
        """
        # Arrange
        mock_s3_client = mocker.Mock()
        bucket_name = None
        mock_s3_client.head_bucket.side_effect = TypeError(
            "NoneType object has no attribute"
        )
        mocker.patch("shared_helpers.boto3_helpers.LOG")

        # Act & Assert
        with pytest.raises(TypeError):
            check_bucket_exists(mock_s3_client, bucket_name)

        # Verify the head_bucket was called with None
        mock_s3_client.head_bucket.assert_called_once_with(Bucket=None)

    # Invalid or None s3_client parameter
    def test_invalid_s3_client(self, mocker):
        """
        Test that the function raises an `AttributeError` for invalid or `None` S3 clients.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - An `AttributeError` is raised with the expected error message.
        """
        # Arrange
        s3_client = None
        bucket_name = "test-bucket"
        mocker.patch("shared_helpers.boto3_helpers.LOG")

        # Act & Assert
        with pytest.raises(AttributeError):
            check_bucket_exists(s3_client, bucket_name)

    # Network timeout or connection issues
    def test_network_timeout(self, mocker):
        """
        Test that the function raises a `RuntimeError` for network timeout or connection issues.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - A `RuntimeError` is raised with the expected error message.
            - A critical log is generated indicating the failure.
        """
        # Arrange
        mock_s3_client = mocker.Mock()
        bucket_name = "timeout-bucket"
        connection_error = ClientError(
            {"Error": {"Code": "RequestTimeout"}}, "HeadBucket"
        )
        mock_s3_client.head_bucket.side_effect = connection_error
        mock_log = mocker.patch("shared_helpers.boto3_helpers.LOG")
        mocker.patch(
            "shared_helpers.boto3_helpers.safeget", return_value="RequestTimeout"
        )

        # Act & Assert
        with pytest.raises(RuntimeError) as excinfo:
            check_bucket_exists(mock_s3_client, bucket_name)

        assert f"Failed to verify S3 bucket <{bucket_name}>" in str(excinfo.value)
        mock_log.critical.assert_called_once_with(
            "Failed to verify S3 bucket <%s>: <%s>", bucket_name, connection_error
        )
