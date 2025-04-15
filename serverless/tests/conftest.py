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
import pytest

from serverless.functions.global_context import global_context

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
