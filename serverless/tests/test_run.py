# import pytest
# from moto import mock_aws
# import boto3

# class TestRun:

#     @mock_aws
#     def test_validates_s3_buckets_and_retrieves_key(self, mocker):
#         # Mock dependencies
#         mock_s3_client = boto3.client("s3", region_name="us-east-1")
#         mock_rekog_client = mocker.Mock()
#         mock_dyndb_client = boto3.client("dynamodb", region_name="us-east-1")
#         mock_dynamodb_helper = mocker.Mock()

#         # Create mock S3 buckets
#         mock_s3_client.create_bucket(Bucket="source-bucket")
#         mock_s3_client.create_bucket(Bucket="dest-bucket")
#         mock_s3_client.create_bucket(Bucket="fail-bucket")

#         # Create mock DynamoDB table
#         mock_dyndb_client.create_table(
#             TableName="test-dynamodb-table",
#             KeySchema=[
#                 {"AttributeName": "batch_id", "KeyType": "HASH"},  # Partition key
#                 {"AttributeName": "img_fprint", "KeyType": "RANGE"},  # Sort key
#             ],
#             AttributeDefinitions=[
#                 {"AttributeName": "batch_id", "AttributeType": "S"},
#                 {"AttributeName": "img_fprint", "AttributeType": "S"},
#             ],
#             ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
#         )

#         # Mock boto3 client generation
#         mocker.patch('serverless.functions.func_s3_bulkimg_analyse.gen_boto3_client', side_effect=lambda service, region:
#             mock_s3_client if service == 's3' else mock_dyndb_client if service == 'dynamodb' else mock_rekog_client)
#         mocker.patch('serverless.functions.func_s3_bulkimg_analyse.DynamoDBHelper', return_value=mock_dynamodb_helper)

#         # Mock environment variables for S3 buckets and DynamoDB table
#         mocker.patch('os.getenv', side_effect=lambda key, default=None: {
#             "s3bucketSource": "source-bucket",
#             "s3bucketDest": "dest-bucket",
#             "s3bucketFail": "fail-bucket",
#             "dynamoDBTableName": "test-dynamodb-table"  # Mock DynamoDB table name
#         }.get(key, default))

#         # Create spies for the validation functions
#         mock_validate_s3bucket = mocker.patch('serverless.functions.func_s3_bulkimg_analyse.validate_s3bucket',
#             return_value=('source-bucket', 'dest-bucket', 'fail-bucket'))
#         mock_get_s3_key = mocker.patch('serverless.functions.func_s3_bulkimg_analyse.get_s3_key_from_event',
#             return_value='hash123/client456/batch-789/20230101/1672531200.png')

#         # Mock remaining helper functions to avoid errors
#         mocker.patch('serverless.functions.func_s3_bulkimg_analyse.gen_item_dict1_from_s3key',
#             return_value={'batch_id': '789', 'img_fprint': 'hash123', 'op_status': 'pending'})
#         mocker.patch('serverless.functions.func_s3_bulkimg_analyse.get_filebytes_from_s3',
#             return_value=b'image_bytes')
#         mocker.patch('serverless.functions.func_s3_bulkimg_analyse.rekog_image_categorise',
#             return_value={'rekog_resp': {'Labels': [], 'ResponseMetadata': {'HTTPStatusCode': 200}}, 'rek_match': True})
#         mocker.patch('serverless.functions.func_s3_bulkimg_analyse.gen_item_dict2_from_rek_resp',
#             return_value={'batch_id': '789', 'img_fprint': 'hash123', 'op_status': 'success'})
#         mocker.patch('serverless.functions.func_s3_bulkimg_analyse.move_s3_object_based_on_rekog_response',
#             return_value=True)
#         mocker.patch('serverless.functions.func_s3_bulkimg_analyse.write_debug_logs_to_dynamodb')

#         # Create test event and context
#         event = {'Records': [{'s3': {'object': {'key': 'hash123/client456/batch-789/20230101/1672531200.png'}}}]}
#         context = mocker.Mock()

#         # Call the function
#         from functions.func_s3_bulkimg_analyse import run
#         run(event, context)

#         # Verify the validation functions were called with correct parameters
#         mock_validate_s3bucket.assert_called_once_with(s3_client=mock_s3_client)
#         mock_get_s3_key.assert_called_once_with(event=event)

# # Validates S3 buckets and retrieves S3 key from event
# def test_validates_s3_buckets_and_retrieves_key(self, mocker):
#     # Mock dependencies
#     mock_s3_client = mocker.Mock()
#     mock_rekog_client = mocker.Mock()
#     mock_dyndb_client = mocker.Mock()
#     mock_dynamodb_helper = mocker.Mock()

