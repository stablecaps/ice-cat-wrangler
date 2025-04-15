"""
Module: test_write_string2file

This module contains unit tests for the `write_string_2file` function in the
`api_client.helpers.general` module. The `write_string_2file` function is responsible
for writing a string to a file.

The tests in this module ensure that:
- The function successfully writes strings to files in both write and append modes.
- The function creates a new file if it does not exist.
- The function overwrites existing file content when using write mode.
- The function appends content to existing files when using append mode.
- The function handles edge cases such as empty strings, large strings, non-existent directories, and permission errors.

Dependencies:
- pytest: For test execution and assertions.
- api_client.helpers.general.write_string_2file: The function under test.

Test Cases:
- `test_write_string_to_file_in_write_mode`: Verifies that the function writes a string to a file in write mode.
- `test_write_string_to_file_in_append_mode`: Ensures the function appends content to a file in append mode.
- `test_creates_new_file_if_not_exists`: Verifies that the function creates a new file if it does not exist.
- `test_overwrites_existing_content_in_write_mode`: Ensures the function overwrites existing file content in write mode.
- `test_appends_to_existing_content`: Verifies that the function appends content to existing files in append mode.
- `test_write_empty_string`: Ensures the function handles empty strings correctly.
- `test_write_large_string`: Verifies that the function handles very large strings without issues.
- `test_filepath_with_nonexistent_directories`: Ensures the function raises a `FileNotFoundError` for non-existent directories.
- `test_file_permission_issues`: Verifies that the function raises a `PermissionError` when writing to a file in a read-only directory.
"""

import os
import shutil

import pytest

from api_client.helpers.general import write_string_2file


class TestWriteString2file:
    """
    Test suite for the `write_string_2file` function.
    """

    # Successfully writes a string to a file in write mode
    def test_write_string_to_file_in_write_mode(self):
        """
        Test that the function writes a string to a file in write mode.

        Asserts:
            - The file is created and contains the expected content.
        """
        # Arrange
        test_file = "test_write.txt"
        test_content = "Hello, World!"

        # Act
        write_string_2file(test_file, test_content)

        # Assert
        with open(test_file, "r", encoding="utf-8") as file:
            content = file.read()
        assert content == test_content

        # Cleanup
        os.remove(test_file)

    # Successfully writes a string to a file in append mode
    def test_write_string_to_file_in_append_mode(self):
        """
        Test that the function appends content to a file in append mode.

        Asserts:
            - The file contains the initial content followed by the appended content.
        """
        # Arrange
        test_file = "test_append.txt"
        initial_content = "Initial content\n"
        append_content = "Appended content"

        # Create file with initial content
        with open(test_file, "w", encoding="utf-8") as file:
            file.write(initial_content)

        # Act
        write_string_2file(test_file, append_content, mode="a")

        # Assert
        with open(test_file, "r", encoding="utf-8") as file:
            content = file.read()
        assert content == initial_content + append_content

        # Cleanup
        os.remove(test_file)

    # Creates a new file if it doesn't exist
    def test_creates_new_file_if_not_exists(self):
        """
        Test that the function creates a new file if it does not exist.

        Asserts:
            - The file is created and contains the expected content.
        """
        # Arrange
        test_file = "new_test_file.txt"
        test_content = "Content in new file"

        # Ensure file doesn't exist
        if os.path.exists(test_file):
            os.remove(test_file)

        # Act
        write_string_2file(test_file, test_content)

        # Assert
        assert os.path.exists(test_file)
        with open(test_file, "r", encoding="utf-8") as file:
            content = file.read()
        assert content == test_content

        # Cleanup
        os.remove(test_file)

    # Overwrites existing file content when using write mode
    def test_overwrites_existing_content_in_write_mode(self):
        """
        Test that the function overwrites existing file content when using write mode.

        Asserts:
            - The file content is replaced with the new content.
        """
        # Arrange
        test_file = "test_overwrite.txt"
        initial_content = "Initial content that should be overwritten"
        new_content = "New content"

        # Create file with initial content
        with open(test_file, "w", encoding="utf-8") as file:
            file.write(initial_content)

        # Act
        write_string_2file(test_file, new_content)

        # Assert
        with open(test_file, "r", encoding="utf-8") as file:
            content = file.read()
        assert content == new_content
        assert content != initial_content

        # Cleanup
        os.remove(test_file)

    # Appends content to existing file when using append mode
    def test_appends_to_existing_content(self):
        """
        Test that the function appends content to an existing file when using append mode.

        Asserts:
            - The file contains the initial content followed by the appended content.
        """
        # Arrange
        test_file = "test_append_existing.txt"
        initial_content = "First line\n"
        second_content = "Second line\n"
        third_content = "Third line"

        # Create file with initial content
        with open(test_file, "w", encoding="utf-8") as file:
            file.write(initial_content)

        # Act - append twice
        write_string_2file(test_file, second_content, mode="a")
        write_string_2file(test_file, third_content, mode="a")

        # Assert
        with open(test_file, "r", encoding="utf-8") as file:
            content = file.read()
        assert content == initial_content + second_content + third_content

        # Cleanup
        os.remove(test_file)

    # Handling empty string as filetext
    def test_write_empty_string(self):
        """
        Test that the function handles empty strings correctly.

        Asserts:
            - The file is created and contains an empty string.
        """
        # Arrange
        test_file = "test_empty.txt"
        empty_content = ""

        # Act
        write_string_2file(test_file, empty_content)

        # Assert
        assert os.path.exists(test_file)
        with open(test_file, "r", encoding="utf-8") as file:
            content = file.read()
        assert content == empty_content
        assert len(content) == 0

        # Cleanup
        os.remove(test_file)

    # Handling very large strings
    def test_write_large_string(self):
        """
        Test that the function handles very large strings without issues.

        Asserts:
            - The file contains the expected large string.
        """
        # Arrange
        test_file = "test_large.txt"
        large_content = "A" * 1000000  # 1MB of data

        # Act
        write_string_2file(test_file, large_content)

        # Assert
        with open(test_file, "r", encoding="utf-8") as file:
            content = file.read()
        assert content == large_content
        assert len(content) == 1000000

        # Cleanup
        os.remove(test_file)

    # Handling filepath with directories that don't exist
    def test_filepath_with_nonexistent_directories(self):
        """
        Test that the function raises a `FileNotFoundError` for non-existent directories.

        Asserts:
            - A `FileNotFoundError` is raised with the correct error message.
        """
        # Arrange
        test_dir = "nonexistent_dir"
        test_file = os.path.join(test_dir, "test_file.txt")
        test_content = "Content in nested file"

        # Ensure directory doesn't exist
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)

        # Act & Assert
        with pytest.raises(FileNotFoundError):
            write_string_2file(test_file, test_content)

        # Cleanup
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)

    # Handling file permission issues
    def test_file_permission_issues(self):
        """
        Test that the function raises a `PermissionError` when writing to a file in a read-only directory.

        Asserts:
            - A `PermissionError` is raised with the correct error message.
        """
        # Skip on Windows as permission handling is different
        if os.name == "nt":
            pytest.skip("Skipping permission test on Windows")

        # Arrange
        test_file = "test_permission.txt"
        test_content = "Test content"

        # Create file and remove write permissions
        with open(test_file, "w", encoding="utf-8") as file:
            file.write("Initial content")
        os.chmod(test_file, 0o444)  # Read-only

        # Act & Assert
        with pytest.raises(PermissionError):
            write_string_2file(test_file, test_content)

        # Cleanup - restore permissions to delete
        os.chmod(test_file, 0o666)
        os.remove(test_file)
