"""
Module: test_construct_secrets_path

This module contains unit tests for the `construct_secrets_path` function in the
`api_client.helpers.config` module. The `construct_secrets_path` function is responsible
for constructing the full path to a secrets file and verifying its existence.

The tests in this module ensure that:
- The function correctly constructs paths using the current working directory and a config folder.
- The function handles various filename formats, including special characters, spaces, and long filenames.
- The function verifies the existence of the secrets file and exits with an error if the file does not exist.
- The function handles edge cases such as empty filenames and relative paths.

Dependencies:
- pytest: For test execution and assertions.
- unittest.mock: For mocking file system operations and system calls.
- api_client.helpers.config.construct_secrets_path: The function under test.

Test Cases:
- `test_returns_correct_path_when_file_exists`: Verifies that the function returns the correct path when the secrets file exists.
- `test_constructs_path_using_cwd_and_config_folder`: Ensures the function constructs the path using the current working directory and the config folder.
- `test_formats_path_with_provided_filename`: Verifies that the function properly formats the path with the provided filename.
- `test_handles_relative_paths_correctly`: Ensures the function handles relative paths correctly.
- `test_works_with_different_filenames`: Verifies that the function works with various filenames.
- `test_exits_when_secrets_file_does_not_exist`: Ensures the function exits with an error when the secrets file does not exist.
- `test_handles_special_characters_in_filename`: Verifies that the function handles filenames with special characters.
- `test_handles_empty_string_as_filename`: Ensures the function handles empty strings as filenames gracefully.
- `test_handles_very_long_filenames`: Verifies that the function handles very long filenames correctly.
- `test_handles_paths_with_spaces`: Ensures the function handles paths with spaces correctly.
"""

from api_client.helpers.config import construct_secrets_path


