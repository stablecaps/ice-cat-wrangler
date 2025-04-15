"""
Module: test_gen_item_dict2_from_rek_resp

This module contains unit tests for the `gen_item_dict2_from_rek_resp` function
in the `serverless.functions.fhelpers` module. The `gen_item_dict2_from_rek_resp`
function is responsible for processing AWS Rekognition responses and generating
a dictionary containing metadata about the analysis results.

The tests in this module ensure that:
- Valid Rekognition responses are correctly processed into metadata dictionaries.
- The global context is used to extract batch ID and image fingerprint.
- Timestamps in Rekognition responses are correctly converted to epoch time.
- Missing or incomplete Rekognition responses are handled gracefully.
- Proper error handling and logging are implemented for invalid inputs.

Dependencies:
- pytest: For test execution and assertions.
- serverless.functions.fhelpers.gen_item_dict2_from_rek_resp: The function under test.
- serverless.functions.global_context: The global context for storing batch-related metadata.
"""

from serverless.functions.fhelpers import gen_item_dict2_from_rek_resp


class TestGenItemDict2FromRekResp:
    """
    Test suite for the `gen_item_dict2_from_rek_resp` function.
    """

    # Successfully processes a valid Rekognition response with all required fields
    def test_valid_rekognition_response(self, mocker):
        """
        Test that a valid Rekognition response with all required fields is correctly
        processed into a metadata dictionary.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The resulting dictionary contains the expected keys and values.
            - The global context values are correctly included in the result.
            - The Rekognition timestamp is correctly converted to epoch time.
        """
        # Mock global_context
        mocker.patch(
            "serverless.functions.fhelpers.global_context",
            {"batch_id": "test-batch-123", "img_fprint": "abc123hash"},
        )

        # Mock safeget function
        mock_safeget = mocker.patch("serverless.functions.fhelpers.safeget")
        mock_safeget.side_effect = lambda d, *keys: (
            "Wed, 01 Jan 2023 12:00:00 GMT" if "date" in keys else 200
        )

        # Mock convert_time_string_to_epoch
        mock_convert = mocker.patch(
            "serverless.functions.fhelpers.convert_time_string_to_epoch"
        )
        mock_convert.return_value = 1672574400

        # Mock convert_to_json
        mock_json = mocker.patch("serverless.functions.fhelpers.convert_to_json")
        mock_json.return_value = '{"Labels": [{"Name": "Cat", "Confidence": 99.5}]}'

        # Mock logger
        mock_logger = mocker.patch("serverless.functions.fhelpers.LOG")

        # Test data
        rekog_results = {
            "rekog_resp": {
                "Labels": [{"Name": "Cat", "Confidence": 99.5}],
                "ResponseMetadata": {
                    "HTTPStatusCode": 200,
                    "HTTPHeaders": {"date": "Wed, 01 Jan 2023 12:00:00 GMT"},
                },
            },
            "rek_match": "True",
        }

        # Call function
        result = gen_item_dict2_from_rek_resp(rekog_results)

        # Assertions
        assert result["batch_id"] == "test-batch-123"
        assert result["img_fprint"] == "abc123hash"
        assert result["op_status"] == "success"
        assert result["rek_iscat"] == "True"
        assert result["rek_ts"] == 1672574400
        assert mock_logger.info.call_count == 2

    # Extracts batch_id and img_fprint from global_context correctly
    def test_global_context_extraction(self, mocker):
        """
        Test that `gen_item_dict2_from_rek_resp` correctly extracts `batch_id`
        and `img_fprint` from the global context.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The `batch_id` and `img_fprint` values in the result match those
              in the global context.
        """
        # Mock global_context with specific values
        mocker.patch(
            "serverless.functions.fhelpers.global_context",
            {"batch_id": "custom-batch-456", "img_fprint": "xyz789hash"},
        )

        # Mock other dependencies
        mock_safeget = mocker.patch("serverless.functions.fhelpers.safeget")
        mock_safeget.side_effect = lambda d, *keys: (
            "Wed, 01 Jan 2023 12:00:00 GMT" if "date" in keys else 200
        )

        mock_convert = mocker.patch(
            "serverless.functions.fhelpers.convert_time_string_to_epoch"
        )
        mock_convert.return_value = 1672574400

        mock_json = mocker.patch("serverless.functions.fhelpers.convert_to_json")
        mock_json.return_value = "{}"

        mocker.patch("serverless.functions.fhelpers.LOG")

        # Test data
        rekog_results = {
            "rekog_resp": {
                "ResponseMetadata": {
                    "HTTPStatusCode": 200,
                    "HTTPHeaders": {"date": "Wed, 01 Jan 2023 12:00:00 GMT"},
                }
            },
            "rek_match": "False",
        }

        # Call function
        result = gen_item_dict2_from_rek_resp(rekog_results)

        # Assertions - focus on the global context extraction
        assert result["batch_id"] == "custom-batch-456"
        assert result["img_fprint"] == "xyz789hash"

    # Converts timestamp string to epoch time using convert_time_string_to_epoch
    def test_timestamp_conversion(self, mocker):
        """
        Test that the timestamp in the Rekognition response is correctly converted
        to epoch time using the `convert_time_string_to_epoch` function.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The `rek_ts` field in the result matches the expected epoch timestamp.
        """
        # Mock global_context
        mocker.patch(
            "serverless.functions.fhelpers.global_context",
            {"batch_id": "test-batch", "img_fprint": "test-hash"},
        )

        # Mock safeget to return a specific timestamp
        mock_safeget = mocker.patch("serverless.functions.fhelpers.safeget")
        mock_safeget.side_effect = lambda d, *keys: (
            "Thu, 15 Jun 2023 08:30:45 GMT" if "date" in keys else 200
        )

        # Mock convert_to_json
        mock_json = mocker.patch("serverless.functions.fhelpers.convert_to_json")
        mock_json.return_value = "{}"

        # Mock logger
        mocker.patch("serverless.functions.fhelpers.LOG")

        # Create a real convert_time_string_to_epoch function to verify it's called correctly
        real_convert = mocker.patch(
            "serverless.functions.fhelpers.convert_time_string_to_epoch"
        )
        real_convert.return_value = (
            1686818445  # Epoch for "Thu, 15 Jun 2023 08:30:45 GMT"
        )

        # Test data
        rekog_results = {
            "rekog_resp": {
                "ResponseMetadata": {
                    "HTTPStatusCode": 200,
                    "HTTPHeaders": {"date": "Thu, 15 Jun 2023 08:30:45 GMT"},
                }
            },
            "rek_match": "True",
        }

        # Call function
        result = gen_item_dict2_from_rek_resp(rekog_results)

        # Assertions
        assert result["rek_ts"] == 1686818445
        real_convert.assert_called_once_with(
            time_string="Thu, 15 Jun 2023 08:30:45 GMT",
            format_string="%a, %d %b %Y %H:%M:%S %Z",
        )

    # Handles missing rekog_resp in the input dictionary
    def test_missing_rekog_resp(self, mocker):
        """
        Test that `gen_item_dict2_from_rek_resp` handles missing `rekog_resp`
        in the input dictionary gracefully.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The function returns an empty dictionary.
            - An error is logged indicating the missing `rekog_resp`.
        """
        # Mock global_context
        mocker.patch(
            "serverless.functions.fhelpers.global_context",
            {"batch_id": "test-batch", "img_fprint": "test-hash"},
        )

        # Mock logger
        mock_logger = mocker.patch("serverless.functions.fhelpers.LOG")

        # Mock safeget and convert functions
        mocker.patch("serverless.functions.fhelpers.safeget")
        mocker.patch("serverless.functions.fhelpers.convert_time_string_to_epoch")
        mocker.patch("serverless.functions.fhelpers.convert_to_json")

        # Test data with missing rekog_resp
        rekog_results = {"rek_match": "True"}

        # Call function
        result = gen_item_dict2_from_rek_resp(rekog_results)

        # Assertions
        assert result == {}  # Should return empty dict on error
        mock_logger.error.assert_called_once()  # Should log an error

    # Handles missing rek_match in the input dictionary (defaults to None)
    def test_missing_rek_match(self, mocker):
        """
        Test that `gen_item_dict2_from_rek_resp` handles missing `rek_match`
        in the input dictionary by defaulting to `None`.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The `rek_iscat` field in the result is `None`.
            - The `op_status` field is set to "fail".
        """
        # Mock global_context
        mocker.patch(
            "serverless.functions.fhelpers.global_context",
            {"batch_id": "test-batch", "img_fprint": "test-hash"},
        )

        # Mock safeget
        mock_safeget = mocker.patch("serverless.functions.fhelpers.safeget")
        mock_safeget.side_effect = lambda d, *keys: (
            "Wed, 01 Jan 2023 12:00:00 GMT" if "date" in keys else 500
        )

        # Mock convert_time_string_to_epoch
        mock_convert = mocker.patch(
            "serverless.functions.fhelpers.convert_time_string_to_epoch"
        )
        mock_convert.return_value = 1672574400

        # Mock convert_to_json
        mock_json = mocker.patch("serverless.functions.fhelpers.convert_to_json")
        mock_json.return_value = "{}"

        # Mock logger
        mocker.patch("serverless.functions.fhelpers.LOG")

        # Test data with missing rek_match
        rekog_results = {
            "rekog_resp": {
                "ResponseMetadata": {
                    "HTTPStatusCode": 500,
                    "HTTPHeaders": {"date": "Wed, 01 Jan 2023 12:00:00 GMT"},
                }
            }
            # rek_match is missing
        }

        # Call function
        result = gen_item_dict2_from_rek_resp(rekog_results)

        # Assertions
        assert result["rek_iscat"] is None  # Should default to None
        assert result["op_status"] == "fail"
        assert result["batch_id"] == "test-batch"
        assert result["img_fprint"] == "test-hash"

    # Handles missing ResponseMetadata or HTTPHeaders in rekog_resp
    def test_missing_response_metadata(self, mocker):
        """
        Test that `gen_item_dict2_from_rek_resp` handles missing `ResponseMetadata`
        or `HTTPHeaders` in the Rekognition response gracefully.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The function returns an empty dictionary.
            - An error is logged indicating the missing metadata.
        """
        # Mock global_context
        mocker.patch(
            "serverless.functions.fhelpers.global_context",
            {"batch_id": "test-batch", "img_fprint": "test-hash"},
        )

        # Mock safeget to return None for missing metadata
        mock_safeget = mocker.patch("serverless.functions.fhelpers.safeget")
        mock_safeget.return_value = None

        # Mock logger
        mock_logger = mocker.patch("serverless.functions.fhelpers.LOG")

        # Mock convert_to_json
        mock_json = mocker.patch("serverless.functions.fhelpers.convert_to_json")
        mock_json.return_value = "{}"

        # Test data with incomplete rekog_resp
        rekog_results = {
            "rekog_resp": {
                # Missing ResponseMetadata and HTTPHeaders
                "Labels": [{"Name": "Dog", "Confidence": 85.0}]
            },
            "rek_match": "False",
        }

        # Call function
        result = gen_item_dict2_from_rek_resp(rekog_results)

        # Assertions
        assert result == {}  # Should return empty dict on error
        mock_logger.error.assert_called_once()  # Should log an error