#     # Mock boto3 client generation
#     mocker.patch('serverless.functions.func_s3_bulkimg_analyse.gen_boto3_client', side_effect=lambda service, region:
#         mock_s3_client if service == 's3' else mock_rekog_client)
#     mocker.patch('serverless.functions.func_s3_bulkimg_analyse.DynamoDBHelper', return_value=mock_dynamodb_helper)

#     # Mock environment variables for S3 buckets
#     mocker.patch('os.getenv', side_effect=lambda key, default=None: {
#         "s3bucketSource": "source-bucket",
#         "s3bucketDest": "dest-bucket",
#         "s3bucketFail": "fail-bucket"
#     }.get(key, default))

#     # Create spies for the validation functions
#     mock_validate_s3bucket = mocker.patch('serverless.functions.func_s3_bulkimg_analyse.validate_s3bucket',
#         return_value=('source-bucket', 'dest-bucket', 'fail-bucket'))
#     mock_get_s3_key = mocker.patch('serverless.functions.func_s3_bulkimg_analyse.get_s3_key_from_event',
#         return_value='hash123/client456/batch-789/20230101/1672531200.png')

#     # Mock remaining helper functions to avoid errors
#     mocker.patch('serverless.functions.func_s3_bulkimg_analyse.gen_item_dict1_from_s3key',
#         return_value={'batch_id': '789', 'img_fprint': 'hash123', 'op_status': 'pending'})
#     mocker.patch('serverless.functions.func_s3_bulkimg_analyse.get_filebytes_from_s3',
#         return_value=b'image_bytes')
#     mocker.patch('serverless.functions.func_s3_bulkimg_analyse.rekog_image_categorise',
#         return_value={'rekog_resp': {'Labels': [], 'ResponseMetadata': {'HTTPStatusCode': 200}}, 'rek_match': True})
#     mocker.patch('serverless.functions.func_s3_bulkimg_analyse.gen_item_dict2_from_rek_resp',
#         return_value={'batch_id': '789', 'img_fprint': 'hash123', 'op_status': 'success'})
#     mocker.patch('serverless.functions.func_s3_bulkimg_analyse.move_s3_object_based_on_rekog_response',
#         return_value=True)
#     mocker.patch('serverless.functions.func_s3_bulkimg_analyse.write_debug_logs_to_dynamodb')

#     # Create test event and context
#     event = {'Records': [{'s3': {'object': {'key': 'hash123/client456/batch-789/20230101/1672531200.png'}}}]}
#     context = mocker.Mock()

#     # Call the function
#     from functions.func_s3_bulkimg_analyse import run
#     run(event, context)

#     # Verify the validation functions were called with correct parameters
#     mock_validate_s3bucket.assert_called_once_with(s3_client=mock_s3_client)
#     mock_get_s3_key.assert_called_once_with(event=event)

# # Writes initial record to DynamoDB with pending status
# def test_writes_initial_record_to_dynamodb(self, mocker):
#     # Mock dependencies
#     mock_s3_client = mocker.Mock()
#     mock_rekog_client = mocker.Mock()
#     mock_dyndb_client = mocker.Mock()
#     mock_dynamodb_helper = mocker.Mock()

#     # Mock boto3 client generation
#     mocker.patch('serverless.functions.func_s3_bulkimg_analyse.gen_boto3_client', side_effect=lambda service, region:
#         mock_s3_client if service == 's3' else mock_rekog_client)
#     mocker.patch('serverless.functions.func_s3_bulkimg_analyse.DynamoDBHelper', return_value=mock_dynamodb_helper)

#     # Mock helper functions
#     mocker.patch('serverless.functions.func_s3_bulkimg_analyse.validate_s3bucket',
#         return_value=('source-bucket', 'dest-bucket', 'fail-bucket'))
#     mocker.patch('serverless.functions.func_s3_bulkimg_analyse.get_s3_key_from_event',
#         return_value='hash123/client456/batch-789/20230101/1672531200.png')

#     # Create the expected initial item dictionary
#     expected_item_dict = {
#         'batch_id': '789',
#         'img_fprint': 'hash123',
#         'client_id': 'client456',
#         's3img_key': 'source-bucket/hash123/client456/batch-789/20230101/1672531200.png',
#         'op_status': 'pending',
#         'current_date': '20230101',
#         'upload_ts': '1672531200',
#         'ttl': mocker.ANY
#     }

