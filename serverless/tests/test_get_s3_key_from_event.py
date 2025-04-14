import pytest
from functions.fhelpers import get_s3_key_from_event


class TestGetS3KeyFromEvent:

    # Successfully extracts S3 key from a valid event with Records containing S3 object key
    def test_extracts_s3_key_from_valid_event(self):
        # Arrange
        event = {"Records": [{"s3": {"object": {"key": "path/to/file.jpg"}}}]}

        # Act
        result = get_s3_key_from_event(event)

        # Assert
        assert result == "path/to/file.jpg"

    # Returns the correct S3 key string when event structure is properly formatted
    def test_returns_correct_s3_key_string(self):
        # Arrange
        expected_key = "folder1/folder2/image.png"
        event = {"Records": [{"s3": {"object": {"key": expected_key}}}]}

        # Act
        from functions.fhelpers import get_s3_key_from_event

        result = get_s3_key_from_event(event)

        # Assert
        assert result == expected_key
        assert isinstance(result, str)

    # Processes event with single record in Records list
    def test_processes_event_with_single_record(self):
        # Arrange
        event = {
            "Records": [
                {
                    "s3": {"object": {"key": "single-record.jpg"}},
                    "eventName": "ObjectCreated:Put",
                }
            ]
        }

        # Act
        result = get_s3_key_from_event(event)

        # Assert
        assert result == "single-record.jpg"

    # Event with empty Records list causes index error when accessing record_list[0]
    def test_empty_records_list_raises_index_error(self):
        # Arrange
        event = {"Records": []}

        # Act & Assert

        with pytest.raises(IndexError):
            get_s3_key_from_event(event)

    # Event with Records list but missing S3 object information
    def test_missing_s3_object_info_exits_system(self):
        # Arrange
        event = {
            "Records": [
                {
                    "s3": {
                        # Missing "object" key
                    }
                }
            ]
        }

        # Act & Assert
        with pytest.raises(SystemExit) as excinfo:
            get_s3_key_from_event(event)

        assert excinfo.value.code == 42

    # Event with Records list but empty S3 object key
    def test_empty_s3_object_key_exits_system(self):
        # Arrange
        event = {"Records": [{"s3": {"object": {"key": None}}}]}  # Empty key

        # Act & Assert
        with pytest.raises(SystemExit) as excinfo:
            get_s3_key_from_event(event)

        assert excinfo.value.code == 42
