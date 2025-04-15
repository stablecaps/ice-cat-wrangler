"""
Module: test_check_env_variables

This module contains unit tests for the `check_env_variables` function in the
`api_client.helpers.config` module. The `check_env_variables` function is responsible
for verifying that all required environment variables are set in the system.

The tests in this module ensure that:
- The function correctly identifies when all required environment variables are set.
- The function handles cases where some or all environment variables are missing.
- The function works with non-string environment variable values.
- The function prints appropriate error messages for missing variables.
- The function behaves correctly when the `secret_vars` list is empty.

Dependencies:
- pytest: For test execution and assertions.
- unittest.mock: For mocking environment variables and print statements.
- api_client.helpers.config.check_env_variables: The function under test.
- api_client.helpers.config.secret_vars: The list of required environment variables.

Test Cases:
- `test_all_env_variables_set_returns_true`: Verifies that the function returns `True` when all required environment variables are set.
- `test_identifies_all_secret_vars_present`: Ensures the function correctly identifies when all `secret_vars` are present in `os.environ`.
- `test_returns_correct_boolean_value`: Verifies that the function returns the correct boolean value based on the presence of environment variables.
- `test_works_with_predefined_secret_vars`: Ensures the function works with the predefined `secret_vars` list from the config module.
- `test_no_env_variables_set_returns_false`: Verifies that the function returns `False` when no environment variables are set.
- `test_some_env_variables_set_returns_false`: Ensures the function returns `False` when only some environment variables are set.
- `test_env_variables_with_empty_values`: Verifies that the function works with environment variables that have empty values.
- `test_empty_secret_vars_list`: Ensures the function behaves correctly when the `secret_vars` list is empty.
- `test_non_string_env_variable_values`: Verifies that the function works with non-string environment variable values.
- `test_prints_error_messages_for_missing_variables`: Ensures the function prints appropriate error messages for missing variables.
"""

from api_client.helpers.config import check_env_variables, secret_vars


class TestCheckEnvVariables:
    """
    Test suite for the `check_env_variables` function.
    """

    # All required environment variables are set and function returns True
    def test_all_env_variables_set_returns_true(self, mocker):
        """
        Test that the function returns `True` when all required environment variables are set.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The function returns `True`.
            - No error messages are printed.
        """
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
        """
        Test that the function correctly identifies when all `secret_vars` are present in `os.environ`.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The function returns `True`.
        """
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
        """
        Test that the function returns the correct boolean value based on the presence of environment variables.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The function returns `False` when a required variable is missing.
            - The function returns `True` when all required variables are present.
        """
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
        """
        Test that the function works with the predefined `secret_vars` list from the config module.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The function returns `True` when all `secret_vars` are set.
            - The function returns `False` when a required variable is missing.
        """
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
        """
        Test that the function returns `False` when no environment variables are set.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The function returns `False`.
            - An error message is printed for each missing variable.
        """
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
        """
        Test that the function returns `False` when only some environment variables are set.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The function returns `False`.
            - An error message is printed for each missing variable.
        """

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
        """
        Test that the function works with environment variables that have empty values.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The function returns `True` (only checks for presence, not content).
        """
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
        """
        Test that the function behaves correctly when the `secret_vars` list is empty.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The function returns `True` (no variables to check means all checks pass).
        """
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
        """
        Test that the function works with non-string environment variable values.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The function returns `True` (only checks for presence, not type).
        """
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
        """
        Test that the function prints appropriate error messages for missing variables.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The function returns `False`.
            - An error message is printed for each missing variable.
        """
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