#     mocker.patch('serverless.functions.func_s3_bulkimg_analyse.gen_item_dict1_from_s3key',
#         return_value=expected_item_dict)

#     # Mock remaining helper functions to avoid errors
#     mocker.patch('serverless.functions.func_s3_bulkimg_analyse.get_filebytes_from_s3',
#         return_value=b'image_bytes')
#     mocker.patch('serverless.functions.func_s3_bulkimg_analyse.rekog_image_categorise',
#         return_value={'rekog_resp': {'Labels': [], 'ResponseMetadata': {'HTTPStatusCode': 200}}, 'rek_match': True})
#     mocker.patch('serverless.functions.func_s3_bulkimg_analyse.gen_item_dict2_from_rek_resp',
#         return_value={'batch_id': '789', 'img_fprint': 'hash123', 'op_status': 'success'})
#     mocker.patch('serverless.functions.func_s3_bulkimg_analyse.move_s3_object_based_on_rekog_response',
#         return_value=True)
#     mocker.patch('serverless.functions.func_s3_bulkimg_analyse.write_debug_logs_to_dynamodb')

#     # Create test event and context
#     event = {'Records': [{'s3': {'object': {'key': 'hash123/client456/batch-789/20230101/1672531200.png'}}}]}
#     context = mocker.Mock()

#     # Call the function
#     from functions.func_s3_bulkimg_analyse import run
#     run(event, context)

#     # Verify the initial record was written to DynamoDB with the correct data
#     mock_dynamodb_helper.write_item.assert_called_once_with(item_dict=expected_item_dict)

# # Retrieves image bytes from source S3 bucket
# def test_retrieves_image_bytes_from_s3(self, mocker):
#     # Mock dependencies
#     mock_s3_client = mocker.Mock()
#     mock_rekog_client = mocker.Mock()
#     mock_dyndb_client = mocker.Mock()
#     mock_dynamodb_helper = mocker.Mock()

#     # Mock boto3 client generation
#     mocker.patch('serverless.functions.func_s3_bulkimg_analyse.gen_boto3_client', side_effect=lambda service, region:
#         mock_s3_client if service == 's3' else mock_rekog_client)
#     mocker.patch('serverless.functions.func_s3_bulkimg_analyse.DynamoDBHelper', return_value=mock_dynamodb_helper)

#     # Mock helper functions
#     s3_key = 'hash123/client456/batch-789/20230101/1672531200.png'
#     source_bucket = 'source-bucket'

#     mocker.patch('serverless.functions.func_s3_bulkimg_analyse.validate_s3bucket',
#         return_value=(source_bucket, 'dest-bucket', 'fail-bucket'))
#     mocker.patch('serverless.functions.func_s3_bulkimg_analyse.get_s3_key_from_event',
#         return_value=s3_key)
#     mocker.patch('serverless.functions.func_s3_bulkimg_analyse.gen_item_dict1_from_s3key',
#         return_value={'batch_id': '789', 'img_fprint': 'hash123', 'op_status': 'pending'})

#     # Create spy for get_filebytes_from_s3
#     mock_get_filebytes = mocker.patch('serverless.functions.func_s3_bulkimg_analyse.get_filebytes_from_s3',
#         return_value=b'image_bytes')

#     # Mock remaining helper functions to avoid errors
#     mocker.patch('serverless.functions.func_s3_bulkimg_analyse.rekog_image_categorise',
#         return_value={'rekog_resp': {'Labels': [], 'ResponseMetadata': {'HTTPStatusCode': 200}}, 'rek_match': True})
#     mocker.patch('serverless.functions.func_s3_bulkimg_analyse.gen_item_dict2_from_rek_resp',
#         return_value={'batch_id': '789', 'img_fprint': 'hash123', 'op_status': 'success'})
#     mocker.patch('serverless.functions.func_s3_bulkimg_analyse.move_s3_object_based_on_rekog_response',
#         return_value=True)
#     mocker.patch('serverless.functions.func_s3_bulkimg_analyse.write_debug_logs_to_dynamodb')

#     # Create test event and context
#     event = {'Records': [{'s3': {'object': {'key': s3_key}}}]}
#     context = mocker.Mock()

#     # Call the function
#     from functions.func_s3_bulkimg_analyse import run
#     run(event, context)

#     # Verify get_filebytes_from_s3 was called with correct parameters
#     mock_get_filebytes.assert_called_once_with(
#         s3_client=mock_s3_client,
#         bucket_name=source_bucket,
#         s3_key=s3_key
#     )
