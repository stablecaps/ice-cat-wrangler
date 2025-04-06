import os
import sys

from dotenv import load_dotenv
from rich import print

secret_vars = [
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "AWS_REGION",
    "SERVICE",
    "API_HOST",
    "ANALYSE_ENDPOINT",
    "RESULTS_ENDPOINT",
]


def construct_secrets_path(secret_filename):
    """Constructs the full path to the secrets file.

    Args:
        secret_filename (str): The name of the secrets file.

    Returns:
        str: The full path to the secrets file.
    """
    root_dir = os.getcwd()
    dotenv_path = f"{root_dir}/config/{secret_filename}"
    return dotenv_path


def check_env_variables(dotenv_path):
    """Check whether environment variables have been correctly loaded.

    This function verifies if the specified dotenv file exists and loads
    the environment variables from it. It then checks if all required
    secrets are set in the environment.

    Args:
        dotenv_path (str): The path to the dotenv file.

    Returns:
        bool: True if all required environment variables are set, False otherwise.

    Raises:
        SystemExit: If the dotenv file does not exist.

    Example:
        >>> check_env_variables("/path/to/.env")
    """

    if not os.path.isfile(dotenv_path):
        print(f"No secret file found at dotenv_path: {dotenv_path}")
        sys.exit(1)

    # load env variables
    load_dotenv(dotenv_path, override=True)

    # check to see if env variables are available to app
    passed = True
    for secret in secret_vars:
        if secret not in os.environ:
            print(f"Environment secret not set: {secret}")
            passed = False

    return passed
