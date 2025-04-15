"""
Module: test_fetch_values_from_ssm

This module contains unit tests for the `fetch_values_from_ssm` function in the
`shared_helpers.boto3_client_helpers` module. The `fetch_values_from_ssm` function
is responsible for retrieving parameter values from AWS Systems Manager (SSM) Parameter Store.

The tests in this module ensure that:
- Parameters are successfully fetched from SSM when valid keys are provided.
- Secure parameters are properly decrypted using `WithDecryption=True`.
- Missing or invalid keys are handled gracefully with appropriate warnings and exit codes.
- Errors such as `ClientError` and missing AWS credentials are handled correctly.
- The function provides helpful error messages for missing or invalid keys.

Dependencies:
- pytest: For test execution and assertions.
- mocker: For mocking dependencies and AWS client interactions.
- botocore.exceptions.ClientError: For simulating AWS client errors.
- shared_helpers.boto3_client_helpers.fetch_values_from_ssm: The function under test.

Test Cases:
- `test_successful_fetch_multiple_parameters`: Verifies successful retrieval of multiple parameters.
- `test_returns_dictionary_with_correct_structure`: Ensures the function returns a dictionary with parameter names as keys.
- `test_decrypts_secure_parameters`: Confirms secure parameters are decrypted with `WithDecryption=True`.
- `test_handles_empty_keys_list`: Ensures the function handles an empty list of keys gracefully.
- `test_handles_missing_or_invalid_keys`: Verifies handling of missing or invalid keys with warnings.
- `test_exits_with_code_42_for_invalid_parameters`: Ensures the function exits with code 42 for invalid parameters.
- `test_exits_with_code_1_for_client_error`: Verifies the function exits with code 1 when a `ClientError` occurs.
- `test_handles_improperly_initialized_client`: Handles cases where the SSM client is not properly initialized.
- `test_handles_missing_aws_credentials`: Ensures proper handling of missing AWS credentials.
- `test_provides_helpful_error_message_for_missing_keys`: Confirms the function provides helpful error messages for missing keys.
"""

import pytest
from botocore.exceptions import ClientError

from shared_helpers.boto3_client_helpers import fetch_values_from_ssm


