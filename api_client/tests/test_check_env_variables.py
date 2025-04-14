import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))


import pytest

from api_client.helpers.config import check_env_variables, secret_vars


class TestCheckEnvVariables:

    # All required environment variables are set and function returns True
    def test_all_env_variables_set_returns_true(self, mocker):
        # Arrange
        mock_environ = {}
        for secret in secret_vars:
            mock_environ[secret] = "test_value"

        mocker.patch.dict("os.environ", mock_environ, clear=True)
        mocker.patch("builtins.print")

        # Act
        result = check_env_variables()

        # Assert
        assert result is True
        assert not print.called

    # Function correctly identifies when all secret_vars are present in os.environ
    def test_identifies_all_secret_vars_present(self, mocker):
        # Arrange
        mock_environ = {
            "AWS_ACCESS_KEY_ID": "test_key",
            "AWS_SECRET_ACCESS_KEY": "test_secret",
            "AWS_REGION": "us-west-2",
            "FUNC_BULKIMG_ANALYSER_NAME": "test_function",
            "S3BUCKET_SOURCE": "test_bucket",
            "DYNAMODB_TABLE_NAME": "test_table",
        }

        mocker.patch.dict("os.environ", mock_environ, clear=True)
        mocker.patch("builtins.print")

        # Act
        result = check_env_variables()

        # Assert
        assert result is True

    # Function returns the correct boolean value based on environment variable presence
    def test_returns_correct_boolean_value(self, mocker):
        # Arrange
        # Test with missing variable
        mock_environ = {var: "value" for var in secret_vars if var != "AWS_REGION"}
        mocker.patch.dict("os.environ", mock_environ, clear=True)
        mocker.patch("builtins.print")

        # Act
        result_missing = check_env_variables()

        # Add the missing variable
        mock_environ["AWS_REGION"] = "us-east-1"
        mocker.patch.dict("os.environ", mock_environ, clear=True)

        # Act again
        result_complete = check_env_variables()

        # Assert
        assert result_missing is False
        assert result_complete is True

    # Function works with the predefined secret_vars list from the config module
    def test_works_with_predefined_secret_vars(self, mocker):
        # Arrange
        mock_environ = {}
        for secret in secret_vars:
            mock_environ[secret] = "test_value"

        # Add some extra environment variables that aren't in secret_vars
        mock_environ["EXTRA_VAR"] = "extra"
        mock_environ["ANOTHER_VAR"] = "another"

        mocker.patch.dict("os.environ", mock_environ, clear=True)
        mocker.patch("builtins.print")

        # Act
        result = check_env_variables()

        # Assert
        assert result is True

        # Remove one secret var to verify it's actually checking the predefined list
        del mock_environ["AWS_REGION"]
        mocker.patch.dict("os.environ", mock_environ, clear=True)

        # Act again
        result_missing = check_env_variables()

        # Assert
        assert result_missing is False

    # No environment variables are set, function returns False
    def test_no_env_variables_set_returns_false(self, mocker):
        # Arrange
        mocker.patch.dict("os.environ", {}, clear=True)
        mock_print = mocker.patch("api_client.helpers.config.print")

        # Act
        result = check_env_variables()

        # Assert
        assert result is False
        assert mock_print.call_count == len(secret_vars)

    # Only some environment variables are set, function returns False
    def test_some_env_variables_set_returns_false(self, mocker):
        # Arrange
        # Set only half of the required variables
        half_index = len(secret_vars) // 2
        mock_environ = {secret_vars[i]: f"value_{i}" for i in range(half_index)}

        mocker.patch.dict("os.environ", mock_environ, clear=True)
        mock_print = mocker.patch("api_client.helpers.config.print")

        # Act
        result = check_env_variables()

        # Assert
        assert result is False
        assert mock_print.call_count == len(secret_vars) - half_index

    # Environment variables are set but with empty values
    def test_env_variables_with_empty_values(self, mocker):
        # Arrange
        mock_environ = {secret: "" for secret in secret_vars}

        mocker.patch.dict("os.environ", mock_environ, clear=True)
        mocker.patch("builtins.print")

        # Act
        result = check_env_variables()

        # Assert
        assert result is True  # Function only checks for presence, not content

    # Function behavior when secret_vars list is empty
    def test_empty_secret_vars_list(self, mocker):
        # Arrange
        mocker.patch("api_client.helpers.config.secret_vars", [])
        mocker.patch.dict("os.environ", {}, clear=True)
        mocker.patch("builtins.print")

        # Act
        result = check_env_variables()

        # Assert
        assert result is True  # No variables to check means all checks pass

    # Function behavior with non-string environment variable values
    def test_non_string_env_variable_values(self, mocker):
        # Arrange
        mock_environ = {
            "AWS_ACCESS_KEY_ID": 12345,
            "AWS_SECRET_ACCESS_KEY": True,
            "AWS_REGION": ["us-west-2"],
            "FUNC_BULKIMG_ANALYSER_NAME": {"name": "function"},
            "S3BUCKET_SOURCE": 3.14,
            "DYNAMODB_TABLE_NAME": None,
        }

        # Convert all values to strings as os.environ would do
        string_environ = {k: str(v) for k, v in mock_environ.items()}

        mocker.patch.dict("os.environ", string_environ, clear=True)
        mocker.patch("builtins.print")

        # Act
        result = check_env_variables()

        # Assert
        assert result is True  # Function only checks for presence, not type

    # Function prints appropriate error messages for missing variables
    def test_prints_error_messages_for_missing_variables(self, mocker):
        # Arrange
        # Set only some variables
        mock_environ = {
            "AWS_ACCESS_KEY_ID": "test_key",
            "AWS_SECRET_ACCESS_KEY": "test_secret",
            # AWS_REGION is missing
            "FUNC_BULKIMG_ANALYSER_NAME": "test_function",
            # S3BUCKET_SOURCE is missing
            "DYNAMODB_TABLE_NAME": "test_table",
        }

        mocker.patch.dict("os.environ", mock_environ, clear=True)
        mock_print = mocker.patch("api_client.helpers.config.print")

        # Act
        result = check_env_variables()

        # Assert
        assert result is False
        assert mock_print.call_count == 2
        mock_print.assert_any_call("Environment secret not set: AWS_REGION")
        mock_print.assert_any_call("Environment secret not set: S3BUCKET_SOURCE")
