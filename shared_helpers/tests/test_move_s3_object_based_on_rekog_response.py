"""
Module: test_move_s3_object_based_on_rekog_response

This module contains unit tests for the `move_s3_object_based_on_rekog_response` function in the
`shared_helpers.boto3_helpers` module. The `move_s3_object_based_on_rekog_response` function is responsible
for moving an object from a source S3 bucket to either a destination bucket or a failure bucket based on
the operation status (`op_status`) provided.

The tests in this module ensure that:
- The function successfully moves objects to the destination bucket when the operation status is "success".
- The function moves objects to the failure bucket when the operation status is not "success".
- The function correctly applies the specified ACL during the copy operation.
- The function handles exceptions such as `ClientError` and unexpected errors gracefully.
- The function logs appropriate messages for successful and failed operations.
- The function processes objects correctly even when they do not exist in the source bucket.

Dependencies:
- pytest: For test execution and assertions.
- pytest-mock: For mocking dependencies and S3 client behavior.
- botocore.exceptions: For simulating AWS client errors.
- shared_helpers.boto3_helpers.move_s3_object_based_on_rekog_response: The function under test.

Test Cases:
- `test_moves_to_destination_when_success`: Verifies that the function moves the object to the destination bucket when `op_status` is "success".
- `test_moves_to_failure_bucket_when_not_success`: Ensures the function moves the object to the failure bucket when `op_status` is not "success".
- `test_copies_with_correct_acl_before_delete`: Verifies that the function applies the correct ACL during the copy operation and deletes the object from the source bucket.
- `test_returns_true_on_successful_move`: Ensures the function returns `True` when the object is successfully moved.
- `test_logs_info_message_after_successful_move`: Verifies that the function logs an appropriate information message after a successful move.
- `test_handles_client_error_during_copy`: Ensures the function handles `ClientError` during the `copy_object` operation and logs the error.
- `test_handles_client_error_during_delete`: Ensures the function handles `ClientError` during the `delete_object` operation and logs the error.
- `test_handles_unexpected_exceptions`: Verifies that the function handles unexpected exceptions during the move operation and logs the error.
- `test_reraises_exceptions_after_logging`: Ensures the function re-raises exceptions after logging them.
- `test_handles_nonexistent_s3_key`: Verifies that the function handles cases where the `s3_key` does not exist in the source bucket.
"""

import pytest
from botocore.exceptions import ClientError

from shared_helpers.boto3_helpers import (
    DEFAULT_S3_ACL,
    move_s3_object_based_on_rekog_response,
)


