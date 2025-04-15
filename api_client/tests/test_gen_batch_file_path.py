"""
Module: test_gen_batch_file_path

This module contains unit tests for the `gen_batch_file_path` function in the
`api_client.helpers.general` module. The `gen_batch_file_path` function is responsible
for generating a file path for batch files based on a given `client_id` and `batch_id`.
It ensures that the file path is constructed in the format `{client_id}_{batch_id}.json`
and resides in a "logs" directory within the current working directory.

The tests in this module ensure that:
- The function generates the correct file path format.
- The function creates the "logs" directory if it does not exist.
- The function handles various input scenarios, including empty strings, long IDs, and valid string inputs.
- The function handles edge cases such as non-writable directories and missing directories.

Dependencies:
- pytest: For test execution and assertions.
- unittest.mock: For mocking file system operations and environment variables.
- os: For handling file and directory paths.

Test Cases:
- `test_returns_correct_file_path_format`: Verifies that the function generates the correct file path format.
- `test_creates_logs_directory_if_not_exists`: Ensures the function creates the "logs" directory if it does not exist.
- `test_handles_valid_string_inputs`: Verifies that the function handles valid string inputs for `client_id` and `batch_id`.
- `test_returns_absolute_path_with_cwd`: Ensures the function returns an absolute path that includes the current working directory.
- `test_joins_path_components_correctly`: Verifies that the function correctly joins path components using `os.path.join`.
- `test_handles_empty_string_inputs`: Ensures the function handles empty strings for `client_id` or `batch_id`.
- `test_handles_very_long_ids`: Verifies that the function handles very long `client_id` or `batch_id` values.
- `test_logs_directory_not_writable`: Ensures the function behaves correctly when the "logs" directory exists but is not writable.
"""

import os

from api_client.helpers.general import gen_batch_file_path


