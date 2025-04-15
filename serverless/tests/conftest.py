# filepath: /media/bsgt/jogi/XX_local_PSYNC_linux2/000_GIT_REPOS/0000_STABLECAPS_GITREPOS/ice-cat-wrangler/serverless/tests/conftest.py
import os
import sys

# Add the project root directory to sys.path
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.insert(0, repo_root)

# Add the shared_helpers directory to sys.path
shared_helpers_path = os.path.abspath(os.path.join(repo_root, "shared_helpers"))
sys.path.insert(0, shared_helpers_path)


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../shared_helpers"))
)
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../shared_helpers/shared_helpers")
    ),
)
from unittest.mock import MagicMock

import pytest

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
    """
    global_context["batch_id"] = None
    global_context["img_fprint"] = None
    global_context["is_debug"] = False


@pytest.fixture(autouse=True)
def set_env_vars():
    """Fixture to set environment variables for tests."""
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