class TestMoveS3ObjectBasedOnRekogResponse:
    """
    Test suite for the `move_s3_object_based_on_rekog_response` function.
    """

    # Successfully moves object to destination bucket when op_status is "success"
    def test_moves_to_destination_when_success(self, mocker):
        """
        Test that the function moves the object to the destination bucket when `op_status` is "success".

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The `copy_object` method is called with the correct parameters.
            - The `delete_object` method is called with the correct parameters.
            - The function returns `True`.
        """
        # Arrange
        mock_s3_client = mocker.Mock()
        op_status = "success"
        s3bucket_source = "source-bucket"
        s3bucket_dest = "destination-bucket"
        s3bucket_fail = "failure-bucket"
        s3_key = "test/image.jpg"

        # Act
        result = move_s3_object_based_on_rekog_response(
            mock_s3_client,
            op_status,
            s3bucket_source,
            s3bucket_dest,
            s3bucket_fail,
            s3_key,
        )

        # Assert
        mock_s3_client.copy_object.assert_called_once_with(
            CopySource={"Bucket": s3bucket_source, "Key": s3_key},
            Bucket=s3bucket_dest,
            Key=s3_key,
            ACL=DEFAULT_S3_ACL,
        )
        mock_s3_client.delete_object.assert_called_once_with(
            Bucket=s3bucket_source, Key=s3_key
        )
        assert result is True

    # Successfully moves object to failure bucket when op_status is not "success"
    def test_moves_to_failure_bucket_when_not_success(self, mocker):
        """
        Test that the function moves the object to the failure bucket when `op_status` is not "success".

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The `copy_object` method is called with the correct parameters for the failure bucket.
            - The `delete_object` method is called with the correct parameters.
            - The function returns `True`.
        """
        # Arrange
        mock_s3_client = mocker.Mock()
        op_status = "failure"
        s3bucket_source = "source-bucket"
        s3bucket_dest = "destination-bucket"
        s3bucket_fail = "failure-bucket"
        s3_key = "test/image.jpg"

        # Act
        result = move_s3_object_based_on_rekog_response(
            mock_s3_client,
            op_status,
            s3bucket_source,
            s3bucket_dest,
            s3bucket_fail,
            s3_key,
        )

        # Assert
        mock_s3_client.copy_object.assert_called_once_with(
            CopySource={"Bucket": s3bucket_source, "Key": s3_key},
            Bucket=s3bucket_fail,
            Key=s3_key,
            ACL=DEFAULT_S3_ACL,
        )
        mock_s3_client.delete_object.assert_called_once_with(
            Bucket=s3bucket_source, Key=s3_key
        )
        assert result is True

    # Correctly copies object with specified ACL before deleting from source
    def test_copies_with_correct_acl_before_delete(self, mocker):
        """
        Test that the function applies the correct ACL during the copy operation and deletes the object from the source bucket.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The `copy_object` method is called with the correct ACL.
            - The `delete_object` method is called after the `copy_object` method.
        """
        # Arrange
        mock_s3_client = mocker.Mock()
        op_status = "success"
        s3bucket_source = "source-bucket"
        s3bucket_dest = "destination-bucket"
        s3bucket_fail = "failure-bucket"
        s3_key = "test/image.jpg"

        # Act
        move_s3_object_based_on_rekog_response(
            mock_s3_client,
            op_status,
            s3bucket_source,
            s3bucket_dest,
            s3bucket_fail,
            s3_key,
        )

        # Assert
        # Verify copy_object is called with correct ACL
        mock_s3_client.copy_object.assert_called_once_with(
            CopySource={"Bucket": s3bucket_source, "Key": s3_key},
            Bucket=s3bucket_dest,
            Key=s3_key,
            ACL=DEFAULT_S3_ACL,
        )

        # Verify delete_object is called with correct parameters
        mock_s3_client.delete_object.assert_called_once_with(
            Bucket=s3bucket_source, Key=s3_key
        )

        # Verify the order of operations: copy first, then delete
        assert mock_s3_client.mock_calls[0] == mocker.call.copy_object(
            CopySource={"Bucket": s3bucket_source, "Key": s3_key},
            Bucket=s3bucket_dest,
            Key=s3_key,
            ACL=DEFAULT_S3_ACL,
        )
        assert mock_s3_client.mock_calls[1] == mocker.call.delete_object(
            Bucket=s3bucket_source, Key=s3_key
        )

    # Returns True when object is successfully moved
    def test_returns_true_on_successful_move(self, mocker):
        """
        Test that the function returns `True` when the object is successfully moved.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The function returns `True`.
        """
        # Arrange
        mock_s3_client = mocker.Mock()
        op_status = "success"
        s3bucket_source = "source-bucket"
        s3bucket_dest = "destination-bucket"
        s3bucket_fail = "failure-bucket"
        s3_key = "test/image.jpg"

        # Act
        result = move_s3_object_based_on_rekog_response(
            mock_s3_client,
            op_status,
            s3bucket_source,
            s3bucket_dest,
            s3bucket_fail,
            s3_key,
        )

        # Assert
        assert result is True

    # Logs appropriate information message after successful move
    def test_logs_info_message_after_successful_move(self, mocker):
        """
        Test that the function logs an appropriate information message after a successful move.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The `info` method of the logger is called with the correct message.
        """
        # Arrange
        mock_s3_client = mocker.Mock()
        mock_logger = mocker.patch("shared_helpers.boto3_helpers.LOG")
        op_status = "success"
        s3bucket_source = "source-bucket"
        s3bucket_dest = "destination-bucket"
        s3bucket_fail = "failure-bucket"
        s3_key = "test/image.jpg"

        # Act
        move_s3_object_based_on_rekog_response(
            mock_s3_client,
            op_status,
            s3bucket_source,
            s3bucket_dest,
            s3bucket_fail,
            s3_key,
        )

        # Assert
        mock_logger.info.assert_called_once_with(
            "Moved object <%s> to <%s>", s3_key, s3bucket_dest
        )

    # Handles ClientError during copy_object operation
    def test_handles_client_error_during_copy(self, mocker):
        """
        Test that the function handles `ClientError` during the `copy_object` operation and logs the error.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The `error` method of the logger is called with the correct message.
            - The `delete_object` method is not called.
        """
        # Arrange
        mock_s3_client = mocker.Mock()
        mock_logger = mocker.patch("shared_helpers.boto3_helpers.LOG")
        op_status = "success"
        s3bucket_source = "source-bucket"
        s3bucket_dest = "destination-bucket"
        s3bucket_fail = "failure-bucket"
        s3_key = "test/image.jpg"

        # Configure copy_object to raise ClientError
        client_error = ClientError(
            {"Error": {"Code": "NoSuchBucket", "Message": "The bucket does not exist"}},
            "CopyObject",
        )
        mock_s3_client.copy_object.side_effect = client_error

        # Act & Assert
        with pytest.raises(ClientError) as excinfo:
            move_s3_object_based_on_rekog_response(
                mock_s3_client,
                op_status,
                s3bucket_source,
                s3bucket_dest,
                s3bucket_fail,
                s3_key,
            )

        # Verify the error is logged
        mock_logger.error.assert_called_once_with(
            "Error moving object %s: %s", s3_key, client_error
        )

        # Verify delete_object was not called
        mock_s3_client.delete_object.assert_not_called()

    # Handles ClientError during delete_object operation
    def test_handles_client_error_during_delete(self, mocker):
        """
        Test that the function handles `ClientError` during the `delete_object` operation and logs the error.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The `error` method of the logger is called with the correct message.
            - The `copy_object` method is called with the correct parameters.
        """
        # Arrange
        mock_s3_client = mocker.Mock()
        mock_logger = mocker.patch("shared_helpers.boto3_helpers.LOG")
        op_status = "success"
        s3bucket_source = "source-bucket"
        s3bucket_dest = "destination-bucket"
        s3bucket_fail = "failure-bucket"
        s3_key = "test/image.jpg"

        # Configure delete_object to raise ClientError
        client_error = ClientError(
            {"Error": {"Code": "AccessDenied", "Message": "Access Denied"}},
            "DeleteObject",
        )
        mock_s3_client.delete_object.side_effect = client_error

        # Act & Assert
        with pytest.raises(ClientError) as excinfo:
            move_s3_object_based_on_rekog_response(
                mock_s3_client,
                op_status,
                s3bucket_source,
                s3bucket_dest,
                s3bucket_fail,
                s3_key,
            )

        # Verify the error is logged
        mock_logger.error.assert_called_once_with(
            "Error moving object %s: %s", s3_key, client_error
        )

        # Verify copy_object was called
        mock_s3_client.copy_object.assert_called_once()

    # Handles unexpected exceptions during the move operation
    def test_handles_unexpected_exceptions(self, mocker):
        """
        Test that the function handles unexpected exceptions during the move operation and logs the error.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The `error` method of the logger is called with the correct message.
            - The exception is re-raised.
        """
        # Arrange
        mock_s3_client = mocker.Mock()
        mock_logger = mocker.patch("shared_helpers.boto3_helpers.LOG")
        op_status = "success"
        s3bucket_source = "source-bucket"
        s3bucket_dest = "destination-bucket"
        s3bucket_fail = "failure-bucket"
        s3_key = "test/image.jpg"

        # Configure copy_object to raise an unexpected exception
        unexpected_error = ValueError("Unexpected error")
        mock_s3_client.copy_object.side_effect = unexpected_error

        # Act & Assert
        with pytest.raises(ValueError) as excinfo:
            move_s3_object_based_on_rekog_response(
                mock_s3_client,
                op_status,
                s3bucket_source,
                s3bucket_dest,
                s3bucket_fail,
                s3_key,
            )

        # Verify the error is logged
        mock_logger.error.assert_called_once_with(
            "Unexpected error while handling Rekognition response: %s", unexpected_error
        )

    # Properly re-raises exceptions after logging them
    def test_reraises_exceptions_after_logging(self, mocker):
        """
        Test that the function re-raises exceptions after logging them.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The exception is re-raised after being logged.
        """
        # Arrange
        mock_s3_client = mocker.Mock()
        mocker.patch("shared_helpers.boto3_helpers.LOG")
        op_status = "success"
        s3bucket_source = "source-bucket"
        s3bucket_dest = "destination-bucket"
        s3bucket_fail = "failure-bucket"
        s3_key = "test/image.jpg"

        # Test cases with different exceptions
        test_exceptions = [
            ClientError(
                {
                    "Error": {
                        "Code": "NoSuchBucket",
                        "Message": "The bucket does not exist",
                    }
                },
                "CopyObject",
            ),
            ValueError("Unexpected error"),
            KeyError("Missing key"),
        ]

        for exception in test_exceptions:
            mock_s3_client.copy_object.side_effect = exception

            # Act & Assert
            with pytest.raises(type(exception)) as excinfo:
                move_s3_object_based_on_rekog_response(
                    mock_s3_client,
                    op_status,
                    s3bucket_source,
                    s3bucket_dest,
                    s3bucket_fail,
                    s3_key,
                )

            # Verify the exception is the same one that was raised
            assert excinfo.value is exception

    # Behavior when s3_key doesn't exist in source bucket
    def test_handles_nonexistent_s3_key(self, mocker):
        """
        Test that the function handles cases where the `s3_key` does not exist in the source bucket.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The `error` method of the logger is called with the correct message.
            - The `delete_object` method is not called.
        """
        # Arrange
        mock_s3_client = mocker.Mock()
        mock_logger = mocker.patch("shared_helpers.boto3_helpers.LOG")
        op_status = "success"
        s3bucket_source = "source-bucket"
        s3bucket_dest = "destination-bucket"
        s3bucket_fail = "failure-bucket"
        s3_key = "nonexistent/image.jpg"

        # Configure copy_object to raise NoSuchKey error
        client_error = ClientError(
            {
                "Error": {
                    "Code": "NoSuchKey",
                    "Message": "The specified key does not exist.",
                }
            },
            "CopyObject",
        )
        mock_s3_client.copy_object.side_effect = client_error

        # Act & Assert
        with pytest.raises(ClientError) as excinfo:
            move_s3_object_based_on_rekog_response(
                mock_s3_client,
                op_status,
                s3bucket_source,
                s3bucket_dest,
                s3bucket_fail,
                s3_key,
            )

        # Verify the error is logged
        mock_logger.error.assert_called_once_with(
            "Error moving object %s: %s", s3_key, client_error
        )

        # Verify delete_object was not called
        mock_s3_client.delete_object.assert_not_called()
