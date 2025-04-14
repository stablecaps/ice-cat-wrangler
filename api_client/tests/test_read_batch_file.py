# Generated by Qodo Gen
import json

import pytest

from api_client.helpers.general import read_batch_file


class TestReadBatchFile:

    # Successfully reads a valid JSON file and returns its contents as a dictionary
    def test_reads_valid_json_file(self, tmp_path):
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
