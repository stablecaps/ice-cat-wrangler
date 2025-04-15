"""
Module: test_convert_time_string_to_epoch

This module contains unit tests for the `convert_time_string_to_epoch` function
in the `serverless.functions.fhelpers` module. The `convert_time_string_to_epoch`
function is responsible for converting a time string into an epoch timestamp.

The tests in this module ensure that:
- Valid time strings are correctly converted to epoch timestamps.
- Custom time formats are supported.
- Edge cases such as future dates, epoch boundaries, and unsupported timezones are handled.
- Proper exceptions are raised for invalid or unsupported inputs.

Dependencies:
- pytest: For test execution and assertions.
- serverless.functions.fhelpers.convert_time_string_to_epoch: The function under test.
"""

import pytest

from serverless.functions.fhelpers import convert_time_string_to_epoch


class TestConvertTimeStringToEpoch:
    """
    Test suite for the `convert_time_string_to_epoch` function.
    """

    # Convert a valid time string with default format to epoch time
    def test_convert_valid_time_string_with_default_format(self):
        """
        Test that a valid time string with the default format is correctly
        converted to an epoch timestamp.

        Asserts:
            - The returned epoch timestamp matches the expected value.
        """
        # Arrange
        time_string = "Mon, 01 Jan 2023 12:00:00 GMT"
        expected_epoch = 1672574400

        # Act
        result = convert_time_string_to_epoch(time_string)

        # Assert
        assert result == expected_epoch

    # Convert a valid time string with custom format to epoch time
    def test_convert_valid_time_string_with_custom_format(self):
        """
        Test that a valid time string with a custom format is correctly
        converted to an epoch timestamp.

        Asserts:
            - The returned epoch timestamp matches the expected value.
        """
        # Arrange
        time_string = "2023-01-01 12:00:00"
        format_string = "%Y-%m-%d %H:%M:%S"
        expected_epoch = 1672574400

        # Act
        result = convert_time_string_to_epoch(time_string, format_string)

        # Assert
        assert result == expected_epoch

    # Test handling of valid time string with GMT timezone
    def test_valid_time_string_gmt(self):
        """
        Test that a valid time string with the GMT timezone is correctly
        converted to an epoch timestamp.

        Asserts:
            - The returned epoch timestamp matches the expected value.
        """
        # Arrange
        time_string = "Mon, 01 Jan 2023 12:00:00 GMT"
        expected_epoch = 1672574400

        # Act
        result = convert_time_string_to_epoch(time_string)

        # Assert
        assert result == expected_epoch

    # TODO: fix this test test_valid_time_string_est
    # Test handling of valid time string with EST timezone
    # def test_valid_time_string_est(self):
    #     """
    #     Test that a valid time string with the EST timezone is correctly
    #     converted to an epoch timestamp.

    #     Asserts:
    #         - The returned epoch timestamp matches the expected value.
    #     """
    #     # Arrange
    #     time_string = "Mon, 01 Jan 2023 07:00:00 EST"
    #     expected_epoch = 1672574400  # Same as GMT but adjusted for EST

    #     # Act
    #     result = convert_time_string_to_epoch(time_string)

    #     # Assert
    #     assert result == expected_epoch

    # Test handling of invalid time string format
    def test_invalid_time_string_format(self):
        """
        Test that an invalid time string format raises a `ValueError`.

        Asserts:
            - A `ValueError` is raised with the expected error message.
        """
        # Arrange
        time_string = "Invalid Time String"

        # Act & Assert
        with pytest.raises(ValueError, match="Error converting time string to epoch"):
            convert_time_string_to_epoch(time_string)

    # Test handling of naive datetime (no timezone)
    def test_naive_datetime(self):
        """
        Test that a naive datetime (without a timezone) is correctly
        converted to an epoch timestamp using a custom format.

        Asserts:
            - The returned epoch timestamp matches the expected value.
        """
        # Arrange
        time_string = "2023-01-01 12:00:00"
        format_string = "%Y-%m-%d %H:%M:%S"
        expected_epoch = 1672574400

        # Act
        result = convert_time_string_to_epoch(time_string, format_string)

        # Assert
        assert result == expected_epoch

    # Test handling of future date
    def test_future_date(self):
        """
        Test that a future date is correctly converted to an epoch timestamp.

        Asserts:
            - The returned epoch timestamp matches the expected value.
        """
        # Arrange
        time_string = "Fri, 01 Jan 2100 00:00:00 GMT"
        expected_epoch = 4102444800

        # Act
        result = convert_time_string_to_epoch(time_string)

        # Assert
        assert result == expected_epoch

    # Test handling of epoch boundary
    def test_epoch_boundary(self):
        """
        Test that the epoch boundary (January 1, 1970) is correctly
        converted to an epoch timestamp.

        Asserts:
            - The returned epoch timestamp is 0.
        """
        # Arrange
        time_string = "Thu, 01 Jan 1970 00:00:00 GMT"
        expected_epoch = 0

        # Act
        result = convert_time_string_to_epoch(time_string)

        # Assert
        assert result == expected_epoch

    # Test handling of unsupported timezone
    def test_unsupported_timezone(self):
        """
        Test that an unsupported timezone in the time string raises a `ValueError`.

        Asserts:
            - A `ValueError` is raised with the expected error message.
        """
        # Arrange
        time_string = "Mon, 01 Jan 2023 07:00:00 XYZ"  # XYZ is not a valid timezone

        # Act & Assert
        with pytest.raises(ValueError, match="Error converting time string to epoch"):
            convert_time_string_to_epoch(time_string)
