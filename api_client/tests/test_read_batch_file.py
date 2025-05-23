"""
Module: test_read_batch_file

This module contains unit tests for the `read_batch_file` function in the
`api_client.helpers.general` module. The `read_batch_file` function is responsible
for reading a batch file and returning its contents as a dictionary.

The tests in this module ensure that:
- The function successfully reads valid JSON files and returns their contents as dictionaries.
- The function handles UTF-8 encoded files correctly.
- The function returns the expected dictionary structure for valid batch files.
- The function properly closes files after reading.
- The function raises appropriate exceptions for missing or invalid files.
- The function handles edge cases such as empty JSON files, large files, and nested structures.
- The function preserves the original exception when JSON decoding fails.

Dependencies:
- pytest: For test execution and assertions.
- json: For handling JSON encoding and decoding.
- api_client.helpers.general.read_batch_file: The function under test.

Test Cases:
- `test_reads_valid_json_file`: Verifies that the function successfully reads a valid JSON file and returns its contents as a dictionary.
- `test_handles_utf8_encoded_files`: Ensures the function handles UTF-8 encoded files correctly.
- `test_returns_expected_dictionary_structure`: Verifies that the function returns the expected dictionary structure for valid batch files.
- `test_properly_closes_file_after_reading`: Ensures the function properly closes files after reading.
- `test_raises_file_not_found_error`: Verifies that the function raises a `FileNotFoundError` when the batch file does not exist.
- `test_raises_value_error_for_invalid_json`: Ensures the function raises a `ValueError` with an appropriate message for invalid JSON files.
- `test_handles_empty_json_files`: Verifies that the function handles empty JSON files correctly by returning an empty dictionary.
- `test_handles_large_json_files`: Ensures the function handles large JSON files without memory issues.
- `test_handles_nested_json_structures`: Verifies that the function handles JSON files with nested structures correctly.
- `test_preserves_original_exception`: Ensures the function preserves the original exception when JSON decoding fails.
"""

import json

import pytest

from api_client.helpers.general import read_batch_file


