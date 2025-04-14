# import os
# import sys
# import pytest
# from unittest.mock import patch, MagicMock
# from moto import mock_aws
# import boto3


# from functions.func_s3_bulkimg_analyse import run

# @pytest.fixture
# def aws_credentials():
#     """Mocked AWS Credentials for moto."""
#     os.environ["AWS_ACCESS_KEY_ID"] = "testing"
#     os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
#     os.environ["AWS_SECURITY_TOKEN"] = "testing"
#     os.environ["AWS_SESSION_TOKEN"] = "testing"

#     # Set required environment variables for S3 buckets
#     os.environ["s3bucketSource"] = "source-bucket"
#     os.environ["s3bucketDest"] = "destination-bucket"
#     os.environ["s3bucketFail"] = "failure-bucket"

# @pytest.fixture
# def aws_setup(aws_credentials):
#     with mock_aws():
#         # Setup S3
#         s3 = boto3.client('s3', region_name='us-east-1')
#         s3.create_bucket(Bucket='source-bucket')
#         s3.create_bucket(Bucket='destination-bucket')
#         s3.create_bucket(Bucket='failure-bucket')
#         s3.put_object(Bucket='source-bucket', Key='73f3355aa775e1ae2d474961b754471dcbf05053cc55504517445f255437f8cc/stablecaps900/batch-1744585329/2025-04-13-23/1744585329-debug.png', Body=b'test data')

#         # Setup DynamoDB
#         dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
#         table = dynamodb.create_table(
#             TableName='test-table',
#             KeySchema=[
#                 {'AttributeName': 'batch_id', 'KeyType': 'HASH'},
#                 {'AttributeName': 'img_fprint', 'KeyType': 'RANGE'}
#             ],
#             AttributeDefinitions=[
#                 {'AttributeName': 'batch_id', 'AttributeType': 'S'},
#                 {'AttributeName': 'img_fprint', 'AttributeType': 'S'}
#             ],
#             ProvisionedThroughput={'ReadCapacityUnits': 1, 'WriteCapacityUnits': 1}
#         )

#         # Mock Rekognition's create_collection
#         with patch('boto3.client') as mock_boto3_client:
#             mock_rekognition = MagicMock()
#             mock_boto3_client.return_value = mock_rekognition
#             mock_rekognition.create_collection.return_value = {
#                 "StatusCode": 200,
#                 "CollectionArn": "arn:aws:rekognition:us-east-1:123456789012:collection/test-collection",
#                 "FaceModelVersion": "3.0"
#             }
#             yield s3, table, mock_rekognition

# @patch('functions.func_s3_bulkimg_analyse.dynamodb_helper')
# @patch('functions.func_s3_bulkimg_analyse.get_s3_key_from_event')
# def test_run_success(mock_get_s3_key, mock_dynamodb_helper, aws_setup):
#     # Mock function calls
#     mock_get_s3_key.return_value = '73f3355aa775e1ae2d474961b754471dcbf05053cc55504517445f255437f8cc/stablecaps900/batch-1744585329/2025-04-13-23/1744585329-debug.png'
#     mock_dynamodb_helper.write_item = MagicMock()
#     mock_dynamodb_helper.update_item = MagicMock()

#     # Create a mock event
#     event = {
#         'Records': [{
#             's3': {
#                 'bucket': {'name': 'source-bucket'},
#                 'object': {'key': '73f3355aa775e1ae2d474961b754471dcbf05053cc55504517445f255437f8cc/stablecaps900/batch-1744585329/2025-04-13-23/1744585329-debug.png'}
#             }
#         }]
#     }

#     # Run the function
#     run(event, None)

#     # Assertions
#     mock_get_s3_key.assert_called_once_with(event=event)
#     mock_dynamodb_helper.write_item.assert_called()
#     mock_dynamodb_helper.update_item.assert_called()
