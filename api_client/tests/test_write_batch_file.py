"""
Module: test_write_batch_file

This module contains unit tests for the `write_batch_file` function in the
`api_client.helpers.general` module. The `write_batch_file` function is responsible
for writing batch records to a JSON file.

The tests in this module ensure that:
- The function successfully writes batch records to the specified file.
- The function creates a new file if it does not exist.
- The function overwrites existing file content if the file already exists.
- The function properly formats JSON with indentation for readability.
- The function handles edge cases such as empty batch records, invalid file paths, and permission errors.
- The function handles large datasets and non-serializable objects gracefully.

Dependencies:
- pytest: For test execution and assertions.
- api_client.helpers.general.write_batch_file: The function under test.

Test Cases:
- `test_writes_batch_records_to_file`: Verifies that the function successfully writes batch records to the specified file.
- `test_creates_new_file_if_not_exists`: Ensures the function creates a new file if it does not exist.
- `test_overwrites_existing_file_content`: Verifies that the function overwrites existing file content if the file already exists.
- `test_formats_json_with_proper_indentation`: Ensures the function properly formats JSON with indentation for readability.
- `test_handles_lists_of_different_sizes`: Verifies that the function handles lists of different sizes correctly.
- `test_handles_empty_batch_records`: Ensures the function handles empty batch records correctly by writing an empty list to the file.
- `test_handles_nonexistent_directory`: Verifies that the function raises a `FileNotFoundError` for invalid file paths.
- `test_handles_permission_errors`: Ensures the function raises a `PermissionError` when writing to a file in a read-only directory.
- `test_handles_non_serializable_objects`: Verifies that the function raises a `TypeError` when batch records contain non-serializable objects.
- `test_handles_large_batch_records`: Ensures the function handles very large batch records without memory issues.
"""

import json
import os
import stat

import pytest

from api_client.helpers.general import write_batch_file


