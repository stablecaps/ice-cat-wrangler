"""
Module: test_gen_boto3_session

This module contains unit tests for the `gen_boto3_session` function in the
`shared_helpers.boto3_helpers` module. The `gen_boto3_session` function is responsible
for creating a boto3 session using AWS credentials and region information from
environment variables.

The tests in this module ensure that:
- A boto3 session is successfully created when all required environment variables are set.
- The function correctly uses environment variables for AWS credentials and region.
- The function handles cases where some or all environment variables are missing.
- The function handles invalid AWS credentials and region names gracefully.
- The function behaves correctly when environment variables contain empty strings.

Dependencies:
- pytest: For test execution and assertions.
- pytest-mock: For mocking dependencies and environment variables.
- boto3: For creating AWS sessions.
- botocore.exceptions: For simulating AWS client errors.
- shared_helpers.boto3_helpers.gen_boto3_session: The function under test.

Test Cases:
- `test_returns_boto3_session_with_all_env_vars`: Verifies that a boto3 session is created when all environment variables are set.
- `test_uses_environment_variables_correctly`: Ensures the function correctly uses environment variables for AWS credentials and region.
- `test_session_created_with_correct_access_key`: Verifies that the session is created with the correct AWS access key ID.
- `test_session_created_with_correct_secret_key`: Verifies that the session is created with the correct AWS secret access key.
- `test_session_created_with_correct_session_token`: Verifies that the session is created with the correct AWS session token.
- `test_works_with_partial_environment_variables`: Ensures the function works when some environment variables are not set.
- `test_works_with_no_environment_variables`: Ensures the function works when no environment variables are set.
- `test_handles_empty_string_environment_variables`: Verifies the function's behavior when environment variables contain empty strings.
- `test_handles_invalid_aws_credentials`: Ensures the function raises a `NoCredentialsError` for invalid AWS credentials.
- `test_handles_invalid_region_name`: Ensures the function raises an `InvalidRegionError` for invalid region names.
"""

import os

import pytest
from botocore.exceptions import InvalidRegionError, NoCredentialsError

from shared_helpers.boto3_helpers import gen_boto3_session