class TestGenBatchFilePath:
    """
    Test suite for the `gen_batch_file_path` function.
    """

    # Returns correct file path with client_id and batch_id in the format "{client_id}_{batch_id}.json"
    def test_returns_correct_file_path_format(self, mocker):
        """
        Test that the function generates the correct file path format.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The file name matches the format `{client_id}_{batch_id}.json`.
            - The directory path matches the "logs" directory in the current working directory.
        """
        # Arrange
        client_id = "client123"
        batch_id = "batch456"
        expected_filename = f"{client_id}_{batch_id}.json"
        mock_cwd = "/fake/cwd"
        mocker.patch("os.getcwd", return_value=mock_cwd)
        mocker.patch("os.path.exists", return_value=True)
        mocker.patch("os.makedirs")

        # Act
        result = gen_batch_file_path(client_id, batch_id)

        # Assert
        assert os.path.basename(result) == expected_filename
        assert os.path.dirname(result) == os.path.join(mock_cwd, "logs")

    # Creates a "logs" directory in the current working directory if it doesn't exist
    def test_creates_logs_directory_if_not_exists(self, mocker):
        """
        Test that the function creates the "logs" directory in the current working directory if it does not exist.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The `os.makedirs` method is called to create the "logs" directory.
        """
        # Arrange
        client_id = "client123"
        batch_id = "batch456"
        mock_cwd = "/fake/cwd"
        logs_path = os.path.join(mock_cwd, "logs")

        mocker.patch("os.getcwd", return_value=mock_cwd)
        mock_exists = mocker.patch("os.path.exists", return_value=False)
        mock_makedirs = mocker.patch("os.makedirs")

        # Act

        gen_batch_file_path(client_id, batch_id)

        # Assert
        mock_exists.assert_called_once_with(logs_path)
        mock_makedirs.assert_called_once_with(logs_path)

    # Handles valid string inputs for both client_id and batch_id
    def test_handles_valid_string_inputs(self, mocker):
        """
        Test that the function handles valid string inputs for `client_id` and `batch_id`.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The file name matches the format `{client_id}_{batch_id}.json` for each test case.
        """
        # Arrange
        test_cases = [
            ("client123", "batch456"),
            ("client-abc", "batch-xyz"),
            ("CLIENT_123", "BATCH_456"),
            ("123", "456"),
        ]
        mocker.patch("os.getcwd", return_value="/fake/cwd")
        mocker.patch("os.path.exists", return_value=True)
        mocker.patch("os.makedirs")

        # Act & Assert

        for client_id, batch_id in test_cases:
            result = gen_batch_file_path(client_id, batch_id)
            assert os.path.basename(result) == f"{client_id}_{batch_id}.json"

    # Returns an absolute path that includes the current working directory
    def test_returns_absolute_path_with_cwd(self, mocker):
        """
        Test that the function returns an absolute path that includes the current working directory.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The returned path starts with the current working directory.
            - The returned path is an absolute path.
        """
        # Arrange
        client_id = "client123"
        batch_id = "batch456"
        mock_cwd = "/fake/cwd"
        mocker.patch("os.getcwd", return_value=mock_cwd)
        mocker.patch("os.path.exists", return_value=True)
        mocker.patch("os.makedirs")

        # Act

        result = gen_batch_file_path(client_id, batch_id)

        # Assert
        assert result.startswith(mock_cwd)
        assert os.path.isabs(result)

    # Successfully joins path components using os.path.join
    def test_joins_path_components_correctly(self, mocker):
        """
        Test that the function correctly joins path components using `os.path.join`.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The returned path matches the expected path constructed using `os.path.join`.
        """
        # Arrange
        client_id = "client123"
        batch_id = "batch456"
        mock_cwd = "/fake/cwd"
        expected_logs_dir = os.path.join(mock_cwd, "logs")
        expected_file_path = os.path.join(
            expected_logs_dir, f"{client_id}_{batch_id}.json"
        )

        mocker.patch("os.getcwd", return_value=mock_cwd)
        mocker.patch("os.path.exists", return_value=True)
        mocker.patch("os.makedirs")

        # Act

        result = gen_batch_file_path(client_id, batch_id)

        # Assert
        assert result == expected_file_path

    # Handles empty strings for client_id or batch_id
    def test_handles_empty_string_inputs(self, mocker):
        """
        Test that the function handles empty strings for `client_id` or `batch_id`.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The file name matches the format `{client_id}_{batch_id}.json` even when inputs are empty strings.
        """
        # Arrange
        test_cases = [("", "batch456"), ("client123", ""), ("", "")]
        mock_cwd = "/fake/cwd"
        mocker.patch("os.getcwd", return_value=mock_cwd)
        mocker.patch("os.path.exists", return_value=True)
        mocker.patch("os.makedirs")

        # Act & Assert

        for client_id, batch_id in test_cases:
            result = gen_batch_file_path(client_id, batch_id)
            assert os.path.basename(result) == f"{client_id}_{batch_id}.json"
            assert os.path.dirname(result) == os.path.join(mock_cwd, "logs")

    # Handles very long client_id or batch_id values
    def test_handles_very_long_ids(self, mocker):
        """
        Test that the function handles very long `client_id` or `batch_id` values.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The file name matches the format `{client_id}_{batch_id}.json` for long inputs.
        """
        # Arrange
        long_client_id = "client" + "x" * 1000
        long_batch_id = "batch" + "y" * 1000
        mock_cwd = "/fake/cwd"
        mocker.patch("os.getcwd", return_value=mock_cwd)
        mocker.patch("os.path.exists", return_value=True)
        mocker.patch("os.makedirs")

        # Act

        result = gen_batch_file_path(long_client_id, long_batch_id)

        # Assert
        assert os.path.basename(result) == f"{long_client_id}_{long_batch_id}.json"
        assert os.path.dirname(result) == os.path.join(mock_cwd, "logs")

    # Behavior when logs directory exists but is not writable
    def test_logs_directory_not_writable(self, mocker):
        """
        Test that the function behaves correctly when the "logs" directory exists but is not writable.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The function still returns the correct file path.
            - The `os.makedirs` method is not called if the directory exists.
        """
        # Arrange
        client_id = "client123"
        batch_id = "batch456"
        mock_cwd = "/fake/cwd"
        logs_path = os.path.join(mock_cwd, "logs")

        mocker.patch("os.getcwd", return_value=mock_cwd)
        mocker.patch("os.path.exists", return_value=True)  # Directory exists
        mock_makedirs = mocker.patch(
            "os.makedirs", side_effect=PermissionError("Permission denied")
        )

        # Act & Assert

        # The function should still return the path even if the directory can't be created
        result = gen_batch_file_path(client_id, batch_id)

        # The function should still return the correct path
        assert result == os.path.join(logs_path, f"{client_id}_{batch_id}.json")
        # makedirs should not be called since the directory exists
        mock_makedirs.assert_not_called()
