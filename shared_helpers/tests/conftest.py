"""
Module: conftest

This module contains shared configuration and fixtures for pytest test cases in the project.
It sets up the Python path to include the project root and the `shared_helpers` directory,
allowing test modules to import project-specific modules without modifying their paths.

The configurations in this module ensure that:
- The project root directory is added to `sys.path` for easy imports of project modules.
- The `shared_helpers` directory is added to `sys.path` for importing helper modules.

Dependencies:
- pytest: For test execution and fixture management.
- os: For handling file and directory paths.
- sys: For modifying the Python path.

This module does not define any test cases or fixtures directly but provides the necessary
setup for the test environment.
"""

import os
import sys

# Add the project root directory to sys.path
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.insert(0, repo_root)

# Add the shared_helpers directory to sys.path
shared_helpers_path = os.path.abspath(os.path.join(repo_root, "shared_helpers"))
sys.path.insert(0, shared_helpers_path)
