"""
Module: test_load_environment_variables

This module contains unit tests for the `load_environment_variables` function in the
`api_client.helpers.config` module. The `load_environment_variables` function is responsible
for loading environment variables from either a dotenv file or AWS SSM Parameter Store.

The tests in this module ensure that:
- The function correctly loads environment variables from SSM when `secretsfile` is "ssm".
- The function correctly loads environment variables from a dotenv file when `secretsfile` is not "ssm".
- The function sets environment variables correctly after loading.
- The function handles edge cases such as missing or invalid SSM parameters, non-existent dotenv files, and malformed dotenv files.
- The function prints debug information when the `debug` flag is set to `True`.

Dependencies:
- pytest: For test execution and assertions.
- unittest.mock: For mocking dependencies and environment variables.
- api_client.helpers.config.load_environment_variables: The function under test.

Test Cases:
- `test_load_from_ssm`: Verifies that the function loads environment variables from SSM when `secretsfile` is "ssm".
- `test_load_from_dotenv_file`: Ensures the function loads environment variables from a dotenv file when `secretsfile` is not "ssm".
- `test_setting_env_vars_from_ssm`: Verifies that the function sets environment variables correctly after loading from SSM.
- `test_successful_dotenv_loading`: Ensures the function sets environment variables correctly after loading from a dotenv file.
- `test_debug_output`: Verifies that the function prints debug information when the `debug` flag is set to `True`.
- `test_handling_missing_ssm_parameters`: Ensures the function handles missing SSM parameters gracefully.
- `test_handling_invalid_ssm_parameters`: Verifies that the function handles invalid SSM parameters and raises an appropriate exception.
- `test_handling_nonexistent_dotenv_file`: Ensures the function handles non-existent dotenv files gracefully.
- `test_handling_malformed_dotenv_file`: Verifies that the function handles empty or malformed dotenv files gracefully.
- `test_handling_missing_required_env_vars`: Ensures the function handles missing required environment variables after loading.
"""

import os

import pytest
from botocore.exceptions import ClientError

from api_client.helpers.config import load_environment_variables


