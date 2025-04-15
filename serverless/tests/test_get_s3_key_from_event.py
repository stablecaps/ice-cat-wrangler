"""
Module: test_get_s3_key_from_event

This module contains unit tests for the `get_s3_key_from_event` function in the
`serverless.functions.fhelpers` module. The `get_s3_key_from_event` function is
responsible for extracting the S3 object key from an event triggered by an S3 bucket.

The tests in this module ensure that:
- The function correctly extracts the S3 key from valid event structures.
- The function handles edge cases such as empty `Records` lists or missing S3 object information.
- Proper exceptions are raised or the system exits gracefully for invalid inputs.

Dependencies:
- pytest: For test execution and assertions.
- serverless.functions.fhelpers.get_s3_key_from_event: The function under test.
"""

import pytest
from functions.fhelpers import get_s3_key_from_event


class TestGetS3KeyFromEvent:
    """
    Test suite for the `get_s3_key_from_event` function.
    """

    # Successfully extracts S3 key from a valid event with Records containing S3 object key
    def test_extracts_s3_key_from_valid_event(self):
        """
        Test that the function successfully extracts the S3 key from a valid event
        containing a `Records` list with S3 object key information.

        Asserts:
            - The extracted S3 key matches the expected value.
        """
        # Arrange
        event = {"Records": [{"s3": {"object": {"key": "path/to/file.jpg"}}}]}

        # Act
        result = get_s3_key_from_event(event)

        # Assert
        assert result == "path/to/file.jpg"

    # Returns the correct S3 key string when event structure is properly formatted
    def test_returns_correct_s3_key_string(self):
        """
        Test that the function returns the correct S3 key string when the event
        structure is properly formatted.

        Asserts:
            - The returned S3 key matches the expected value.
            - The returned value is of type `str`.
        """
        # Arrange
        expected_key = "folder1/folder2/image.png"
        event = {"Records": [{"s3": {"object": {"key": expected_key}}}]}

        # Act
        result = get_s3_key_from_event(event)

        # Assert
        assert result == expected_key
        assert isinstance(result, str)

    # Processes event with single record in Records list
    def test_processes_event_with_single_record(self):
        """
        Test that the function processes an event with a single record in the
        `Records` list and extracts the correct S3 key.

        Asserts:
            - The extracted S3 key matches the expected value.
        """
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
        """
        Test that an event with an empty `Records` list raises an `IndexError`.

        Asserts:
            - An `IndexError` is raised when attempting to access the first record.
        """
        # Arrange
        event = {"Records": []}

        # Act & Assert

        with pytest.raises(IndexError):
            get_s3_key_from_event(event)

    # Event with Records list but missing S3 object information
    def test_missing_s3_object_info_exits_system(self):
        """
        Test that an event with a `Records` list but missing S3 object information
        causes the system to exit with code 42.

        Asserts:
            - A `SystemExit` is raised with the exit code 42.
        """
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
        """
        Test that an event with a `Records` list but an empty S3 object key
        causes the system to exit with code 42.

        Asserts:
            - A `SystemExit` is raised with the exit code 42.
        """
        # Arrange
        event = {"Records": [{"s3": {"object": {"key": None}}}]}  # Empty key

        # Act & Assert
        with pytest.raises(SystemExit) as excinfo:
            get_s3_key_from_event(event)

        assert excinfo.value.code == 42
