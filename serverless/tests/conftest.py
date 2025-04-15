"""
Module: conftest

This module provides shared configurations, fixtures, and setup logic for the test suite.
It is automatically loaded by pytest and is used to configure the test environment,
mock dependencies, and provide reusable fixtures for tests.

The configurations and fixtures in this module ensure that:
- The global context is reset before each test to avoid interference between tests.
- Required environment variables are set and cleaned up after each test.
- AWS clients (S3, Rekognition, DynamoDB) are mocked for isolated testing.
- Common helper functions and dependencies are mocked where necessary.

Dependencies:
- pytest: For test execution and fixture management.
- mocker: For mocking dependencies and environment variables.
- serverless.functions.global_context: The global context used across the application.

Fixtures:
- `reset_global_context`: Resets the global context before each test.
- `set_env_vars`: Sets required environment variables for tests.
- `mock_aws_clients`: Provides mocked AWS clients for S3, Rekognition, and DynamoDB.
- `mock_dynamodb_helper`: Mocks the DynamoDBHelper object.
"""

import os
import sys

import pytest

# Add the project root directory to sys.path
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.insert(0, repo_root)

# Add the shared_helpers directory to sys.path
shared_helpers_path = os.path.abspath(os.path.join(repo_root, "shared_helpers"))
sys.path.insert(0, shared_helpers_path)

# Add the serverless directory to sys.path
serverless_path = os.path.abspath(os.path.join(repo_root, "serverless"))
sys.path.insert(0, serverless_path)

# Add the tests directory to sys.path
tests_path = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, tests_path)

# Add the modules directory to sys.path (if needed)
modules_path = os.path.abspath(os.path.join(repo_root, "modules"))
sys.path.insert(0, modules_path)


from serverless.functions.global_context import global_context

### constants
bucket_names = {
    "s3bucketSource": "source-bucket",
    "s3bucketDest": "dest-bucket",
    "s3bucketFail": "fail-bucket",
}


### Fixtures
@pytest.fixture(autouse=True)
def reset_global_context():
    """
    Reset the global_context before each test to avoid test interference.

    This fixture ensures that the `global_context` dictionary is reset to its default
    state before each test, preventing data leakage between tests.

    Modifies:
        - `global_context`: Resets `batch_id`, `img_fprint`, and `is_debug` to their default values.
    """
    global_context["batch_id"] = None
    global_context["img_fprint"] = None
    global_context["is_debug"] = False


@pytest.fixture(autouse=True)
def set_env_vars():
    """
    Set required environment variables for tests.

    This fixture sets the necessary environment variables for the test suite and
    ensures they are cleaned up after each test.

    Environment Variables:
        - `s3bucketSource`: The source S3 bucket name.
        - `s3bucketDest`: The destination S3 bucket name.
        - `s3bucketFail`: The failure S3 bucket name.

    Yields:
        None: Allows the test to run with the environment variables set.

    Cleans Up:
        - Removes the environment variables after the test.
    """
    # Set the required environment variables
    os.environ["s3bucketSource"] = "source-bucket"
    os.environ["s3bucketDest"] = "dest-bucket"
    os.environ["s3bucketFail"] = "fail-bucket"

    # Yield to allow the test to run
    yield

    # Cleanup: Remove the environment variables after the test
    del os.environ["s3bucketSource"]
    del os.environ["s3bucketDest"]
    del os.environ["s3bucketFail"]


@pytest.fixture
def mock_aws_clients(mocker):
    """
    Mock AWS clients (S3, Rekognition, DynamoDB).

    This fixture provides mocked AWS clients for S3, Rekognition, and DynamoDB,
    allowing tests to simulate AWS interactions without making actual API calls.

    Args:
        mocker: The pytest-mock fixture for mocking dependencies.

    Returns:
        tuple: A tuple containing mocked S3, Rekognition, and DynamoDB clients.
    """
    mock_s3_client = mocker.Mock()
    mock_rekog_client = mocker.Mock()
    mock_dyndb_client = mocker.Mock()

    mocker.patch(
        "functions.func_s3_bulkimg_analyse.gen_boto3_client",
        side_effect=lambda service, region=None: {
            "s3": mock_s3_client,
            "rekognition": mock_rekog_client,
            "dynamodb": mock_dyndb_client,
        }[service],
    )

    return mock_s3_client, mock_rekog_client, mock_dyndb_client


@pytest.fixture
def mock_dynamodb_helper(mocker):
    """
    Mock the DynamoDBHelper object.

    This fixture provides a mocked DynamoDBHelper object, allowing tests to simulate
    DynamoDB interactions without making actual API calls.

    Args:
        mocker: The pytest-mock fixture for mocking dependencies.

    Returns:
        MagicMock: A mocked DynamoDBHelper object.
    """
    return mocker.patch("functions.func_s3_bulkimg_analyse.dynamodb_helper")


# @pytest.fixture
# def mock_common_functions(mocker):
#     """
#     Mock common helper functions used in tests.
#     """
#     mocker.patch(
#         "functions.func_s3_bulkimg_analyse.validate_s3bucket",
#         return_value=("source-bucket", "dest-bucket", "fail-bucket"),
#     )
#     mocker.patch(
#         "functions.func_s3_bulkimg_analyse.get_s3_key_from_event",
#         return_value="hash123/client456/batch-789/20230101/1609459200.png",
#     )
#     mocker.patch(
#         "functions.func_s3_bulkimg_analyse.gen_item_dict1_from_s3key",
#         return_value={"batch_id": "789", "img_fprint": "hash123"},
#     )
#     mocker.patch(
#         "functions.func_s3_bulkimg_analyse.get_filebytes_from_s3",
#         return_value={"Body": MagicMock(read=lambda: b"filebytes")},
#     )
#     mocker.patch(
#         "functions.func_s3_bulkimg_analyse.rekog_image_categorise",
#         return_value={
#             "rekog_resp": {"ResponseMetadata": {"HTTPStatusCode": 200}},
#             "rek_match": True,
#         },
#     )
#     mocker.patch(
#         "functions.func_s3_bulkimg_analyse.gen_item_dict2_from_rek_resp",
#         return_value={"op_status": "success"},
#     )
#     mocker.patch(
#         "functions.func_s3_bulkimg_analyse.move_s3_object_based_on_rekog_response",
#         return_value=True,
#     )
