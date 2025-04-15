"""
Module: test_read_file2string

This module contains unit tests for the `read_file_2string` function in the
`api_client.helpers.general` module. The `read_file_2string` function is responsible
for reading the contents of a file and returning it as a string.

The tests in this module ensure that:
- The function successfully reads text files and returns their content as strings.
- The function handles UTF-8 encoded files and special characters correctly.
- The function strips leading and trailing whitespace from the file content.
- The function handles edge cases such as empty files, files with only whitespace, and non-existent files.
- The function uses the default read mode "r" when no mode is specified.

Dependencies:
- pytest: For test execution and assertions.
- api_client.helpers.general.read_file_2string: The function under test.

Test Cases:
- `test_reads_file_content_successfully`: Verifies that the function successfully reads a text file and returns its content as a string.
- `test_strips_whitespace_from_content`: Ensures the function strips leading and trailing whitespace from the file content.
- `test_uses_default_read_mode`: Verifies that the function uses the default read mode "r" when no mode is specified.
- `test_handles_utf8_encoded_files`: Ensures the function handles UTF-8 encoded files correctly.
- `test_returns_none_for_nonexistent_file`: Verifies that the function returns `None` when the file does not exist.
- `test_handles_empty_file`: Ensures the function handles empty files correctly by returning an empty string.
- `test_handles_whitespace_only_file`: Verifies that the function handles files with only whitespace characters correctly by returning an empty string.
- `test_handles_special_characters`: Ensures the function handles files with special characters using UTF-8 encoding.
"""

from api_client.helpers.general import read_file_2string


class TestReadFile2string:
    """
    Test suite for the `read_file_2string` function.
    """

    # Successfully reads a text file and returns its content as a string
    def test_reads_file_content_successfully(self, tmp_path):
        """
        Test that the function successfully reads a text file and returns its content as a string.

        Args:
            tmp_path: The pytest fixture for creating temporary file paths.

        Asserts:
            - The returned string matches the expected content of the file.
        """
        # Arrange
        test_file = tmp_path / "test_file.txt"
        expected_content = "Hello, world!"
        test_file.write_text(expected_content)

        # Act
        result = read_file_2string(str(test_file))

        # Assert
        assert result == expected_content

    # Strips whitespace from the beginning and end of the file content
    def test_strips_whitespace_from_content(self, tmp_path):
        """
        Test that the function strips leading and trailing whitespace from the file content.

        Args:
            tmp_path: The pytest fixture for creating temporary file paths.

        Asserts:
            - The returned string matches the expected content without leading or trailing whitespace.
        """
        # Arrange
        test_file = tmp_path / "whitespace_file.txt"
        test_file.write_text("  \n  Hello, world!  \n  ")

        # Act
        result = read_file_2string(str(test_file))

        # Assert
        assert result == "Hello, world!"

    # Opens file with default read mode "r" when no mode is specified
    def test_uses_default_read_mode(self, tmp_path, monkeypatch):
        """
        Test that the function uses the default read mode "r" when no mode is specified.

        Args:
            tmp_path: The pytest fixture for creating temporary file paths.
            monkeypatch: The pytest fixture for mocking built-in functions.

        Asserts:
            - The file is opened in read mode "r".
            - The returned string matches the expected content of the file.
        """
        # Arrange
        test_file = tmp_path / "mode_test.txt"
        test_file.write_text("Test content")

        # Mock open to verify the mode
        original_open = open

        def mock_open(file, mode, **kwargs):
            assert mode == "r"
            return original_open(file, mode, **kwargs)

        monkeypatch.setattr("builtins.open", mock_open)

        # Act
        result = read_file_2string(str(test_file))

        # Assert
        assert result == "Test content"

    # Properly handles UTF-8 encoded text files
    def test_handles_utf8_encoded_files(self, tmp_path):
        """
        Test that the function properly handles UTF-8 encoded text files.

        Args:
            tmp_path: The pytest fixture for creating temporary file paths.

        Asserts:
            - The returned string matches the expected UTF-8 encoded content of the file.
        """
        # Arrange
        test_file = tmp_path / "utf8_file.txt"
        utf8_content = "こんにちは世界! ñáéíóú 你好世界"
        test_file.write_text(utf8_content, encoding="utf-8")

        # Act
        result = read_file_2string(str(test_file))

        # Assert
        assert result == utf8_content

    # Returns None when the file does not exist
    def test_returns_none_for_nonexistent_file(self, tmp_path):
        """
        Test that the function returns `None` when the file does not exist.

        Args:
            tmp_path: The pytest fixture for creating temporary file paths.

        Asserts:
            - The returned value is `None`.
        """
        # Arrange
        nonexistent_file = tmp_path / "does_not_exist.txt"

        # Act
        result = read_file_2string(str(nonexistent_file))

        # Assert
        assert result is None

    # Prints error message when file is not found
    # def test_prints_error_for_nonexistent_file(self, tmp_path, capsys):
    #     # Arrange
    #     nonexistent_file = f"{tmp_path}/missing_file.txt"

    #     # Act
    #     read_file_2string(str(nonexistent_file))

    #     # Assert
    #     captured = capsys.readouterr()
    #     print("captured", captured)
    #     assert f"File not found: {nonexistent_file}" in captured.out

    # Handles empty files correctly (returns empty string after stripping)
    def test_handles_empty_file(self, tmp_path):
        """
        Test that the function handles empty files correctly by returning an empty string.

        Args:
            tmp_path: The pytest fixture for creating temporary file paths.

        Asserts:
            - The returned string is empty.
        """
        # Arrange
        empty_file = tmp_path / "empty.txt"
        empty_file.write_text("")

        # Act
        result = read_file_2string(str(empty_file))

        # Assert
        assert result == ""

    # Handles files with only whitespace characters (returns empty string after stripping)
    def test_handles_whitespace_only_file(self, tmp_path):
        """
        Test that the function handles files with only whitespace characters correctly by returning an empty string.

        Args:
            tmp_path: The pytest fixture for creating temporary file paths.

        Asserts:
            - The returned string is empty.
        """

        # Arrange
        whitespace_file = tmp_path / "whitespace.txt"
        whitespace_file.write_text("   \n\t   \n   ")

        # Act
        result = read_file_2string(str(whitespace_file))

        # Assert
        assert result == ""

    # Handles files with special characters using UTF-8 encoding
    def test_handles_special_characters(self, tmp_path):
        """
        Test that the function handles files with special characters using UTF-8 encoding.

        Args:
            tmp_path: The pytest fixture for creating temporary file paths.

        Asserts:
            - The returned string matches the expected content with special characters.
        """
        # Arrange
        special_chars_file = tmp_path / "special.txt"
        special_content = "★☆♠♣♥♦✓✗€£¥©®™"
        special_chars_file.write_text(special_content, encoding="utf-8")

        # Act
        result = read_file_2string(str(special_chars_file))

        # Assert
        assert result == special_content
