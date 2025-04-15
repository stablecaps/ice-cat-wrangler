"""
Module: test_gen_item_dict1_from_s3key

This module contains unit tests for the `gen_item_dict1_from_s3key` function
in the `serverless.functions.fhelpers` module. The `gen_item_dict1_from_s3key`
function is responsible for parsing an S3 key and generating a dictionary
containing metadata about the file.

The tests in this module ensure that:
- Valid S3 keys are correctly parsed into metadata dictionaries.
- The global context is updated with batch ID, image fingerprint, and debug status.
- S3 keys with invalid formats raise appropriate exceptions.
- The "batch-" prefix is properly removed from batch IDs when present.

Dependencies:
- pytest: For test execution and assertions.
- serverless.functions.fhelpers.gen_item_dict1_from_s3key: The function under test.
- serverless.functions.global_context: The global context for storing batch-related metadata.
"""

import pytest

from serverless.functions.fhelpers import gen_item_dict1_from_s3key
from serverless.functions.global_context import global_context


class TestGenItemDict1FromS3key:
    """
    Test suite for the `gen_item_dict1_from_s3key` function.
    """

    # Correctly parses a valid S3 key in the format:
    #  "{file_hash}/{client_id}/{batch_id}/{current_date}/{epoch_timestamp}.png"
    def test_valid_s3_key_parsing(self, mocker):
        """
        Test that a valid S3 key in the format
        "{file_hash}/{client_id}/{batch_id}/{current_date}/{epoch_timestamp}.png"
        is correctly parsed into a metadata dictionary.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The resulting dictionary contains the expected keys and values.
        """
        # Arrange
        mocker.patch("serverless.functions.fhelpers.dyndb_ttl", "1234567890")
        s3_key = "abc123/client001/batch-456/2023-01-01/1672531200.png"
        s3_bucket = "test-bucket"

        # Act
        result = gen_item_dict1_from_s3key(s3_key, s3_bucket)

        # Assert
        assert result["img_fprint"] == "abc123"
        assert result["client_id"] == "client001"
        assert result["batch_id"] == "456"
        assert result["current_date"] == "2023-01-01"
        assert result["upload_ts"] == "1672531200"
        assert (
            result["s3img_key"]
            == "test-bucket/abc123/client001/batch-456/2023-01-01/1672531200.png"
        )
        assert result["op_status"] == "pending"
        assert result["ttl"] == "1234567890"

    # Updates global_context with batch_id, img_fprint, and is_debug values
    def test_global_context_update(self, mocker):
        """
        Test that the global context is updated with the batch ID, image fingerprint,
        and debug status when a valid S3 key is parsed.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The global context contains the expected values for batch ID,
              image fingerprint, and debug status.
        """
        # Arrange
        mocker.patch("serverless.functions.fhelpers.dyndb_ttl", "1234567890")
        mocker.patch("serverless.functions.fhelpers.global_context", global_context)
        s3_key = "hash789/client123/batch-456/2023-06-30/1688083200.png"
        s3_bucket = "test-bucket"

        # Act
        gen_item_dict1_from_s3key(s3_key, s3_bucket)

        # Assert
        assert global_context["batch_id"] == "456"
        assert global_context["img_fprint"] == "hash789"
        assert global_context["is_debug"] is False

    # Handles S3 keys with "-debug" suffix correctly by setting is_debug to True
    def test_debug_suffix_handling(self, mocker):
        """
        Test that S3 keys with a "-debug" suffix are correctly handled by setting
        the `is_debug` flag to `True` in the global context.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The `is_debug` flag in the global context is set to `True`.
            - The resulting dictionary contains the expected metadata values.
        """
        # Arrange
        mocker.patch("serverless.functions.fhelpers.dyndb_ttl", "1234567890")

        log_mock = mocker.patch("serverless.functions.fhelpers.LOG")
        s3_key = "hash123/client456/batch-303/2023-07-15/1689465600-debug.png"
        s3_bucket = "test-bucket"

        # Act
        result = gen_item_dict1_from_s3key(s3_key, s3_bucket)

        # Assert
        from serverless.functions.fhelpers import global_context

        assert global_context["is_debug"] is True
        assert log_mock.info.called
        assert result["upload_ts"] == "1689465600"
        assert result["batch_id"] == "303"

    # Raises ValueError when S3 key has incorrect number of parts (not 5)
    def test_invalid_s3_key_format(self):
        """
        Test that an S3 key with an invalid format raises a `ValueError`.

        Asserts:
            - A `ValueError` is raised with the expected error message.
        """
        # Arrange
        s3_key = (
            "hash123/client456/batch-303/2023-07-15"  # Missing epoch_timestamp part
        )
        s3_bucket = "test-bucket"

        # Act & Assert
        with pytest.raises(ValueError) as excinfo:
            gen_item_dict1_from_s3key(s3_key, s3_bucket)

        assert "S3 key does not match the expected format" in str(excinfo.value)

        # Test with too many parts
        s3_key = "hash123/client456/batch-303/2023-07-15/1689465600/extra.png"
        with pytest.raises(ValueError) as excinfo:
            gen_item_dict1_from_s3key(s3_key, s3_bucket)

        assert "S3 key does not match the expected format" in str(excinfo.value)

    # Properly removes "batch-" prefix from batch_id if present
    def test_batch_prefix_removal(self, mocker):
        """
        Test that the "batch-" prefix is properly removed from the batch ID
        when present in the S3 key.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The resulting dictionary contains the batch ID without the "batch-" prefix.
        """
        # Arrange
        mocker.patch("serverless.functions.fhelpers.dyndb_ttl", "1234567890")

        # Test with batch- prefix
        s3_key_with_prefix = "hash123/client456/batch-789/2023-08-01/1690934400.png"
        s3_bucket = "test-bucket"

        # Act
        result_with_prefix = gen_item_dict1_from_s3key(s3_key_with_prefix, s3_bucket)

        # Assert
        assert result_with_prefix["batch_id"] == "789"

        # Test without batch- prefix
        s3_key_without_prefix = "hash123/client456/789/2023-08-01/1690934400.png"

        # Act
        result_without_prefix = gen_item_dict1_from_s3key(
            s3_key_without_prefix, s3_bucket
        )

        # Assert
        assert result_without_prefix["batch_id"] == "789"
