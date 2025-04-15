"""
Module: test_rekog_image_categorise

This module contains unit tests for the `rekog_image_categorise` function in the
`shared_helpers.boto3_helpers` module. The `rekog_image_categorise` function is responsible
for analyzing an image using AWS Rekognition and determining whether a specified label pattern
matches any of the detected labels.

The tests in this module ensure that:
- The function successfully categorizes images when a matching label pattern is found.
- The function correctly handles case sensitivity in label matching.
- The function uses default values for label patterns and confidence thresholds when not specified.
- The function logs detected labels and match statuses appropriately.
- The function handles edge cases such as empty image bytes, no labels returned, or invalid Rekognition clients.
- The function raises appropriate exceptions for AWS service errors or invalid inputs.

Dependencies:
- pytest: For test execution and assertions.
- pytest-mock: For mocking dependencies and Rekognition client behavior.
- botocore.exceptions: For simulating AWS client errors.
- shared_helpers.boto3_helpers.rekog_image_categorise: The function under test.

Test Cases:
- `test_successful_categorization_with_matching_label`: Verifies that the function successfully categorizes an image when a matching label pattern is found.
- `test_returns_true_when_label_pattern_found`: Ensures the function returns `rek_match="True"` when the label pattern is found.
- `test_returns_false_when_label_pattern_not_found`: Ensures the function returns `rek_match="False"` when the label pattern is not found.
- `test_uses_default_label_pattern`: Verifies that the function uses the default label pattern when none is specified.
- `test_logs_detected_labels_and_match_status`: Ensures the function logs detected labels and match statuses correctly.
- `test_handles_empty_image_bytes`: Verifies that the function handles empty image bytes gracefully and logs an error.
- `test_handles_case_sensitivity_in_label_matching`: Ensures the function handles case sensitivity in label matching by converting all labels and patterns to lowercase.
- `test_handles_no_labels_returned`: Verifies that the function handles cases where Rekognition returns no labels.
- `test_handles_invalid_rekog_client`: Ensures the function raises an exception and logs an error when the Rekognition client is invalid or `None`.
- `test_raises_exception_on_aws_service_error`: Verifies that the function raises appropriate exceptions for AWS service errors and logs the error.
"""

import pytest
from botocore.exceptions import ClientError

from shared_helpers.boto3_helpers import (
    DEFAULT_MIN_CONFIDENCE,
    MAX_LABELS,
    rekog_image_categorise,
)


