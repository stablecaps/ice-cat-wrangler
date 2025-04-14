import pytest


class TestWriteDebugLogsToDynamodb:

    # Function writes logs to DynamoDB when is_debug is True and batch_id/img_fprint are set
    def test_writes_logs_to_dynamodb_when_debug_enabled(self, mocker):
        # Arrange
        mock_dynamodb_helper = mocker.patch(
            "functions.func_s3_bulkimg_analyse.dynamodb_helper"
        )
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
        from functions.func_s3_bulkimg_analyse import write_debug_logs_to_dynamodb

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
    def test_retrieves_batch_id_and_img_fprint_from_global_context(self, mocker):
        # Arrange
        mock_dynamodb_helper = mocker.patch(
            "functions.func_s3_bulkimg_analyse.dynamodb_helper"
        )
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
        from functions.func_s3_bulkimg_analyse import write_debug_logs_to_dynamodb

        write_debug_logs_to_dynamodb()

        # Assert
        mock_dynamodb_helper.update_item.assert_called_once()
        call_args = mock_dynamodb_helper.update_item.call_args[1]
        assert call_args["item_dict"]["batch_id"] == test_batch_id
        assert call_args["item_dict"]["img_fprint"] == test_img_fprint

    # Function successfully converts logs to JSON using convert_to_json
    def test_converts_logs_to_json(self, mocker):
        # Arrange
        mock_dynamodb_helper = mocker.patch(
            "functions.func_s3_bulkimg_analyse.dynamodb_helper"
        )
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
        from functions.func_s3_bulkimg_analyse import write_debug_logs_to_dynamodb

        write_debug_logs_to_dynamodb()

        # Assert
        mock_convert_to_json.assert_called_once_with(data=test_logs)
        mock_dynamodb_helper.update_item.assert_called_once()
        assert (
            mock_dynamodb_helper.update_item.call_args[1]["item_dict"]["logs"]
            == mock_convert_to_json.return_value
        )

    # Function correctly calls dynamodb_helper.update_item with proper item_dict
    def test_calls_dynamodb_helper_update_item_with_correct_parameters(self, mocker):
        # Arrange
        mock_dynamodb_helper = mocker.patch(
            "functions.func_s3_bulkimg_analyse.dynamodb_helper"
        )
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
        from functions.func_s3_bulkimg_analyse import write_debug_logs_to_dynamodb

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
        # Arrange
        mock_dynamodb_helper = mocker.patch(
            "functions.func_s3_bulkimg_analyse.dynamodb_helper"
        )
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
        from functions.func_s3_bulkimg_analyse import write_debug_logs_to_dynamodb

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
    def test_exits_early_when_debug_disabled(self, mocker):
        # Arrange
        mock_dynamodb_helper = mocker.patch(
            "functions.func_s3_bulkimg_analyse.dynamodb_helper"
        )
        mock_log_collector = mocker.patch(
            "functions.func_s3_bulkimg_analyse.log_collector"
        )
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
        from functions.func_s3_bulkimg_analyse import write_debug_logs_to_dynamodb

        write_debug_logs_to_dynamodb()

        # Assert
        mock_logger.info.assert_called_once_with("in write_debug_logs_to_dynamodb()")
        mock_dynamodb_helper.update_item.assert_not_called()
        mock_convert_to_json.assert_not_called()

    # Function exits early when batch_id is None
    def test_exits_early_when_batch_id_is_none(self, mocker):
        # Arrange
        mock_dynamodb_helper = mocker.patch(
            "functions.func_s3_bulkimg_analyse.dynamodb_helper"
        )
        mock_log_collector = mocker.patch(
            "functions.func_s3_bulkimg_analyse.log_collector"
        )
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
        from functions.func_s3_bulkimg_analyse import write_debug_logs_to_dynamodb

        write_debug_logs_to_dynamodb()

        # Assert
        mock_logger.error.assert_called_once_with("batch_id not set. Exiting")
        mock_dynamodb_helper.update_item.assert_not_called()
        mock_convert_to_json.assert_not_called()

    # Function exits early when img_fprint is None
    def test_exits_early_when_img_fprint_is_none(self, mocker):
        # Arrange
        mock_dynamodb_helper = mocker.patch(
            "functions.func_s3_bulkimg_analyse.dynamodb_helper"
        )
        mock_log_collector = mocker.patch(
            "functions.func_s3_bulkimg_analyse.log_collector"
        )
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
        from functions.func_s3_bulkimg_analyse import write_debug_logs_to_dynamodb

        write_debug_logs_to_dynamodb()

        # Assert
        mock_logger.error.assert_called_once_with("batch_id not set. Exiting")
        mock_dynamodb_helper.update_item.assert_not_called()
        mock_convert_to_json.assert_not_called()