class TestReadBatchFile:
    """
    Test suite for the `read_batch_file` function.
    """

    # Successfully reads a valid JSON file and returns its contents as a dictionary
    def test_reads_valid_json_file(self, tmp_path):
        """
        Test that the function successfully reads a valid JSON file and returns its contents as a dictionary.

        Args:
            tmp_path: The pytest fixture for creating temporary file paths.

        Asserts:
            - The returned dictionary matches the expected data.
            - The returned object is of type `dict`.
        """
        # Arrange
        test_data = {"key": "value", "number": 42}
        batch_file = tmp_path / "valid_batch.json"
        with open(batch_file, "w", encoding="utf-8") as f:
            json.dump(test_data, f)

        # Act
        result = read_batch_file(str(batch_file))

        # Assert
        assert result == test_data
        assert isinstance(result, dict)

    # Handles UTF-8 encoded files correctly
    def test_handles_utf8_encoded_files(self, tmp_path):
        """
        Test that the function handles UTF-8 encoded files correctly.

        Args:
            tmp_path: The pytest fixture for creating temporary file paths.

        Asserts:
            - The returned dictionary matches the expected data.
            - UTF-8 encoded characters are correctly read and returned.
        """
        # Arrange
        test_data = {
            "unicode_key": "Unicode value with special chars: 你好, こんにちは, Привет"
        }
        batch_file = tmp_path / "utf8_batch.json"
        with open(batch_file, "w", encoding="utf-8") as f:
            json.dump(test_data, f)

        # Act
        result = read_batch_file(str(batch_file))

        # Assert
        assert result == test_data
        assert (
            result["unicode_key"]
            == "Unicode value with special chars: 你好, こんにちは, Привет"
        )

    # Returns the expected dictionary structure from a valid batch file
    def test_returns_expected_dictionary_structure(self, tmp_path):
        """
        Test that the function returns the expected dictionary structure from a valid batch file.

        Args:
            tmp_path: The pytest fixture for creating temporary file paths.

        Asserts:
            - The returned dictionary matches the expected structure.
            - All expected keys and values are present in the returned dictionary.
        """
        # Arrange
        expected_structure = {
            "client_id": "client123",
            "batch_id": "batch456",
            "timestamp": "2023-01-01T12:00:00",
            "items": [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}],
        }
        batch_file = tmp_path / "structured_batch.json"
        with open(batch_file, "w", encoding="utf-8") as f:
            json.dump(expected_structure, f)

        # Act
        result = read_batch_file(str(batch_file))

        # Assert
        assert result == expected_structure
        assert "client_id" in result
        assert "batch_id" in result
        assert "items" in result
        assert len(result["items"]) == 2

    # Properly closes the file after reading (using context manager)
    def test_properly_closes_file_after_reading(self, tmp_path, monkeypatch):
        """
        Test that the function properly closes the file after reading (using a context manager).

        Args:
            tmp_path: The pytest fixture for creating temporary file paths.
            monkeypatch: The pytest fixture for mocking built-in functions.

        Asserts:
            - The file is properly closed after reading.
        """
        # Arrange
        test_data = {"key": "value"}
        batch_file = tmp_path / "close_test_batch.json"
        with open(batch_file, "w", encoding="utf-8") as f:
            json.dump(test_data, f)

        # Mock the open function to track if it's properly closed
        original_open = open
        file_closed = False

        class MockFile:
            def __init__(self, *args, **kwargs):
                self.file = original_open(*args, **kwargs)

            def __enter__(self):
                return self.file

            def __exit__(self, *args, **kwargs):
                nonlocal file_closed
                file_closed = True
                return self.file.__exit__(*args, **kwargs)

            def __getattr__(self, name):
                return getattr(self.file, name)

        monkeypatch.setattr("builtins.open", MockFile)

        # Act
        read_batch_file(str(batch_file))

        # Assert
        assert file_closed is True

    # Raises FileNotFoundError when the batch file does not exist
    def test_raises_file_not_found_error(self, tmp_path):
        """
        Test that the function raises a `FileNotFoundError` when the batch file does not exist.

        Args:
            tmp_path: The pytest fixture for creating temporary file paths.

        Asserts:
            - A `FileNotFoundError` is raised with the correct error message.
        """
        # Arrange
        non_existent_file = tmp_path / "does_not_exist.json"

        # Act & Assert
        with pytest.raises(FileNotFoundError) as excinfo:
            read_batch_file(str(non_existent_file))

        # Verify the error message contains the file path
        assert str(non_existent_file) in str(excinfo.value)
        assert "Batch file not found" in str(excinfo.value)

    # Raises ValueError with appropriate message when the file contains invalid JSON
    def test_raises_value_error_for_invalid_json(self, tmp_path):
        """
        Test that the function raises a `ValueError` with an appropriate message when the file contains invalid JSON.

        Args:
            tmp_path: The pytest fixture for creating temporary file paths.

        Asserts:
            - A `ValueError` is raised with the correct error message.
        """
        # Arrange
        invalid_json_file = tmp_path / "invalid.json"
        with open(invalid_json_file, "w", encoding="utf-8") as f:
            f.write("{invalid json: content")

        # Act & Assert
        with pytest.raises(ValueError) as excinfo:
            read_batch_file(str(invalid_json_file))

        # Verify the error message
        assert "Error decoding JSON from batch file" in str(excinfo.value)

    # Handles empty JSON files (returning an empty dictionary)
    def test_handles_empty_json_files(self, tmp_path):
        """
        Test that the function handles empty JSON files correctly by returning an empty dictionary.

        Args:
            tmp_path: The pytest fixture for creating temporary file paths.

        Asserts:
            - The returned object is an empty dictionary.
        """
        # Arrange
        empty_json_file = tmp_path / "empty.json"
        with open(empty_json_file, "w", encoding="utf-8") as f:
            f.write("{}")

        # Act
        result = read_batch_file(str(empty_json_file))

        # Assert
        assert result == {}
        assert isinstance(result, dict)
        assert len(result) == 0

    # Handles large JSON files without memory issues
    def test_handles_large_json_files(self, tmp_path):
        """
        Test that the function handles large JSON files without memory issues.

        Args:
            tmp_path: The pytest fixture for creating temporary file paths.

        Asserts:
            - The returned dictionary contains all expected data.
            - The function processes large files efficiently.
        """
        # Arrange
        large_json_file = tmp_path / "large.json"
        large_data = {"items": [{"id": i, "data": "x" * 1000} for i in range(1000)]}
        with open(large_json_file, "w", encoding="utf-8") as f:
            json.dump(large_data, f)

        # Act
        result = read_batch_file(str(large_json_file))

        # Assert
        assert len(result["items"]) == 1000
        assert result["items"][0]["id"] == 0
        assert result["items"][999]["id"] == 999
        assert len(result["items"][0]["data"]) == 1000

    # Handles JSON files with nested structures correctly
    def test_handles_nested_json_structures(self, tmp_path):
        """
        Test that the function handles JSON files with nested structures correctly.

        Args:
            tmp_path: The pytest fixture for creating temporary file paths.

        Asserts:
            - The returned dictionary contains all nested data as expected.
        """
        # Arrange
        nested_data = {
            "level1": {
                "level2": {"level3": {"level4": {"value": "deeply nested value"}}}
            },
            "array_of_objects": [
                {"id": 1, "nested": {"value": "nested in array 1"}},
                {"id": 2, "nested": {"value": "nested in array 2"}},
            ],
        }
        nested_json_file = tmp_path / "nested.json"
        with open(nested_json_file, "w", encoding="utf-8") as f:
            json.dump(nested_data, f)

        # Act
        result = read_batch_file(str(nested_json_file))

        # Assert
        assert (
            result["level1"]["level2"]["level3"]["level4"]["value"]
            == "deeply nested value"
        )
        assert result["array_of_objects"][0]["nested"]["value"] == "nested in array 1"
        assert result["array_of_objects"][1]["nested"]["value"] == "nested in array 2"

    # Preserves the original exception when JSON decoding fails
    def test_preserves_original_exception(self, tmp_path):
        """
        Test that the function preserves the original exception when JSON decoding fails.

        Args:
            tmp_path: The pytest fixture for creating temporary file paths.

        Asserts:
            - The raised `ValueError` contains the original `JSONDecodeError` as its cause.
        """
        # Arrange
        invalid_json_file = tmp_path / "invalid_with_original_exception.json"
        with open(invalid_json_file, "w", encoding="utf-8") as f:
            f.write('{"unclosed": "bracket"')

        # Act & Assert
        with pytest.raises(ValueError) as excinfo:
            read_batch_file(str(invalid_json_file))

        # Check that the original exception is preserved
        assert excinfo.value.__cause__ is not None
        assert isinstance(excinfo.value.__cause__, json.JSONDecodeError)