class TestRekogImageCategorise:
    """
    Test suite for the `rekog_image_categorise` function.
    """

    # Successfully categorizes an image with matching label pattern
    def test_successful_categorization_with_matching_label(self, mocker):
        """
        Test that the function successfully categorizes an image when a matching label pattern is found.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The `rek_match` field in the result is "True".
            - The `detect_labels` method is called with the correct parameters.
        """
        # Arrange
        mock_rekog_client = mocker.Mock()
        mock_rekog_client.detect_labels.return_value = {
            "Labels": [
                {"Name": "Dog", "Confidence": 98.2},
                {"Name": "Cat", "Confidence": 96.5},
                {"Name": "Pet", "Confidence": 94.3},
            ]
        }
        mock_log = mocker.patch("shared_helpers.boto3_helpers.LOG")
        image_bytes = b"fake_image_data"

        # Act
        result = rekog_image_categorise(mock_rekog_client, image_bytes, "cat")

        # Assert
        assert result["rek_match"] == "True"
        assert "rekog_resp" in result
        mock_rekog_client.detect_labels.assert_called_once_with(
            Image={"Bytes": image_bytes},
            MaxLabels=MAX_LABELS,
            MinConfidence=DEFAULT_MIN_CONFIDENCE,
        )

    # Returns dictionary with rekog_resp and rek_match="True" when label pattern is found
    def test_returns_true_when_label_pattern_found(self, mocker):
        """
        Test that the function returns `rek_match="True"` when the label pattern is found in the detected labels.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The `rek_match` field in the result is "True".
            - The `rekog_resp` field contains the detected labels.
        """
        # Arrange
        mock_rekog_client = mocker.Mock()
        mock_response = {
            "Labels": [
                {"Name": "Animal", "Confidence": 99.1},
                {"Name": "Dog", "Confidence": 97.8},
                {"Name": "Mammal", "Confidence": 95.2},
            ]
        }
        mock_rekog_client.detect_labels.return_value = mock_response
        mocker.patch("shared_helpers.boto3_helpers.LOG")
        image_bytes = b"fake_image_data"

        # Act
        result = rekog_image_categorise(mock_rekog_client, image_bytes, "dog")

        # Assert
        assert result["rek_match"] == "True"
        assert result["rekog_resp"] == mock_response

    # Returns dictionary with rekog_resp and rek_match="False" when label pattern is not found
    def test_returns_false_when_label_pattern_not_found(self, mocker):
        """
        Test that the function returns `rek_match="False"` when the label pattern is not found in the detected labels.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The `rek_match` field in the result is "False".
            - The `rekog_resp` field contains the detected labels.
        """
        # Arrange
        mock_rekog_client = mocker.Mock()
        mock_response = {
            "Labels": [
                {"Name": "Animal", "Confidence": 99.1},
                {"Name": "Dog", "Confidence": 97.8},
                {"Name": "Mammal", "Confidence": 95.2},
            ]
        }
        mock_rekog_client.detect_labels.return_value = mock_response
        mocker.patch("shared_helpers.boto3_helpers.LOG")
        image_bytes = b"fake_image_data"

        # Act
        result = rekog_image_categorise(mock_rekog_client, image_bytes, "bird")

        # Assert
        assert result["rek_match"] == "False"
        assert result["rekog_resp"] == mock_response

    # Correctly uses default label_pattern "cat" when not specified
    def test_uses_default_label_pattern(self, mocker):
        """
        Test that the function uses the default label pattern "cat" when no label pattern is specified.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The `rek_match` field in the result is "True" when the default label pattern matches.
            - The `info` method of the logger is called with the correct message.
        """
        # Arrange
        mock_rekog_client = mocker.Mock()
        mock_rekog_client.detect_labels.return_value = {
            "Labels": [
                {"Name": "Cat", "Confidence": 98.5},
                {"Name": "Animal", "Confidence": 97.2},
            ]
        }
        mock_log = mocker.patch("shared_helpers.boto3_helpers.LOG")
        image_bytes = b"fake_image_data"

        # Act
        result = rekog_image_categorise(mock_rekog_client, image_bytes)

        # Assert
        assert result["rek_match"] == "True"
        mock_log.info.assert_any_call(
            "rek_match for label_pattern: <%s> is <%s>", "cat", "True"
        )

    # Logs detected labels and match status correctly
    def test_logs_detected_labels_and_match_status(self, mocker):
        """
        Test that the function logs detected labels and match statuses correctly.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The `info` method of the logger is called with the correct messages for detected labels and match status.
        """
        # Arrange
        mock_rekog_client = mocker.Mock()
        mock_rekog_client.detect_labels.return_value = {
            "Labels": [
                {"Name": "Dog", "Confidence": 98.2},
                {"Name": "Animal", "Confidence": 97.5},
            ]
        }
        mock_log = mocker.patch("shared_helpers.boto3_helpers.LOG")
        image_bytes = b"fake_image_data"

        # Act
        rekog_image_categorise(mock_rekog_client, image_bytes, "dog")

        # Assert
        mock_log.info.assert_any_call("Labels detected: <%s>", ["dog", "animal"])
        mock_log.info.assert_any_call(
            "rek_match for label_pattern: <%s> is <%s>", "dog", "True"
        )

    # Handles empty image_bytes input
    def test_handles_empty_image_bytes(self, mocker):
        """
        Test that the function handles empty `image_bytes` input gracefully and logs an error.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - An exception is raised for invalid image bytes.
            - The `error` method of the logger is called with the correct message.
        """
        # Arrange
        mock_rekog_client = mocker.Mock()
        mock_rekog_client.detect_labels.side_effect = Exception("Invalid image bytes")
        mock_log = mocker.patch("shared_helpers.boto3_helpers.LOG")
        image_bytes = b""

        # Act & Assert
        with pytest.raises(Exception):
            rekog_image_categorise(mock_rekog_client, image_bytes)

        mock_log.error.assert_called_once()
        mock_rekog_client.detect_labels.assert_called_once_with(
            Image={"Bytes": image_bytes},
            MaxLabels=MAX_LABELS,
            MinConfidence=DEFAULT_MIN_CONFIDENCE,
        )

    # Handles case sensitivity in label matching (converts all to lowercase)
    def test_handles_case_sensitivity_in_label_matching(self, mocker):
        """
        Test that the function handles case sensitivity in label matching by converting all labels and patterns to lowercase.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The `rek_match` field in the result is "True" for matching labels, regardless of case.
        """
        # Arrange
        mock_rekog_client = mocker.Mock()
        mock_rekog_client.detect_labels.return_value = {
            "Labels": [
                {"Name": "CAT", "Confidence": 98.5},
                {"Name": "Animal", "Confidence": 97.2},
            ]
        }
        mocker.patch("shared_helpers.boto3_helpers.LOG")
        image_bytes = b"fake_image_data"

        # Act
        result = rekog_image_categorise(mock_rekog_client, image_bytes, "cat")

        # Assert
        assert result["rek_match"] == "True"

        # Test with mixed case in label pattern
        result = rekog_image_categorise(mock_rekog_client, image_bytes, "CaT")
        assert result["rek_match"] == "True"

    # Handles when Rekognition returns no labels
    def test_handles_no_labels_returned(self, mocker):
        """
        Test that the function handles cases where Rekognition returns no labels.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The `rek_match` field in the result is "False".
            - The `rekog_resp` field contains an empty list of labels.
        """
        # Arrange
        mock_rekog_client = mocker.Mock()
        mock_rekog_client.detect_labels.return_value = {"Labels": []}
        mocker.patch("shared_helpers.boto3_helpers.LOG")
        image_bytes = b"fake_image_data"

        # Act
        result = rekog_image_categorise(mock_rekog_client, image_bytes, "cat")

        # Assert
        assert result["rek_match"] == "False"
        assert result["rekog_resp"]["Labels"] == []

    # Handles when rekog_client is None or invalid
    def test_handles_invalid_rekog_client(self, mocker):
        """
        Test that the function raises an exception and logs an error when the Rekognition client is invalid or `None`.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - An `AttributeError` is raised for an invalid Rekognition client.
            - The `error` method of the logger is called with the correct message.
        """
        # Arrange
        mock_log = mocker.patch("shared_helpers.boto3_helpers.LOG")
        image_bytes = b"fake_image_data"

        # Act & Assert
        with pytest.raises(AttributeError):
            rekog_image_categorise(None, image_bytes)

        mock_log.error.assert_called_once()

    # Properly raises exceptions when AWS service errors occur
    def test_raises_exception_on_aws_service_error(self, mocker):
        """
        Test that the function raises appropriate exceptions for AWS service errors and logs the error.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - A `ClientError` is raised for AWS service errors.
            - The `error` method of the logger is called with the correct message.
        """
        # Arrange
        mock_rekog_client = mocker.Mock()
        aws_error = ClientError(
            {
                "Error": {
                    "Code": "InvalidParameterException",
                    "Message": "Invalid parameter",
                }
            },
            "DetectLabels",
        )
        mock_rekog_client.detect_labels.side_effect = aws_error
        mock_log = mocker.patch("shared_helpers.boto3_helpers.LOG")
        image_bytes = b"fake_image_data"

        # Act & Assert
        with pytest.raises(ClientError):
            rekog_image_categorise(mock_rekog_client, image_bytes)

        mock_log.error.assert_called_once_with(
            "Error processing image from S3: <%s>", aws_error
        )
