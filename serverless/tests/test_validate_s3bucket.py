"""
Module: test_validate_s3bucket

This module contains unit tests for the `validate_s3bucket` function in the
`serverless.functions.fhelpers` module. The `validate_s3bucket` function is responsible
for validating the existence of S3 buckets and retrieving their names from environment variables.

The tests in this module ensure that:
- The function correctly retrieves bucket names from environment variables.
- The function validates the existence of the specified S3 buckets.
- Proper error handling is implemented for missing environment variables or non-existent buckets.

Dependencies:
- pytest: For test execution and assertions.
- mocker: For mocking dependencies and environment variables.
- serverless.functions.fhelpers.validate_s3bucket: The function under test.
- shared_helpers.boto3_helpers.check_bucket_exists: Mocked to simulate bucket existence checks.

Fixtures:
- `mock_aws_clients`: Provides mocked AWS clients for S3, Rekognition, and DynamoDB.

"""

import pytest
from boto3_helpers import LOG

from serverless.functions.fhelpers import validate_s3bucket
from serverless.tests.conftest import bucket_names


class TestValidateS3bucket:
    """
    Test suite for the `validate_s3bucket` function.
    """

    # Returns a tuple of three bucket names when all environment variables are set and buckets exist
    def test_returns_bucket_names_when_all_vars_set(self, mocker, mock_aws_clients):
        """
        Test that `validate_s3bucket` returns a tuple of bucket names when all
        environment variables are set and the buckets exist.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.
            mock_aws_clients: The fixture providing mocked AWS clients.

        Asserts:
            - The returned bucket names match the expected values.
        """
        # Arrange
        s3_client_mock, _, _ = mock_aws_clients

        mocker.patch("shared_helpers.boto3_helpers.check_bucket_exists")

        # Act
        result = validate_s3bucket(s3_client_mock)

        # Assert
        assert result == ("source-bucket", "dest-bucket", "fail-bucket")

    # Successfully calls check_bucket_exists for each bucket in the environment list
    def test_calls_check_bucket_exists_for_each_bucket(self, mocker, mock_aws_clients):
        """
        Test that `validate_s3bucket` calls `check_bucket_exists` for each bucket
        in the environment variable list.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.
            mock_aws_clients: The fixture providing mocked AWS clients.

        Asserts:
            - `check_bucket_exists` is called exactly three times.
            - Each call is made with the correct bucket name.
        """
        # Arrange
        s3_client_mock, _, _ = mock_aws_clients

        check_bucket_mock = mocker.patch(
            "serverless.functions.fhelpers.check_bucket_exists"
        )

        # Act
        validate_s3bucket(s3_client_mock)

        # Assert
        assert check_bucket_mock.call_count == 3
        for bucket in bucket_names.values():
            check_bucket_mock.assert_any_call(
                s3_client=s3_client_mock, bucket_name=bucket
            )

    # Properly retrieves environment variables using os.getenv
    def test_retrieves_correct_environment_variables(self, mocker, mock_aws_clients):
        """
        Test that `validate_s3bucket` retrieves the correct environment variables
        using `os.getenv`.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.
            mock_aws_clients: The fixture providing mocked AWS clients.

        Asserts:
            - `os.getenv` is called with the correct environment variable names.
        """
        # Arrange
        s3_client_mock, _, _ = mock_aws_clients
        getenv_mock = mocker.patch("os.getenv")
        mocker.patch("serverless.functions.fhelpers.check_bucket_exists")

        # Act
        validate_s3bucket(s3_client_mock)

        # Assert
        getenv_mock.assert_has_calls(
            [
                mocker.call("s3bucketSource"),
                mocker.call("s3bucketDest"),
                mocker.call("s3bucketFail"),
            ]
        )

    # Exits with code 42 when any environment variable is None
    def test_exits_when_env_var_is_none(self, mocker, mock_aws_clients):
        """
        Test that `validate_s3bucket` exits with code 42 when any environment
        variable is not set.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.
            mock_aws_clients: The fixture providing mocked AWS clients.

        Asserts:
            - `sys.exit` is called with the exit code 42.
        """
        # Arrange
        s3_client_mock, _, _ = mock_aws_clients
        mocker.patch("os.getenv", side_effect=["source-bucket", None, "fail-bucket"])
        sys_exit_mock = mocker.patch("sys.exit")

        # Act
        validate_s3bucket(s3_client_mock)

        # Assert
        sys_exit_mock.assert_called_once_with(42)

    # Logs critical error when environment variables are unset
    def test_logs_critical_error_when_env_vars_unset(self, mocker, mock_aws_clients):
        """
        Test that `validate_s3bucket` logs a critical error when environment
        variables are unset.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.
            mock_aws_clients: The fixture providing mocked AWS clients.

        Asserts:
            - A critical log message is generated indicating unset environment variables.
        """
        # Arrange
        s3_client_mock, _, _ = mock_aws_clients
        env_vars = ["source-bucket", None, "fail-bucket"]
        mocker.patch("os.getenv", side_effect=env_vars)
        mocker.patch("sys.exit")
        log_mock = mocker.patch.object(LOG, "critical")

        # Act
        validate_s3bucket(s3_client_mock)

        # Assert
        log_mock.assert_called_once()
        assert "env vars are unset" in log_mock.call_args[0][0]
        assert str(tuple(env_vars)) in str(log_mock.call_args[0][1])

    # Behavior when check_bucket_exists raises an exception
    def test_propagates_exception_from_check_bucket_exists(
        self, mocker, mock_aws_clients
    ):
        """
        Test that `validate_s3bucket` propagates exceptions raised by
        `check_bucket_exists`.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.
            mock_aws_clients: The fixture providing mocked AWS clients.

        Asserts:
            - An exception is raised when `check_bucket_exists` fails.
            - The exception message matches the expected error.
        """
        # Arrange
        s3_client_mock, _, _ = mock_aws_clients

        check_bucket_mock = mocker.patch(
            "serverless.functions.fhelpers.check_bucket_exists"
        )  # Correct import path
        check_bucket_mock.side_effect = Exception("Bucket does not exist")

        # Act & Assert
        with pytest.raises(Exception) as excinfo:
            validate_s3bucket(s3_client_mock)

        assert "Bucket does not exist" in str(excinfo.value)
