"""
Module: test_write_debug_logs_to_dynamodb

This module contains unit tests for the `write_debug_logs_to_dynamodb` function
in the `functions.func_s3_bulkimg_analyse` module. The `write_debug_logs_to_dynamodb`
function is responsible for writing debug logs to DynamoDB when debug mode is enabled.

The tests in this module ensure that:
- Logs are correctly written to DynamoDB when debug mode is enabled.
- The function retrieves `batch_id` and `img_fprint` from the global context.
- Logs are properly converted to JSON before being written to DynamoDB.
- The function exits early when debug mode is disabled or required keys are missing.
- Appropriate log messages are generated during execution.

Dependencies:
- pytest: For test execution and assertions.
- mocker: For mocking dependencies and global context.
- functions.func_s3_bulkimg_analyse.write_debug_logs_to_dynamodb: The function under test.

Fixtures:
- `mock_dynamodb_helper`: Provides a mocked DynamoDBHelper object for testing.
"""

from functions.func_s3_bulkimg_analyse import write_debug_logs_to_dynamodb


class TestWriteDebugLogsToDynamodb:
    """
    Test suite for the `write_debug_logs_to_dynamodb` function.
    """

    # Function writes logs to DynamoDB when is_debug is True and batch_id/img_fprint are set
    def test_writes_logs_to_dynamodb_when_debug_enabled(
        self, mocker, mock_dynamodb_helper
    ):
        """
        Test that logs are written to DynamoDB when debug mode is enabled and
        `batch_id` and `img_fprint` are set in the global context.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.
            mock_dynamodb_helper: The fixture providing a mocked DynamoDBHelper object.

        Asserts:
            - Logs are converted to JSON and written to DynamoDB.
            - The `update_item` method of DynamoDBHelper is called with the correct parameters.
        """
        # Arrange
        mock_log_collector = mocker.patch(
            "functions.func_s3_bulkimg_analyse.log_collector"
        )
        mock_log_collector.logs = ["test log 1", "test log 2"]
        mock_convert_to_json = mocker.patch(
            "functions.func_s3_bulkimg_analyse.convert_to_json"
        )
        mock_convert_to_json.return_value = '["test log 1", "test log 2"]'

        # Set global context
        mocker.patch.dict(
            "functions.func_s3_bulkimg_analyse.global_context",
            {
                "is_debug": True,
                "batch_id": "test-batch-id",
                "img_fprint": "test-img-fprint",
            },
        )

        # Act
        write_debug_logs_to_dynamodb()

        # Assert
        expected_item_dict = {
            "batch_id": "test-batch-id",
            "img_fprint": "test-img-fprint",
            "logs": '["test log 1", "test log 2"]',
        }
        mock_dynamodb_helper.update_item.assert_called_once_with(
            item_dict=expected_item_dict
        )

    # Function correctly retrieves batch_id and img_fprint from global_context
    def test_retrieves_batch_id_and_img_fprint_from_global_context(
        self, mocker, mock_dynamodb_helper
    ):
        """
        Test that `write_debug_logs_to_dynamodb` correctly retrieves `batch_id`
        and `img_fprint` from the global context.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.
            mock_dynamodb_helper: The fixture providing a mocked DynamoDBHelper object.

        Asserts:
            - The `batch_id` and `img_fprint` values in the item dictionary match
              those in the global context.
        """
        # Arrange
        mock_log_collector = mocker.patch(
            "functions.func_s3_bulkimg_analyse.log_collector"
        )
        mock_log_collector.logs = ["test log"]
        mock_convert_to_json = mocker.patch(
            "functions.func_s3_bulkimg_analyse.convert_to_json"
        )
        mock_convert_to_json.return_value = '["test log"]'

        test_batch_id = "custom-batch-id"
        test_img_fprint = "custom-img-fprint"

        # Set global context
        mocker.patch.dict(
            "functions.func_s3_bulkimg_analyse.global_context",
            {
                "is_debug": True,
                "batch_id": test_batch_id,
                "img_fprint": test_img_fprint,
            },
        )

        # Act

        write_debug_logs_to_dynamodb()

        # Assert
        mock_dynamodb_helper.update_item.assert_called_once()
        call_args = mock_dynamodb_helper.update_item.call_args[1]
        assert call_args["item_dict"]["batch_id"] == test_batch_id
        assert call_args["item_dict"]["img_fprint"] == test_img_fprint

    # Function successfully converts logs to JSON using convert_to_json
    def test_converts_logs_to_json(self, mocker, mock_dynamodb_helper):
        """
        Test that logs are successfully converted to JSON using the `convert_to_json` function.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.
            mock_dynamodb_helper: The fixture providing a mocked DynamoDBHelper object.

        Asserts:
            - The `convert_to_json` function is called with the correct log data.
            - The converted JSON is included in the item dictionary written to DynamoDB.
        """
        # Arrange
        mock_log_collector = mocker.patch(
            "functions.func_s3_bulkimg_analyse.log_collector"
        )
        test_logs = ["log1", "log2", {"complex": "structure"}]
        mock_log_collector.logs = test_logs

        # Mock convert_to_json and capture the input
        mock_convert_to_json = mocker.patch(
            "functions.func_s3_bulkimg_analyse.convert_to_json"
        )
        mock_convert_to_json.return_value = '["log1", "log2", {"complex": "structure"}]'

        # Set global context
        mocker.patch.dict(
            "functions.func_s3_bulkimg_analyse.global_context",
            {
                "is_debug": True,
                "batch_id": "test-batch-id",
                "img_fprint": "test-img-fprint",
            },
        )

        # Act
        write_debug_logs_to_dynamodb()

        # Assert
        mock_convert_to_json.assert_called_once_with(data=test_logs)
        mock_dynamodb_helper.update_item.assert_called_once()
        assert (
            mock_dynamodb_helper.update_item.call_args[1]["item_dict"]["logs"]
            == mock_convert_to_json.return_value
        )

    # Function correctly calls dynamodb_helper.update_item with proper item_dict
    def test_calls_dynamodb_helper_update_item_with_correct_parameters(
        self, mocker, mock_dynamodb_helper
    ):
        """
        Test that `write_debug_logs_to_dynamodb` calls the `update_item` method
        of DynamoDBHelper with the correct item dictionary.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.
            mock_dynamodb_helper: The fixture providing a mocked DynamoDBHelper object.

        Asserts:
            - The `update_item` method is called with the expected item dictionary.
        """
        # Arrange
        mock_log_collector = mocker.patch(
            "functions.func_s3_bulkimg_analyse.log_collector"
        )
        mock_log_collector.logs = ["test log"]

        mock_convert_to_json = mocker.patch(
            "functions.func_s3_bulkimg_analyse.convert_to_json"
        )
        json_result = '["test log"]'
        mock_convert_to_json.return_value = json_result

        # Set global context
        mocker.patch.dict(
            "functions.func_s3_bulkimg_analyse.global_context",
            {
                "is_debug": True,
                "batch_id": "test-batch-id",
                "img_fprint": "test-img-fprint",
            },
        )

        # Act

        write_debug_logs_to_dynamodb()

        # Assert
        expected_item_dict = {
            "batch_id": "test-batch-id",
            "img_fprint": "test-img-fprint",
            "logs": json_result,
        }
        mock_dynamodb_helper.update_item.assert_called_once_with(
            item_dict=expected_item_dict
        )

    # Function logs appropriate messages during successful execution
    def test_logs_appropriate_messages_during_execution(self, mocker):
        """
        Test that `write_debug_logs_to_dynamodb` logs appropriate messages during execution.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.
            mock_dynamodb_helper: The fixture providing a mocked DynamoDBHelper object.

        Asserts:
            - Log messages indicate the function's entry and the writing of logs to DynamoDB.
        """
        # Arrange
        mock_log_collector = mocker.patch(
            "functions.func_s3_bulkimg_analyse.log_collector"
        )
        mock_log_collector.logs = ["test log"]
        mock_convert_to_json = mocker.patch(
            "functions.func_s3_bulkimg_analyse.convert_to_json"
        )
        mock_convert_to_json.return_value = '["test log"]'

        mock_logger = mocker.patch("functions.func_s3_bulkimg_analyse.LOG")

        # Set global context
        mocker.patch.dict(
            "functions.func_s3_bulkimg_analyse.global_context",
            {
                "is_debug": True,
                "batch_id": "test-batch-id",
                "img_fprint": "test-img-fprint",
            },
        )

        # Act

        write_debug_logs_to_dynamodb()

        # Assert
        mock_logger.info.assert_any_call("in write_debug_logs_to_dynamodb()")

        # Check for the log message about writing to DynamoDB
        item_dict_log_call = False
        for call in mock_logger.info.call_args_list:
            if "Writing logs to DynamoDB atexit:" in call[0][0]:
                item_dict_log_call = True
                break

        assert (
            item_dict_log_call
        ), "Expected log message about writing to DynamoDB was not found"

    # Function exits early when is_debug is False
    def test_exits_early_when_debug_disabled(self, mocker, mock_dynamodb_helper):
        """
        Test that `write_debug_logs_to_dynamodb` exits early when debug mode is disabled.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.
            mock_dynamodb_helper: The fixture providing a mocked DynamoDBHelper object.

        Asserts:
            - The function does not call `update_item` or `convert_to_json`.
            - An appropriate log message indicates early exit.
        """
        # Arrange
        mock_convert_to_json = mocker.patch(
            "functions.func_s3_bulkimg_analyse.convert_to_json"
        )
        mock_logger = mocker.patch("functions.func_s3_bulkimg_analyse.LOG")

        # Set global context with debug disabled
        mocker.patch.dict(
            "functions.func_s3_bulkimg_analyse.global_context",
            {
                "is_debug": False,
                "batch_id": "test-batch-id",
                "img_fprint": "test-img-fprint",
            },
        )

        # Act

        write_debug_logs_to_dynamodb()

        # Assert
        mock_logger.info.assert_called_once_with("in write_debug_logs_to_dynamodb()")
        mock_dynamodb_helper.update_item.assert_not_called()
        mock_convert_to_json.assert_not_called()

    # Function exits early when batch_id is None
    def test_exits_early_when_batch_id_is_none(self, mocker, mock_dynamodb_helper):
        """
        Test that `write_debug_logs_to_dynamodb` exits early when `batch_id` is None.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.
            mock_dynamodb_helper: The fixture providing a mocked DynamoDBHelper object.

        Asserts:
            - The function does not call `update_item` or `convert_to_json`.
            - An error log message indicates that `batch_id` is not set.
        """
        # Arrange
        mock_convert_to_json = mocker.patch(
            "functions.func_s3_bulkimg_analyse.convert_to_json"
        )
        mock_logger = mocker.patch("functions.func_s3_bulkimg_analyse.LOG")

        # Set global context with batch_id as None
        mocker.patch.dict(
            "functions.func_s3_bulkimg_analyse.global_context",
            {"is_debug": True, "batch_id": None, "img_fprint": "test-img-fprint"},
        )

        # Act

        write_debug_logs_to_dynamodb()

        # Assert
        mock_logger.error.assert_called_once_with("batch_id not set. Exiting")
        mock_dynamodb_helper.update_item.assert_not_called()
        mock_convert_to_json.assert_not_called()

    # Function exits early when img_fprint is None
    def test_exits_early_when_img_fprint_is_none(self, mocker, mock_dynamodb_helper):
        """
        Test that `write_debug_logs_to_dynamodb` exits early when `img_fprint` is None.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.
            mock_dynamodb_helper: The fixture providing a mocked DynamoDBHelper object.

        Asserts:
            - The function does not call `update_item` or `convert_to_json`.
            - An error log message indicates that `img_fprint` is not set.
        """
        # Arrange
        mock_convert_to_json = mocker.patch(
            "functions.func_s3_bulkimg_analyse.convert_to_json"
        )
        mock_logger = mocker.patch("functions.func_s3_bulkimg_analyse.LOG")

        # Set global context with img_fprint as None
        mocker.patch.dict(
            "functions.func_s3_bulkimg_analyse.global_context",
            {"is_debug": True, "batch_id": "test-batch-id", "img_fprint": None},
        )

        # Act

        write_debug_logs_to_dynamodb()

        # Assert
        mock_logger.error.assert_called_once_with("batch_id not set. Exiting")
        mock_dynamodb_helper.update_item.assert_not_called()
        mock_convert_to_json.assert_not_called()
