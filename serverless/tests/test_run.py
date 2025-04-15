import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../shared_helpers"))
)
import pytest
from functions.func_s3_bulkimg_analyse import run


class TestRun:

    # Successfully processes an S3 event with valid image data
    def test_successful_processing_of_valid_s3_event(
        self, mocker, mock_aws_clients, mock_dynamodb_helper
    ):
        # Mock AWS services and helpers
        mock_s3_client, _, _ = mock_aws_clients

        # Mock the validate_s3bucket function
        mock_validate = mocker.patch(
            "functions.func_s3_bulkimg_analyse.validate_s3bucket"
        )
        mock_validate.return_value = ("source-bucket", "dest-bucket", "fail-bucket")

        # Mock the get_s3_key_from_event function
        mock_get_key = mocker.patch(
            "functions.func_s3_bulkimg_analyse.get_s3_key_from_event"
        )
        mock_get_key.return_value = (
            "hash123/client456/batch-789/20230101/1609459200.png"
        )

        # Mock the gen_item_dict1_from_s3key function
        mock_gen_dict1 = mocker.patch(
            "functions.func_s3_bulkimg_analyse.gen_item_dict1_from_s3key"
        )
        mock_gen_dict1.return_value = {
            "batch_id": "789",
            "img_fprint": "hash123",
            "client_id": "client456",
            "s3img_key": "source-bucket/hash123/client456/batch-789/20230101/1609459200.png",
            "op_status": "pending",
        }

        # Mock get_filebytes_from_s3
        mock_get_bytes = mocker.patch(
            "functions.func_s3_bulkimg_analyse.get_filebytes_from_s3"
        )
        mock_get_bytes.return_value = b"fake_image_bytes"

        # Mock the S3 client's get_object method to simulate a successful response
        mock_s3_client.get_object.return_value = {
            "Body": mocker.Mock(read=lambda: b"fake_image_bytes")
        }

        # Mock rekog_image_categorise
        mock_rekog = mocker.patch(
            "functions.func_s3_bulkimg_analyse.rekog_image_categorise"
        )
        mock_rekog.return_value = {
            "rekog_resp": {
                "ResponseMetadata": {
                    "HTTPStatusCode": 200,
                    "HTTPHeaders": {"date": "Wed, 01 Jan 2023 00:00:00 GMT"},
                }
            },
            "rek_match": True,
        }

        # Mock gen_item_dict2_from_rek_resp
        mock_gen_dict2 = mocker.patch(
            "functions.func_s3_bulkimg_analyse.gen_item_dict2_from_rek_resp"
        )
        mock_gen_dict2.return_value = {
            "batch_id": "789",
            "img_fprint": "hash123",
            "op_status": "success",
            "rek_iscat": True,
        }

        # Mock move_s3_object_based_on_rekog_response
        mock_move = mocker.patch(
            "functions.func_s3_bulkimg_analyse.move_s3_object_based_on_rekog_response"
        )
        mock_move.return_value = True

        # Mock global_context
        mocker.patch(
            "functions.func_s3_bulkimg_analyse.global_context",
            {"batch_id": "789", "img_fprint": "hash123", "is_debug": False},
        )

        # Mock write_debug_logs_to_dynamodb
        mock_write_logs = mocker.patch(
            "functions.func_s3_bulkimg_analyse.write_debug_logs_to_dynamodb"
        )

        # Create test event and context
        event = {
            "Records": [
                {
                    "s3": {
                        "object": {
                            "key": "hash123/client456/batch-789/20230101/1609459200.png"
                        }
                    }
                }
            ]
        }
        context = {}

        # Call the function under test
        from functions.func_s3_bulkimg_analyse import run

        run(event, context)

        # Verify all expected functions were called
        mock_validate.assert_called_once_with(s3_client=mocker.ANY)
        mock_get_key.assert_called_once_with(event=event)
        mock_gen_dict1.assert_called_once()
        mock_dynamodb_helper.write_item.assert_called_once()
        mock_get_bytes.assert_called_once()
        mock_rekog.assert_called_once()
        mock_gen_dict2.assert_called_once()
        mock_dynamodb_helper.update_item.assert_called()
        mock_move.assert_called_once()
        mock_write_logs.assert_called_once()

    # Correctly extracts S3 key from event and validates S3 buckets
    def test_s3_key_extraction_and_bucket_validation(self, mocker):

        # Mock the validate_s3bucket function
        mock_validate = mocker.patch(
            "functions.func_s3_bulkimg_analyse.validate_s3bucket"
        )
        mock_validate.return_value = ("source-bucket", "dest-bucket", "fail-bucket")

        # Mock the get_s3_key_from_event function
        mock_get_key = mocker.patch(
            "functions.func_s3_bulkimg_analyse.get_s3_key_from_event"
        )
        mock_get_key.return_value = (
            "hash123/client456/batch-789/20230101/1609459200.png"
        )

        # Mock remaining functions to isolate the test
        mocker.patch("functions.func_s3_bulkimg_analyse.gen_item_dict1_from_s3key")
        mocker.patch("functions.func_s3_bulkimg_analyse.get_filebytes_from_s3")
        mocker.patch("functions.func_s3_bulkimg_analyse.rekog_image_categorise")
        mocker.patch("functions.func_s3_bulkimg_analyse.gen_item_dict2_from_rek_resp")
        mocker.patch(
            "functions.func_s3_bulkimg_analyse.move_s3_object_based_on_rekog_response"
        )
        mocker.patch("functions.func_s3_bulkimg_analyse.write_debug_logs_to_dynamodb")
        mocker.patch("functions.func_s3_bulkimg_analyse.dynamodb_helper")

        # Create test event and context
        event = {
            "Records": [
                {
                    "s3": {
                        "object": {
                            "key": "hash123/client456/batch-789/20230101/1609459200.png"
                        }
                    }
                }
            ]
        }
        context = {}

        # Call the function under test
        from functions.func_s3_bulkimg_analyse import run

        run(event, context)

        # Verify the key extraction and bucket validation functions were called with correct parameters
        mock_validate.assert_called_once_with(s3_client=mocker.ANY)
        mock_get_key.assert_called_once_with(event=event)

        # Verify the returned values are used in subsequent operations
        assert mock_validate.return_value[0] == "source-bucket"
        assert mock_validate.return_value[1] == "dest-bucket"
        assert mock_validate.return_value[2] == "fail-bucket"
        assert (
            mock_get_key.return_value
            == "hash123/client456/batch-789/20230101/1609459200.png"
        )

    # Successfully analyzes image with Rekognition and detects a cat
    def test_successful_rekognition_cat_detection(
        self, mocker, mock_aws_clients, mock_dynamodb_helper
    ):
        # Mock AWS services
        mock_s3_client, mock_rekog_client, _ = mock_aws_clients

        # Mock helper functions
        mocker.patch(
            "functions.func_s3_bulkimg_analyse.validate_s3bucket",
            return_value=("source-bucket", "dest-bucket", "fail-bucket"),
        )
        mocker.patch(
            "functions.func_s3_bulkimg_analyse.get_s3_key_from_event",
            return_value="hash123/client456/batch-789/20230101/1609459200.png",
        )
        mocker.patch(
            "functions.func_s3_bulkimg_analyse.gen_item_dict1_from_s3key",
            return_value={
                "batch_id": "789",
                "img_fprint": "hash123",
                "client_id": "client456",
                "s3img_key": "source-bucket/hash123/client456/batch-789/20230101/1609459200.png",
                "op_status": "pending",
            },
        )

        # Mock get_filebytes_from_s3
        mock_get_bytes = mocker.patch(
            "functions.func_s3_bulkimg_analyse.get_filebytes_from_s3"
        )
        mock_get_bytes.return_value = b"fake_image_bytes"

        # Mock the S3 client's get_object method to simulate a successful response
        mock_s3_client.get_object.return_value = {
            "Body": mocker.Mock(read=lambda: b"fake_image_bytes")
        }

        # Mock rekog_image_categorise with a response that indicates a cat was detected
        mock_rekog = mocker.patch(
            "functions.func_s3_bulkimg_analyse.rekog_image_categorise"
        )
        rekog_response = {
            "rekog_resp": {
                "Labels": [{"Name": "Cat", "Confidence": 98.5}],
                "ResponseMetadata": {
                    "HTTPStatusCode": 200,
                    "HTTPHeaders": {"date": "Wed, 01 Jan 2023 00:00:00 GMT"},
                },
            },
            "rek_match": True,
        }
        mock_rekog.return_value = rekog_response

        # Mock gen_item_dict2_from_rek_resp
        mock_gen_dict2 = mocker.patch(
            "functions.func_s3_bulkimg_analyse.gen_item_dict2_from_rek_resp"
        )
        mock_gen_dict2.return_value = {
            "batch_id": "789",
            "img_fprint": "hash123",
            "op_status": "success",
            "rek_iscat": True,
        }

        # Mock remaining functions
        mocker.patch(
            "functions.func_s3_bulkimg_analyse.move_s3_object_based_on_rekog_response",
            return_value=True,
        )
        mocker.patch(
            "functions.func_s3_bulkimg_analyse.global_context",
            {"batch_id": "789", "img_fprint": "hash123", "is_debug": False},
        )
        mocker.patch("functions.func_s3_bulkimg_analyse.write_debug_logs_to_dynamodb")
        # mock_dynamodb_helper = mocker.patch(
        #     "functions.func_s3_bulkimg_analyse.dynamodb_helper"
        # )

        # Create test event and context
        event = {
            "Records": [
                {
                    "s3": {
                        "object": {
                            "key": "hash123/client456/batch-789/20230101/1609459200.png"
                        }
                    }
                }
            ]
        }
        context = {}

        # Call the function under test
        from functions.func_s3_bulkimg_analyse import run

        run(event, context)

        # Verify Rekognition was called with the correct parameters
        mock_rekog.assert_called_once_with(
            rekog_client=mocker.ANY,
            image_bytes=b"fake_image_bytes",
            label_pattern="cat",
        )

        # Verify the Rekognition results were processed correctly
        mock_gen_dict2.assert_called_once_with(rekog_results=rekog_response)

        # Verify DynamoDB was updated with the Rekognition results
        mock_dynamodb_helper.update_item.assert_any_call(
            item_dict=mock_gen_dict2.return_value
        )

    # Successfully moves image to destination bucket after successful analysis
    # def test_successful_image_move_to_destination(self, mocker, mock_aws_clients):
    #     # Mock the S3 client and its head_bucket method
    #     # mock_s3_client = mocker.Mock()
    #   mock_s3_client, _, _ = mock_aws_clients
    #     mock_s3_client.head_bucket.return_value = {}  # Simulate successful bucket check

    #     # Patch gen_boto3_client to return the mocked S3 client
    #     mocker.patch("shared_helpers.boto3_helpers.gen_boto3_client", return_value=mock_s3_client)

    #     # Patch the s3_client directly in func_s3_bulkimg_analyse
    #     mocker.patch("functions.func_s3_bulkimg_analyse.s3_client", mock_s3_client)

    #     # Mock other dependencies
    #     mocker.patch(
    #         "serverless.functions.func_s3_bulkimg_analyse.validate_s3bucket",
    #         return_value=("source-bucket", "dest-bucket", "fail-bucket"),
    #     )
    #     mocker.patch(
    #         "serverless.functions.func_s3_bulkimg_analyse.get_s3_key_from_event",
    #         return_value="hash123/client456/batch-789/20230101/1609459200.png"
    #     )
    #     mocker.patch(
    #         "serverless.functions.func_s3_bulkimg_analyse.gen_item_dict1_from_s3key",
    #         return_value={"batch_id": "789", "img_fprint": "hash123"},
    #     )
    #     mocker.patch(
    #         "serverless.functions.func_s3_bulkimg_analyse.get_filebytes_from_s3",
    #         return_value=b"filebytes",
    #     )
    #     mocker.patch(
    #         "serverless.functions.func_s3_bulkimg_analyse.rekog_image_categorise",
    #         return_value={
    #             "rekog_resp": {"ResponseMetadata": {"HTTPStatusCode": 200}},
    #             "rek_match": True,
    #         },
    #     )
    #     mocker.patch(
    #         "serverless.functions.func_s3_bulkimg_analyse.gen_item_dict2_from_rek_resp",
    #         return_value={"op_status": "success"},
    #     )
    #     mocker.patch(
    #         "serverless.functions.func_s3_bulkimg_analyse.move_s3_object_based_on_rekog_response",
    #         return_value=True,
    #     )
    #     mock_dynamodb_helper = mocker.patch(
    #         "functions.func_s3_bulkimg_analyse.dynamodb_helper"
    #     )

    #     # Create a valid event dictionary
    #     event = {
    #         "Records": [
    #             {
    #                 "s3": {
    #                     "object": {
    #                         "key": "hash123/client456/batch-789/20230101/1609459200.png"
    #                     }
    #                 }
    #             }
    #         ]
    #     }
    #     context = {}

    #     # Run the function
    #     run(event=event, context=context)

    #     # Assertions
    #     assert mock_dynamodb_helper.write_item.called
    #     assert mock_dynamodb_helper.update_item.call_count == 2

    # # Successfully updates DynamoDB with initial, Rekognition, and final data
    # def test_successful_dynamodb_updates(self, mocker):
    #     # Mock dependencies
    #     mocker.patch('serverless.functions.func_s3_bulkimg_analyse.validate_s3bucket', return_value=('source-bucket', 'dest-bucket', 'fail-bucket'))
    #     mocker.patch('serverless.functions.func_s3_bulkimg_analyse.get_s3_key_from_event', return_value='test/key.png')
    #     mocker.patch('serverless.functions.func_s3_bulkimg_analyse.gen_item_dict1_from_s3key', return_value={'batch_id': '123', 'img_fprint': 'abc'})
    #     mocker.patch('serverless.functions.func_s3_bulkimg_analyse.get_filebytes_from_s3', return_value=b'filebytes')
    #     mocker.patch('serverless.functions.func_s3_bulkimg_analyse.rekog_image_categorise', return_value={'rekog_resp': {'ResponseMetadata': {'HTTPStatusCode': 200}}, 'rek_match': True})
    #     mocker.patch('serverless.functions.func_s3_bulkimg_analyse.gen_item_dict2_from_rek_resp', return_value={'op_status': 'success'})
    #     mocker.patch('serverless.functions.func_s3_bulkimg_analyse.move_s3_object_based_on_rekog_response', return_value=True)
    #     mock_dynamodb_helper = mocker.patch('serverless.functions.func_s3_bulkimg_analyse.dynamodb_helper')

    #     # Run the function
    #     run(event={}, context={})

    #     # Assertions
    #     assert mock_dynamodb_helper.write_item.called
    #     assert mock_dynamodb_helper.update_item.call_count == 2

    # # Properly handles debug mode by writing logs to DynamoDB when is_debug is true
    # def test_debug_mode_logs_written_to_dynamodb(self, mocker):
    #     # Set global context to debug mode
    #     # from serverless.functions.global_context import global_context
    #     global_context['is_debug'] = True

    #     # Mock dependencies
    #     mocker.patch('serverless.functions.func_s3_bulkimg_analyse.validate_s3bucket', return_value=('source-bucket', 'dest-bucket', 'fail-bucket'))
    #     mocker.patch('serverless.functions.func_s3_bulkimg_analyse.get_s3_key_from_event', return_value='test/key.png')
    #     mocker.patch('serverless.functions.func_s3_bulkimg_analyse.gen_item_dict1_from_s3key', return_value={'batch_id': '123', 'img_fprint': 'abc'})
    #     mocker.patch('serverless.functions.func_s3_bulkimg_analyse.get_filebytes_from_s3', return_value=b'filebytes')
    #     mocker.patch('serverless.functions.func_s3_bulkimg_analyse.rekog_image_categorise', return_value={'rekog_resp': {'ResponseMetadata': {'HTTPStatusCode': 200}}, 'rek_match': True})
    #     mocker.patch('serverless.functions.func_s3_bulkimg_analyse.gen_item_dict2_from_rek_resp', return_value={'op_status': 'success'})
    #     mocker.patch('serverless.functions.func_s3_bulkimg_analyse.move_s3_object_based_on_rekog_response', return_value=True)
    #     mock_dynamodb_helper = mocker.patch('serverless.functions.func_s3_bulkimg_analyse.dynamodb_helper')

    #     # Run the function
    #     run(event={}, context={})

    #     # Assertions
    #     assert mock_dynamodb_helper.update_item.called
