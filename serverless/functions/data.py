"""
data.py

This module contains constants and utilities for handling data operations
in the Ice Cat Wrangler project. It defines required keys for DynamoDB
operations and may include additional data-related functionality.

Constants:
    required_dyndb_keys (list): A list of required keys for DynamoDB operations.

Example:
    Use `required_dyndb_keys` to validate the presence of necessary keys
    in a DynamoDB item:

        if all(key in item for key in required_dyndb_keys):
            print("Item is valid.")
"""

required_dyndb_keys = ["batch_id", "img_fprint"]