class TestLoadEnvironmentVariables:
    """
    Test suite for the `load_environment_variables` function.
    """

    # Loading environment variables from SSM when secretsfile is "ssm"
    def test_load_from_ssm(self, mocker):
        """
        Test that the function loads environment variables from SSM when `secretsfile` is "ssm".

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The `fetch_values_from_ssm` function is called with the correct parameters.
            - The environment variables are set correctly after loading.
        """
        # Arrange
        mock_ssm_client = mocker.Mock()
        mock_fetch = mocker.patch(
            "api_client.helpers.config.fetch_values_from_ssm",
            return_value={
                "prefix/AWS_ACCESS_KEY_ID": "test_key",
                "prefix/AWS_SECRET_ACCESS_KEY": "test_secret",
                "prefix/AWS_REGION": "us-west-2",
            },
        )
        mocker.patch("api_client.helpers.config.ssm_client", mock_ssm_client)
        mocker.patch("api_client.helpers.config.check_env_variables", return_value=True)
        mocker.patch(
            "api_client.helpers.config.ssm_keys",
            [
                "prefix/AWS_ACCESS_KEY_ID",
                "prefix/AWS_SECRET_ACCESS_KEY",
                "prefix/AWS_REGION",
            ],
        )

        # Act
        load_environment_variables("ssm")

        # Assert
        mock_fetch.assert_called_once_with(
            mock_ssm_client,
            [
                "prefix/AWS_ACCESS_KEY_ID",
                "prefix/AWS_SECRET_ACCESS_KEY",
                "prefix/AWS_REGION",
            ],
        )
        assert os.environ.get("AWS_ACCESS_KEY_ID") == "test_key"
        assert os.environ.get("AWS_SECRET_ACCESS_KEY") == "test_secret"
        assert os.environ.get("AWS_REGION") == "us-west-2"

    # Loading environment variables from a dotenv file when secretsfile is not "ssm"
    def test_load_from_dotenv_file(self, mocker):
        """
        Test that the function loads environment variables from a dotenv file when `secretsfile` is not "ssm".

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The `construct_secrets_path` function is called with the correct filename.
            - The `load_dotenv` function is called with the correct path.
        """
        # Arrange
        mock_construct_path = mocker.patch(
            "api_client.helpers.config.construct_secrets_path",
            return_value="/path/to/.env",
        )
        mock_load_dotenv = mocker.patch("api_client.helpers.config.load_dotenv")
        mocker.patch("api_client.helpers.config.check_env_variables", return_value=True)

        # Act
        load_environment_variables("dev.env")

        # Assert
        mock_construct_path.assert_called_once_with(secret_filename="dev.env")
        mock_load_dotenv.assert_called_once_with("/path/to/.env", override=True)

    # Successfully setting environment variables from SSM parameters
    def test_setting_env_vars_from_ssm(self, mocker):
        """
        Test that the function sets environment variables correctly after loading from SSM.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The environment variables are set correctly for each key-value pair.
        """
        # Arrange
        ssm_response = {
            "prefix/AWS_ACCESS_KEY_ID": "test_key",
            "prefix/AWS_SECRET_ACCESS_KEY": "test_secret",
            "prefix/AWS_REGION": "us-west-2",
            "prefix/FUNC_BULKIMG_ANALYSER_NAME": "test_func",
            "prefix/S3BUCKET_SOURCE": "test_bucket",
            "prefix/DYNAMODB_TABLE_NAME": "test_table",
        }
        mocker.patch(
            "api_client.helpers.config.fetch_values_from_ssm", return_value=ssm_response
        )
        mocker.patch("api_client.helpers.config.check_env_variables", return_value=True)
        mocker.patch("api_client.helpers.config.ssm_keys", list(ssm_response.keys()))

        # Act
        load_environment_variables("ssm")

        # Assert
        for key, value in ssm_response.items():
            env_key = key.split("/")[-1]
            assert os.environ.get(env_key) == value

    # Successfully loading environment variables from dotenv file
    def test_successful_dotenv_loading(self, mocker):
        """
        Test that the function sets environment variables correctly after loading from a dotenv file.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The environment variables are set correctly for each key-value pair.
        """
        # Arrange
        mock_construct_path = mocker.patch(
            "api_client.helpers.config.construct_secrets_path",
            return_value="/path/to/.env",
        )

        # Mock load_dotenv to set environment variables
        def mock_load_dotenv_effect(path, override):
            os.environ["AWS_ACCESS_KEY_ID"] = "dotenv_key"
            os.environ["AWS_SECRET_ACCESS_KEY"] = "dotenv_secret"
            os.environ["AWS_REGION"] = "eu-west-1"
            os.environ["FUNC_BULKIMG_ANALYSER_NAME"] = "dotenv_func"
            os.environ["S3BUCKET_SOURCE"] = "dotenv_bucket"
            os.environ["DYNAMODB_TABLE_NAME"] = "dotenv_table"
            return True

        mock_load_dotenv = mocker.patch(
            "api_client.helpers.config.load_dotenv", side_effect=mock_load_dotenv_effect
        )
        mocker.patch("api_client.helpers.config.check_env_variables", return_value=True)

        # Act
        load_environment_variables("dev.env")

        # Assert
        assert os.environ.get("AWS_ACCESS_KEY_ID") == "dotenv_key"
        assert os.environ.get("AWS_SECRET_ACCESS_KEY") == "dotenv_secret"
        assert os.environ.get("AWS_REGION") == "eu-west-1"
        assert os.environ.get("FUNC_BULKIMG_ANALYSER_NAME") == "dotenv_func"
        assert os.environ.get("S3BUCKET_SOURCE") == "dotenv_bucket"
        assert os.environ.get("DYNAMODB_TABLE_NAME") == "dotenv_table"

    # Printing debug information when debug flag is True
    def test_debug_output(self, mocker):
        """
        Test that the function prints debug information when the `debug` flag is set to `True`.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - Debug information is printed for each environment variable.
        """
        # Arrange
        mocker.patch(
            "api_client.helpers.config.fetch_values_from_ssm",
            return_value={
                "prefix/AWS_ACCESS_KEY_ID": "test_key",
                "prefix/AWS_SECRET_ACCESS_KEY": "test_secret",
            },
        )
        mocker.patch("api_client.helpers.config.check_env_variables", return_value=True)
        mocker.patch(
            "api_client.helpers.config.ssm_keys",
            ["prefix/AWS_ACCESS_KEY_ID", "prefix/AWS_SECRET_ACCESS_KEY"],
        )
        mocker.patch(
            "api_client.helpers.config.secret_vars",
            ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"],
        )
        mock_print = mocker.patch("api_client.helpers.config.print")

        # Act
        load_environment_variables("ssm", debug=True)

        # Assert
        debug_calls = [
            call
            for call in mock_print.call_args_list
            if "Retrieved env vars" in str(call)
        ]
        assert len(debug_calls) > 0
        assert mock_print.call_count > 3  # At least a few debug prints should happen

    # Handling missing SSM parameters
    def test_handling_missing_ssm_parameters(self, mocker):
        """
        Test that the function handles missing SSM parameters gracefully.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The function raises a `SystemExit` exception with the correct exit code.
        """
        # Arrange
        mocker.patch(
            "api_client.helpers.config.fetch_values_from_ssm",
            side_effect=SystemExit(42),
        )
        mocker.patch("api_client.helpers.config.ssm_keys", ["prefix/MISSING_KEY"])

        # Act & Assert
        with pytest.raises(SystemExit) as excinfo:
            load_environment_variables("ssm")

        assert excinfo.value.code == 42

    # Handling invalid SSM parameters
    def test_handling_invalid_ssm_parameters(self, mocker):
        """
        Test that the function handles invalid SSM parameters and raises an appropriate exception.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The function raises a `SystemExit` exception with the correct exit code.
        """
        # Arrange
        # Simulate ClientError from boto3
        mock_error = ClientError(
            {"Error": {"Code": "InvalidParameter", "Message": "Parameter not found"}},
            "GetParameters",
        )
        mocker.patch(
            "api_client.helpers.config.fetch_values_from_ssm", side_effect=mock_error
        )
        mocker.patch("api_client.helpers.config.ssm_keys", ["prefix/INVALID_KEY"])

        # Act & Assert
        with pytest.raises(SystemExit) as excinfo:
            load_environment_variables("ssm")

        assert excinfo.value.code == 1

    # Handling non-existent dotenv file path
    def test_handling_nonexistent_dotenv_file(self, mocker):
        """
        Test that the function handles non-existent dotenv files gracefully.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The function raises a `SystemExit` exception with the correct exit code.
        """
        # Arrange
        mocker.patch(
            "api_client.helpers.config.construct_secrets_path",
            side_effect=SystemExit(1),
        )

        # Act & Assert
        with pytest.raises(SystemExit) as excinfo:
            load_environment_variables("nonexistent.env")

        assert excinfo.value.code == 1

    # Handling empty or malformed dotenv file
    def test_handling_malformed_dotenv_file(self, mocker):
        """
        Test that the function handles empty or malformed dotenv files gracefully.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The function raises a `SystemExit` exception with the correct exit code.
        """
        # Arrange
        mocker.patch(
            "api_client.helpers.config.construct_secrets_path",
            return_value="/path/to/empty.env",
        )
        mocker.patch(
            "api_client.helpers.config.load_dotenv", return_value=False
        )  # load_dotenv returns False if file is empty or malformed
        mocker.patch(
            "api_client.helpers.config.check_env_variables", return_value=False
        )  # No env vars were loaded

        # Act & Assert
        with pytest.raises(SystemExit) as excinfo:
            load_environment_variables("empty.env")

        assert excinfo.value.code == 1

    # Handling missing required environment variables after loading
    def test_handling_missing_required_env_vars(self, mocker):
        """
        Test that the function handles missing required environment variables after loading.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The function raises a `SystemExit` exception with the correct exit code.
        """
        # Arrange
        mocker.patch(
            "api_client.helpers.config.construct_secrets_path",
            return_value="/path/to/.env",
        )
        mocker.patch("api_client.helpers.config.load_dotenv")
        mocker.patch(
            "api_client.helpers.config.check_env_variables", return_value=False
        )  # Simulate missing required env vars

        # Act & Assert
        with pytest.raises(SystemExit) as excinfo:
            load_environment_variables("dev.env")

        assert excinfo.value.code == 1