class TestWriteBatchFile:
    """
    Test suite for the `write_batch_file` function.
    """

    # Successfully writes batch records to the specified filepath
    def test_writes_batch_records_to_file(self):
        """
        Test that the function successfully writes batch records to the specified file.

        Asserts:
            - The file is created and contains the expected batch records.
        """
        # Arrange
        filepath = "test_batch.json"
        batch_records = [{"id": 1, "name": "Test Record"}]

        # Act
        write_batch_file(filepath, batch_records)

        # Assert
        assert os.path.exists(filepath)
        with open(filepath, "r", encoding="utf-8") as file:
            content = json.load(file)
        assert content == batch_records

        # Cleanup
        os.remove(filepath)

    # Creates a new file if it doesn't exist
    def test_creates_new_file_if_not_exists(self):
        """
        Test that the function creates a new file if it does not exist.

        Asserts:
            - The file is created and contains the expected batch records.
        """
        # Arrange
        filepath = "new_test_batch.json"
        batch_records = [{"id": 1, "name": "Test Record"}]

        # Ensure file doesn't exist
        if os.path.exists(filepath):
            os.remove(filepath)

        # Act
        write_batch_file(filepath, batch_records)

        # Assert
        assert os.path.exists(filepath)

        # Cleanup
        os.remove(filepath)

    # Overwrites existing file content if the file already exists
    def test_overwrites_existing_file_content(self):
        """
        Test that the function overwrites existing file content if the file already exists.

        Asserts:
            - The file content is replaced with the new batch records.
        """
        # Arrange
        filepath = "existing_test_batch.json"
        initial_records = [{"id": 1, "name": "Initial Record"}]
        new_records = [{"id": 2, "name": "New Record"}]

        # Create initial file
        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(initial_records, file)

        # Act
        write_batch_file(filepath, new_records)

        # Assert
        with open(filepath, "r", encoding="utf-8") as file:
            content = json.load(file)
        assert content == new_records
        assert content != initial_records

        # Cleanup
        os.remove(filepath)

    # Properly formats JSON with indent=4 for readability
    def test_formats_json_with_proper_indentation(self):
        """
        Test that the function properly formats JSON with indentation for readability.

        Asserts:
            - The JSON file contains properly indented content.
        """
        # Arrange
        filepath = "indented_test_batch.json"
        batch_records = [{"id": 1, "name": "Test Record", "nested": {"key": "value"}}]

        # Act
        write_batch_file(filepath, batch_records)

        # Assert
        with open(filepath, "r", encoding="utf-8") as file:
            content = file.read()

        # Check for indentation (4 spaces)
        assert '    "id": 1' in content
        assert '        "key": "value"' in content

        # Cleanup
        os.remove(filepath)

    # Handles lists of different sizes correctly
    def test_handles_lists_of_different_sizes(self):
        """
        Test that the function handles lists of different sizes correctly.

        Asserts:
            - The file contains the expected number of batch records for each test case.
        """
        # Arrange
        filepath = "varying_size_test_batch.json"

        # Test with different list sizes
        test_cases = [
            [{"id": i} for i in range(1)],
            [{"id": i} for i in range(10)],
            [{"id": i} for i in range(100)],
        ]

        for batch_records in test_cases:
            # Act
            write_batch_file(filepath, batch_records)

            # Assert
            with open(filepath, "r", encoding="utf-8") as file:
                content = json.load(file)
            assert content == batch_records
            assert len(content) == len(batch_records)

        # Cleanup
        os.remove(filepath)

    # Handles empty batch_records list
    def test_handles_empty_batch_records(self):
        """
        Test that the function handles empty batch records correctly by writing an empty list to the file.

        Asserts:
            - The file contains an empty list.
        """
        # Arrange
        filepath = "empty_test_batch.json"
        batch_records = []

        # Act
        write_batch_file(filepath, batch_records)

        # Assert
        with open(filepath, "r", encoding="utf-8") as file:
            content = json.load(file)
        assert content == []
        assert isinstance(content, list)
        assert len(content) == 0

        # Cleanup
        os.remove(filepath)

    # Handles invalid filepath (non-existent directory)
    def test_handles_nonexistent_directory(self):
        """
        Test that the function raises a `FileNotFoundError` for invalid file paths.

        Asserts:
            - A `FileNotFoundError` is raised with the correct error message.
        """
        # Arrange
        filepath = "nonexistent_dir/test_batch.json"
        batch_records = [{"id": 1, "name": "Test Record"}]

        # Act & Assert
        with pytest.raises(FileNotFoundError):
            write_batch_file(filepath, batch_records)

    # Handles permission errors when writing to file
    def test_handles_permission_errors(self):
        """
        Test that the function raises a `PermissionError` when writing to a file in a read-only directory.

        Asserts:
            - A `PermissionError` is raised with the correct error message.
        """
        # Arrange
        # Create a directory with no write permissions
        read_only_dir = "read_only_dir"
        if not os.path.exists(read_only_dir):
            os.makedirs(read_only_dir)

        filepath = os.path.join(read_only_dir, "test_batch.json")
        batch_records = [{"id": 1, "name": "Test Record"}]

        # Make directory read-only on Unix systems
        if os.name != "nt":  # Skip on Windows
            os.chmod(read_only_dir, stat.S_IRUSR | stat.S_IXUSR)

            # Act & Assert
            with pytest.raises(PermissionError):
                write_batch_file(filepath, batch_records)

            # Cleanup - restore permissions for cleanup
            os.chmod(read_only_dir, stat.S_IRWXU)

        # Cleanup
        os.rmdir(read_only_dir)

    # Handles non-serializable objects in batch_records
    def test_handles_non_serializable_objects(self):
        """
        Test that the function raises a `TypeError` when batch records contain non-serializable objects.

        Asserts:
            - A `TypeError` is raised with the correct error message.
        """
        # Arrange
        filepath = "non_serializable_test_batch.json"

        # Create a non-serializable object (a function)
        def sample_function():
            return "This is not JSON serializable"

        batch_records = [{"id": 1, "function": sample_function}]

        # Act & Assert
        with pytest.raises(TypeError):
            write_batch_file(filepath, batch_records)

        # Verify file wasn't created or was empty
        if os.path.exists(filepath):
            os.remove(filepath)

    # Handles very large batch_records that may cause memory issues
    def test_handles_large_batch_records(self):
        """
        Test that the function handles very large batch records without memory issues.

        Asserts:
            - The file is created and contains all expected batch records.
            - The file size is greater than a specified threshold.
        """
        # Arrange
        filepath = "large_test_batch.json"

        # Create a relatively large dataset (not too large for test purposes)
        # 10,000 records with some nested data
        batch_records = [
            {
                "id": i,
                "data": "x" * 100,  # 100 character string
                "nested": {"values": list(range(20))},
            }
            for i in range(10000)
        ]

        # Act
        write_batch_file(filepath, batch_records)

        # Assert
        assert os.path.exists(filepath)
        file_size = os.path.getsize(filepath)
        assert file_size > 5000000  # Should be several MB

        # Verify data integrity by checking a few random elements
        with open(filepath, "r", encoding="utf-8") as file:
            content = json.load(file)
        assert len(content) == 10000
        assert content[0]["id"] == 0
        assert content[9999]["id"] == 9999

        # Cleanup
        os.remove(filepath)
