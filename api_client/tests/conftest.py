# filepath: /media/bsgt/jogi/XX_local_PSYNC_linux2/000_GIT_REPOS/0000_STABLECAPS_GITREPOS/ice-cat-wrangler/serverless/tests/conftest.py
import os
import sys

# Add the project root directory to sys.path
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.insert(0, repo_root)

# Add the shared_helpers directory to sys.path
shared_helpers_path = os.path.abspath(os.path.join(repo_root, "shared_helpers"))
sys.path.insert(0, shared_helpers_path)


shared_helpers_path2 = os.path.abspath(
    os.path.join(shared_helpers_path, "shared_helpers")
)
sys.path.insert(0, shared_helpers_path2)

print("sys.path:", sys.path)