class TestGenBoto3Session:
    """
    Test suite for the `gen_boto3_session` function.
    """

    # Function returns a boto3.Session object when all environment variables are set
    def test_returns_boto3_session_with_all_env_vars(self, mocker):
        """
        Test that a boto3 session is created when all required environment variables are set.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The `boto3.Session` method is called with the correct arguments.
            - The returned session matches the mocked session.
        """
        # Arrange
        mock_env = {
            "AWS_ACCESS_KEY_ID": "test_access_key",
            "AWS_SECRET_ACCESS_KEY": "test_secret_key",
            "AWS_SESSION_TOKEN": "test_session_token",
            "AWS_REGION": "us-west-2",
        }
        mocker.patch.dict(os.environ, mock_env)
        mock_session = mocker.patch("boto3.Session")

        # Act
        result = gen_boto3_session()

        # Assert
        mock_session.assert_called_once_with(
            aws_access_key_id="test_access_key",
            aws_secret_access_key="test_secret_key",
            aws_session_token="test_session_token",
            region_name="us-west-2",
        )
        assert result == mock_session.return_value

    # Function correctly uses environment variables for AWS credentials and region
    def test_uses_environment_variables_correctly(self, mocker):
        """
        Test that the function correctly uses environment variables for AWS credentials and region.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The `os.getenv` method is called for each required environment variable.
            - The `boto3.Session` method is called with the correct arguments.
        """
        # Arrange
        mock_env = {
            "AWS_ACCESS_KEY_ID": "test_access_key",
            "AWS_SECRET_ACCESS_KEY": "test_secret_key",
            "AWS_SESSION_TOKEN": "test_session_token",
            "AWS_REGION": "eu-central-1",
        }
        mocker.patch.dict(os.environ, mock_env)
        mock_getenv = mocker.patch(
            "os.getenv", side_effect=lambda key: mock_env.get(key)
        )
        mock_session = mocker.patch("boto3.Session")

        # Act
        gen_boto3_session()

        # Assert
        assert mock_getenv.call_count == 4
        mock_getenv.assert_any_call("AWS_ACCESS_KEY_ID")
        mock_getenv.assert_any_call("AWS_SECRET_ACCESS_KEY")
        mock_getenv.assert_any_call("AWS_SESSION_TOKEN")
        mock_getenv.assert_any_call("AWS_REGION")

    # Session is created with the correct AWS access key ID from environment
    def test_session_created_with_correct_access_key(self, mocker):
        """
        Test that the session is created with the correct AWS access key ID from environment variables.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The `aws_access_key_id` argument in the `boto3.Session` call matches the expected value.
        """
        # Arrange
        expected_access_key = "AKIAIOSFODNN7EXAMPLE"
        mocker.patch.dict(os.environ, {"AWS_ACCESS_KEY_ID": expected_access_key})
        mock_session = mocker.patch("boto3.Session")

        # Act
        gen_boto3_session()

        # Assert
        called_kwargs = mock_session.call_args.kwargs
        assert called_kwargs["aws_access_key_id"] == expected_access_key

    # Session is created with the correct AWS secret access key from environment
    def test_session_created_with_correct_secret_key(self, mocker):
        """
        Test that the session is created with the correct AWS secret access key from environment variables.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The `aws_secret_access_key` argument in the `boto3.Session` call matches the expected value.
        """
        # Arrange
        expected_secret_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
        mocker.patch.dict(os.environ, {"AWS_SECRET_ACCESS_KEY": expected_secret_key})
        mock_session = mocker.patch("boto3.Session")

        # Act
        gen_boto3_session()

        # Assert
        called_kwargs = mock_session.call_args.kwargs
        assert called_kwargs["aws_secret_access_key"] == expected_secret_key

    # Session is created with the correct AWS session token from environment
    def test_session_created_with_correct_session_token(self, mocker):
        """
        Test that the session is created with the correct AWS session token from environment variables.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The `aws_session_token` argument in the `boto3.Session` call matches the expected value.
        """
        # Arrange
        expected_session_token = "AQoEXAMPLEH4aoAH0gNCAPyJxz4BlCFFxWNE1OPTgk5TthT+"
        mocker.patch.dict(os.environ, {"AWS_SESSION_TOKEN": expected_session_token})
        mock_session = mocker.patch("boto3.Session")

        # Act
        gen_boto3_session()

        # Assert
        called_kwargs = mock_session.call_args.kwargs
        assert called_kwargs["aws_session_token"] == expected_session_token

    # Function works when some environment variables are not set
    def test_works_with_partial_environment_variables(self, mocker):
        """
        Test that the function works when some environment variables are not set.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The `boto3.Session` method is called with `None` for missing environment variables.
        """
        # Arrange
        mock_env = {
            "AWS_ACCESS_KEY_ID": "test_access_key",
            "AWS_SECRET_ACCESS_KEY": "test_secret_key",
            # AWS_SESSION_TOKEN and AWS_REGION not set
        }
        mocker.patch.dict(os.environ, mock_env, clear=True)
        mock_session = mocker.patch("boto3.Session")

        # Act
        result = gen_boto3_session()

        # Assert
        mock_session.assert_called_once_with(
            aws_access_key_id="test_access_key",
            aws_secret_access_key="test_secret_key",
            aws_session_token=None,
            region_name=None,
        )
        assert result == mock_session.return_value

    # Function works when all environment variables are not set
    def test_works_with_no_environment_variables(self, mocker):
        """
        Test that the function works when no environment variables are set.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The `boto3.Session` method is called with `None` for all arguments.
        """
        # Arrange
        mocker.patch.dict(os.environ, {}, clear=True)
        mock_session = mocker.patch("boto3.Session")

        # Act
        result = gen_boto3_session()

        # Assert
        mock_session.assert_called_once_with(
            aws_access_key_id=None,
            aws_secret_access_key=None,
            aws_session_token=None,
            region_name=None,
        )
        assert result == mock_session.return_value

    # Function behavior when environment variables contain empty strings
    def test_handles_empty_string_environment_variables(self, mocker):
        """
        Test that the function handles empty string values in environment variables.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The `boto3.Session` method is called with empty strings for the corresponding arguments.
        """
        # Arrange
        mock_env = {
            "AWS_ACCESS_KEY_ID": "",
            "AWS_SECRET_ACCESS_KEY": "",
            "AWS_SESSION_TOKEN": "",
            "AWS_REGION": "",
        }
        mocker.patch.dict(os.environ, mock_env)
        mock_session = mocker.patch("boto3.Session")

        # Act
        result = gen_boto3_session()

        # Assert
        mock_session.assert_called_once_with(
            aws_access_key_id="",
            aws_secret_access_key="",
            aws_session_token="",
            region_name="",
        )
        assert result == mock_session.return_value

    # Function behavior with invalid AWS credentials in environment variables
    def test_handles_invalid_aws_credentials(self, mocker):
        """
        Test that `gen_boto3_session` raises a `NoCredentialsError` when invalid AWS credentials are provided.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - A `NoCredentialsError` is raised when invalid credentials are used.
        """
        # Arrange
        mock_env = {
            "AWS_ACCESS_KEY_ID": "invalid_key",
            "AWS_SECRET_ACCESS_KEY": "invalid_secret",
            "AWS_SESSION_TOKEN": "invalid_token",
            "AWS_REGION": "us-west-2",
        }
        mocker.patch.dict(os.environ, mock_env)
        mock_session = mocker.patch("boto3.Session")
        mock_session.side_effect = NoCredentialsError()

        # Act & Assert
        with pytest.raises(NoCredentialsError):
            gen_boto3_session()

    # Function behavior with invalid region name in environment variables
    def test_handles_invalid_region_name(self, mocker):
        """
        Test that the function raises an `InvalidRegionError` when an invalid region name is provided.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - An `InvalidRegionError` is raised with the expected error message.
        """
        # Arrange
        mock_env = {
            "AWS_ACCESS_KEY_ID": "test_access_key",
            "AWS_SECRET_ACCESS_KEY": "test_secret_key",
            "AWS_SESSION_TOKEN": "test_session_token",
            "AWS_REGION": "invalid-region-123",
        }
        mocker.patch.dict(os.environ, mock_env)
        mock_session = mocker.patch("boto3.Session")
        mock_session.side_effect = InvalidRegionError(region_name="invalid-region-123")

        # Act & Assert
        with pytest.raises(InvalidRegionError):
            gen_boto3_session()