class TestFetchValuesFromSsm:
    """
    Test suite for the `fetch_values_from_ssm` function.
    """

    # Successfully fetches multiple parameters from SSM when all keys exist
    def test_successful_fetch_multiple_parameters(self, mocker):
        """
        Test that multiple parameters are successfully fetched from SSM when all keys exist.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The returned dictionary contains the expected parameter names and values.
            - The `get_parameters` method of the SSM client is called with the correct arguments.
        """
        # Arrange
        mock_ssm_client = mocker.Mock()
        mock_ssm_client.get_parameters.return_value = {
            "Parameters": [
                {"Name": "key1", "Value": "value1"},
                {"Name": "key2", "Value": "value2"},
            ],
            "InvalidParameters": [],
        }
        ssm_keys = ["key1", "key2"]

        # Act
        result = fetch_values_from_ssm(mock_ssm_client, ssm_keys)

        # Assert
        assert result == {"key1": "value1", "key2": "value2"}
        mock_ssm_client.get_parameters.assert_called_once_with(
            Names=ssm_keys, WithDecryption=True
        )

    # Returns a dictionary with parameter names as keys and their values as values
    def test_returns_dictionary_with_correct_structure(self, mocker):
        """
        Test that the function returns a dictionary with parameter names as keys
        and their corresponding values as values.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The returned object is a dictionary.
            - The keys and values in the dictionary match the expected structure.
        """
        # Arrange
        mock_ssm_client = mocker.Mock()
        mock_ssm_client.get_parameters.return_value = {
            "Parameters": [
                {"Name": "param1", "Value": "value1"},
                {"Name": "param2", "Value": "value2"},
                {"Name": "param3", "Value": "value3"},
            ],
            "InvalidParameters": [],
        }
        ssm_keys = ["param1", "param2", "param3"]

        # Act
        result = fetch_values_from_ssm(mock_ssm_client, ssm_keys)

        # Assert
        assert isinstance(result, dict)
        assert list(result.keys()) == ["param1", "param2", "param3"]
        assert list(result.values()) == ["value1", "value2", "value3"]

    # Properly decrypts secure parameters with WithDecryption=True
    def test_decrypts_secure_parameters(self, mocker):
        """
        Test that secure parameters are properly decrypted using `WithDecryption=True`.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The returned dictionary contains the decrypted parameter values.
            - The `get_parameters` method is called with `WithDecryption=True`.
        """
        # Arrange
        mock_ssm_client = mocker.Mock()
        mock_ssm_client.get_parameters.return_value = {
            "Parameters": [{"Name": "secure_param", "Value": "decrypted_value"}],
            "InvalidParameters": [],
        }
        ssm_keys = ["secure_param"]

        # Act
        result = fetch_values_from_ssm(mock_ssm_client, ssm_keys)

        # Assert
        assert result == {"secure_param": "decrypted_value"}
        # Verify WithDecryption is set to True
        mock_ssm_client.get_parameters.assert_called_once_with(
            Names=ssm_keys, WithDecryption=True
        )

    # # Handles empty list of SSM keys gracefully
    def test_handles_empty_keys_list(self, mocker):
        """
        Test that the function handles an empty list of SSM keys gracefully.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The returned dictionary is empty.
            - The `get_parameters` method is called with an empty list of keys.
        """
        # Arrange
        mock_ssm_client = mocker.Mock()
        mock_ssm_client.get_parameters.return_value = {
            "Parameters": [],
            "InvalidParameters": [],
        }
        ssm_keys = []

        # Act
        result = fetch_values_from_ssm(mock_ssm_client, ssm_keys)

        # Assert
        assert result == {}
        mock_ssm_client.get_parameters.assert_called_once_with(
            Names=ssm_keys, WithDecryption=True
        )

    # Handles case when some SSM keys are missing or invalid
    def test_handles_missing_or_invalid_keys(self, mocker):
        """
        Test that the function handles missing or invalid keys gracefully by
        logging a warning and exiting with code 42.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - A warning is logged for missing or invalid keys.
            - The function exits with code 42.
        """
        # Arrange
        mock_ssm_client = mocker.Mock()
        mock_ssm_client.get_parameters.return_value = {
            "Parameters": [{"Name": "valid_key", "Value": "valid_value"}],
            "InvalidParameters": ["invalid_key"],
        }
        ssm_keys = ["valid_key", "invalid_key"]

        # Mock rich_print to prevent actual printing
        mock_rich_print = mocker.patch("shared_helpers.boto3_client_helpers.rich_print")
        # Mock sys.exit to prevent actual exit
        mock_exit = mocker.patch("shared_helpers.boto3_client_helpers.sys.exit")

        # Act
        fetch_values_from_ssm(mock_ssm_client, ssm_keys)

        # Assert
        mock_rich_print.assert_any_call(
            "Warning: The following SSM keys are missing or invalid: ['invalid_key']"
        )
        mock_exit.assert_called_once_with(42)

    # Exits with code 42 when invalid parameters are detected
    def test_exits_with_code_42_for_invalid_parameters(self, mocker):
        """
        Test that the function exits with code 42 when invalid parameters are detected.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The function exits with code 42.
        """
        # Arrange
        mock_ssm_client = mocker.Mock()
        mock_ssm_client.get_parameters.return_value = {
            "Parameters": [],
            "InvalidParameters": ["key1", "key2"],
        }
        ssm_keys = ["key1", "key2"]

        # Mock rich_print to prevent actual printing
        mock_rich_print = mocker.patch("shared_helpers.boto3_client_helpers.rich_print")
        # Mock sys.exit to prevent actual exit
        mock_exit = mocker.patch("shared_helpers.boto3_client_helpers.sys.exit")

        # Act
        fetch_values_from_ssm(mock_ssm_client, ssm_keys)

        # Assert
        mock_exit.assert_called_once_with(42)

    # Exits with code 1 when ClientError occurs
    def test_exits_with_code_1_for_client_error(self, mocker):
        """
        Test that the function exits with code 1 when a `ClientError` occurs.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - A critical error message is logged.
            - The function exits with code 1.
        """
        # Arrange
        mock_ssm_client = mocker.Mock()
        mock_ssm_client.get_parameters.side_effect = ClientError(
            {
                "Error": {
                    "Code": "InternalServerError",
                    "Message": "Internal server error",
                }
            },
            "GetParameters",
        )
        ssm_keys = ["key1", "key2"]

        # Mock rich_print to prevent actual printing
        mock_rich_print = mocker.patch("shared_helpers.boto3_client_helpers.rich_print")
        # Mock sys.exit to prevent actual exit
        mock_exit = mocker.patch("shared_helpers.boto3_client_helpers.sys.exit")

        # Act
        fetch_values_from_ssm(mock_ssm_client, ssm_keys)

        # Assert
        mock_rich_print.assert_called_once()
        mock_exit.assert_called_once_with(1)

    # Handles case when SSM client is not properly initialized
    def test_handles_improperly_initialized_client(self, mocker):
        """
        Test that the function handles cases where the SSM client is not properly initialized.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - An `AttributeError` is raised when the SSM client is improperly initialized.
        """
        # Arrange
        mock_ssm_client = mocker.Mock()
        mock_ssm_client.get_parameters.side_effect = AttributeError(
            "'NoneType' object has no attribute 'get_parameters'"
        )
        ssm_keys = ["key1"]

        # Mock rich_print to prevent actual printing
        mock_rich_print = mocker.patch("shared_helpers.boto3_client_helpers.rich_print")
        # Mock sys.exit to prevent actual exit
        mocker.patch("shared_helpers.boto3_client_helpers.sys.exit")

        # Act and Assert
        with pytest.raises(AttributeError):
            fetch_values_from_ssm(mock_ssm_client, ssm_keys)

    # Handles case when AWS credentials are not properly configured
    def test_handles_missing_aws_credentials(self, mocker):
        """
        Test that the function handles cases where AWS credentials are not properly configured.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - A critical error message is logged.
            - The function exits with code 1.
        """
        # Arrange
        mock_ssm_client = mocker.Mock()
        mock_ssm_client.get_parameters.side_effect = ClientError(
            {
                "Error": {
                    "Code": "InvalidClientTokenId",
                    "Message": "The security token included in the request is invalid",
                }
            },
            "GetParameters",
        )
        ssm_keys = ["key1"]

        # Mock rich_print to prevent actual printing
        mock_rich_print = mocker.patch("shared_helpers.boto3_client_helpers.rich_print")
        # Mock sys.exit to prevent actual exit
        mock_exit = mocker.patch("shared_helpers.boto3_client_helpers.sys.exit")

        # Act
        fetch_values_from_ssm(mock_ssm_client, ssm_keys)

        # Assert
        mock_rich_print.assert_called_once()
        assert "Error fetching parameters from SSM" in mock_rich_print.call_args[0][0]
        mock_exit.assert_called_once_with(1)

    # Provides helpful error message when keys are missing
    def test_provides_helpful_error_message_for_missing_keys(self, mocker):
        """
        Test that the function provides a helpful error message when keys are missing.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - A warning message is logged for missing keys.
            - A helpful message about setting the `AWS_REGION` environment variable is logged.
            - The function exits with code 42.
        """
        # Arrange
        mock_ssm_client = mocker.Mock()
        mock_ssm_client.get_parameters.return_value = {
            "Parameters": [],
            "InvalidParameters": ["missing_key1", "missing_key2"],
        }
        ssm_keys = ["missing_key1", "missing_key2"]

        # Mock rich_print to prevent actual printing
        mock_rich_print = mocker.patch("shared_helpers.boto3_client_helpers.rich_print")
        # Mock sys.exit to prevent actual exit
        mock_exit = mocker.patch("shared_helpers.boto3_client_helpers.sys.exit")

        # Act
        fetch_values_from_ssm(mock_ssm_client, ssm_keys)

        # Assert
        # Check first call contains warning about missing keys
        assert (
            "Warning: The following SSM keys are missing or invalid"
            in mock_rich_print.call_args_list[0][0][0]
        )
        # Check second call contains helpful message about AWS_REGION
        assert "export AWS_REGION" in mock_rich_print.call_args_list[1][0][0]
        mock_exit.assert_called_once_with(42)