class TestConstructSecretsPath:
    """
    Test suite for the `construct_secrets_path` function.
    """

    # Returns correct path when secrets file exists
    def test_returns_correct_path_when_file_exists(self, mocker):
        """
        Test that the function returns the correct path when the secrets file exists.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The returned path matches the expected path.
            - The `os.path.isfile` method is called with the correct path.
        """
        # Arrange
        mocker.patch("os.getcwd", return_value="/root")
        mock_isfile = mocker.patch("os.path.isfile", return_value=True)
        secret_filename = ".env"
        expected_path = "/root/config/.env"

        # Act
        result = construct_secrets_path(secret_filename)

        # Assert
        assert result == expected_path
        mock_isfile.assert_called_once_with(expected_path)

    # Constructs path using current working directory and config folder
    def test_constructs_path_using_cwd_and_config_folder(self, mocker):
        """
        Test that the function constructs the path using the current working directory and the config folder.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The returned path matches the expected path.
            - The `os.getcwd` method is called once.
        """
        # Arrange
        mock_getcwd = mocker.patch("os.getcwd", return_value="/custom/path")
        mocker.patch("os.path.isfile", return_value=True)
        secret_filename = "secrets.env"
        expected_path = "/custom/path/config/secrets.env"

        # Act
        result = construct_secrets_path(secret_filename)

        # Assert
        assert result == expected_path
        mock_getcwd.assert_called_once()

    # Properly formats the path with the provided filename
    def test_formats_path_with_provided_filename(self, mocker):
        """
        Test that the function properly formats the path with the provided filename.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The returned path includes the provided filename.
        """
        # Arrange
        mocker.patch("os.getcwd", return_value="/root")
        mocker.patch("os.path.isfile", return_value=True)
        secret_filename = "test_secrets.json"
        expected_path = "/root/config/test_secrets.json"

        # Act
        result = construct_secrets_path(secret_filename)

        # Assert
        assert result == expected_path
        assert "test_secrets.json" in result

    # Handles relative paths correctly
    def test_handles_relative_paths_correctly(self, mocker):
        """
        Test that the function handles relative paths correctly.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The returned path matches the expected relative path.
        """
        # Arrange
        mocker.patch("os.getcwd", return_value=".")
        mocker.patch("os.path.isfile", return_value=True)
        secret_filename = "secrets.env"
        expected_path = "./config/secrets.env"

        # Act
        result = construct_secrets_path(secret_filename)

        # Assert
        assert result == expected_path

    # Works with different filenames
    def test_works_with_different_filenames(self, mocker):
        """
        Test that the function works with various filenames.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The returned path matches the expected path for each filename.
        """
        # Arrange
        mocker.patch("os.getcwd", return_value="/root")
        mocker.patch("os.path.isfile", return_value=True)
        filenames = [".env", "secrets.json", "config.yaml", "credentials.txt"]

        for filename in filenames:
            # Act
            result = construct_secrets_path(filename)

            # Assert
            assert result == f"/root/config/{filename}"

    # Exits with code 1 when secrets file does not exist
    def test_exits_when_secrets_file_does_not_exist(self, mocker):
        """
        Test that the function exits with an error when the secrets file does not exist.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The `print` method is called with the correct error message.
            - The `sys.exit` method is called with exit code 1.
        """
        # Arrange
        mocker.patch("os.getcwd", return_value="/root")
        mocker.patch("os.path.isfile", return_value=False)
        mock_print = mocker.patch("api_client.helpers.config.print")
        mock_exit = mocker.patch("sys.exit")
        secret_filename = ".env"
        expected_path = "/root/config/.env"

        # Act
        construct_secrets_path(secret_filename)

        # Assert
        mock_print.assert_called_once_with(
            f"No secret file found at dotenv_path: {expected_path}"
        )
        mock_exit.assert_called_once_with(1)

    # Handles special characters in filename
    def test_handles_special_characters_in_filename(self, mocker):
        """
        Test that the function handles filenames with special characters.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The returned path matches the expected path for each special character filename.
        """
        # Arrange
        mocker.patch("os.getcwd", return_value="/root")
        mocker.patch("os.path.isfile", return_value=True)
        special_filenames = [
            "file-with-dashes.env",
            "file_with_underscores.env",
            "file.with.dots.env",
            "file@with#special$chars.env",
        ]

        for filename in special_filenames:
            # Act
            result = construct_secrets_path(filename)

            # Assert
            assert result == f"/root/config/{filename}"

    # Handles empty string as filename
    def test_handles_empty_string_as_filename(self, mocker):
        """
        Test that the function handles empty strings as filenames gracefully.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The `print` method is called with the correct error message.
            - The `sys.exit` method is called with exit code 1.
        """
        # Arrange
        mocker.patch("os.getcwd", return_value="/root")
        mocker.patch("os.path.isfile", return_value=False)
        mock_print = mocker.patch("api_client.helpers.config.print")
        mock_exit = mocker.patch("sys.exit")
        secret_filename = ""
        expected_path = "/root/config/"

        # Act
        construct_secrets_path(secret_filename)

        # Assert
        mock_print.assert_called_once_with(
            f"No secret file found at dotenv_path: {expected_path}"
        )
        mock_exit.assert_called_once_with(1)

    # Handles very long filenames
    def test_handles_very_long_filenames(self, mocker):
        """
        Test that the function handles very long filenames correctly.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The returned path matches the expected path for the long filename.
            - The length of the returned path is greater than 200 characters.
        """
        # Arrange
        mocker.patch("os.getcwd", return_value="/root")
        mocker.patch("os.path.isfile", return_value=True)
        long_filename = "a" * 200 + ".env"  # 200 'a's followed by .env
        expected_path = f"/root/config/{long_filename}"

        # Act
        result = construct_secrets_path(long_filename)

        # Assert
        assert result == expected_path
        assert len(result) > 200  # Ensure the path is indeed long

    # Handles paths with spaces
    def test_handles_paths_with_spaces(self, mocker):
        """
        Test that the function handles paths with spaces correctly.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The returned path matches the expected path.
            - The returned path preserves spaces in the directory or filename.
        """
        # Arrange
        mocker.patch("os.getcwd", return_value="/path with spaces")
        mocker.patch("os.path.isfile", return_value=True)
        filename_with_spaces = "secret file.env"
        expected_path = "/path with spaces/config/secret file.env"

        # Act
        result = construct_secrets_path(filename_with_spaces)

        # Assert
        assert result == expected_path
        assert " " in result  # Ensure spaces are preserved
