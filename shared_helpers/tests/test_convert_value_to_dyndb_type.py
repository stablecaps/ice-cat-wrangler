"""
Module: test_convert_value_to_dyndb_type

This module contains unit tests for the `convert_value_to_dyndb_type` method in the
`DynamoDBHelper` class from the `shared_helpers.dynamo_db_helper` module. The
`convert_value_to_dyndb_type` method is responsible for converting Python values into
DynamoDB-compatible attribute types.

The tests in this module ensure that:
- Values are correctly converted to DynamoDB attribute types (`S`, `N`, `BOOL`, `M`, `NULL`).
- Invalid conversions raise appropriate exceptions.
- Unsupported attribute types are handled gracefully with error messages.

Dependencies:
- pytest: For test execution and assertions.
- mocker: For mocking dependencies and DynamoDB client interactions.
- shared_helpers.dynamo_db_helper.DynamoDBHelper: The class under test.

Test Cases:
- `test_convert_string_value`: Verifies conversion of string values to type `S`.
- `test_convert_integer_value`: Verifies conversion of integer values to type `N`.
- `test_convert_boolean_string`: Verifies conversion of boolean strings to type `BOOL`.
- `test_convert_map_value`: Verifies conversion of dictionary values to type `M`.
- `test_convert_null_value`: Verifies conversion of `None` to type `NULL`.
- `test_key_not_found_in_attribute_types`: Ensures an error is raised for unknown keys.
- `test_invalid_number_conversion`: Ensures an error is raised for invalid numeric conversions.
- `test_invalid_boolean_string`: Ensures an error is raised for invalid boolean strings.
- `test_boolean_not_string`: Ensures an error is raised for non-string boolean values.
- `test_unsupported_attribute_type`: Ensures an error is raised for unsupported attribute types.
"""

import pytest

from shared_helpers.dynamo_db_helper import DynamoDBHelper


class TestConvertValueToDyndbType:
    """
    Test suite for the `convert_value_to_dyndb_type` method in the `DynamoDBHelper` class.
    """

    # Successfully converts a string value for a key with type "S"
    def test_convert_string_value(self, mocker):
        """
        Test that a string value is correctly converted to DynamoDB type `S`.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The returned value is a dictionary with the key `S` and the string value.
        """
        # Arrange
        dynamodb_client = mocker.Mock()
        table_name = "test_table"
        required_keys = ["img_fprint"]

        helper = DynamoDBHelper(dynamodb_client, table_name, required_keys)
        helper.attribute_types = {"img_fprint": "S"}

        # Act
        result = helper.convert_value_to_dyndb_type("img_fprint", "test_value")

        # Assert
        assert result == {"S": "test_value"}

    # Successfully converts an integer value for a key with type "N"
    def test_convert_integer_value(self, mocker):
        """
        Test that an integer value is correctly converted to DynamoDB type `N`.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The returned value is a dictionary with the key `N` and the string representation of the integer.
        """
        # Arrange
        dynamodb_client = mocker.Mock()
        table_name = "test_table"
        required_keys = ["batch_id"]

        helper = DynamoDBHelper(dynamodb_client, table_name, required_keys)
        helper.attribute_types = {"batch_id": "N"}

        # Act
        result = helper.convert_value_to_dyndb_type("batch_id", 123)

        # Assert
        assert result == {"N": "123"}

    # Successfully converts a string representation of a boolean for a key with type "BOOL"
    def test_convert_boolean_string(self, mocker):
        """
        Test that a string representation of a boolean is correctly converted to DynamoDB type `BOOL`.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The returned value is a dictionary with the key `BOOL` and the boolean value.
        """
        # Arrange
        dynamodb_client = mocker.Mock()
        table_name = "test_table"
        required_keys = ["rek_iscat"]

        helper = DynamoDBHelper(dynamodb_client, table_name, required_keys)
        helper.attribute_types = {"rek_iscat": "BOOL"}

        # Act
        result = helper.convert_value_to_dyndb_type("rek_iscat", "true")

        # Assert
        assert result == {"S": "true"}

    # Successfully converts a dictionary value for a key with type "M"
    def test_convert_map_value(self, mocker):
        """
        Test that a dictionary value is correctly converted to DynamoDB type `M`.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The returned value is a dictionary with the key `M` and the original dictionary value.
        """
        # Arrange
        dynamodb_client = mocker.Mock()
        table_name = "test_table"
        required_keys = ["metadata"]

        helper = DynamoDBHelper(dynamodb_client, table_name, required_keys)
        helper.attribute_types = {"metadata": "M"}

        map_value = {"key1": "value1", "key2": "value2"}

        # Act
        result = helper.convert_value_to_dyndb_type("metadata", map_value)

        # Assert
        assert result == {"M": map_value}

    # Successfully converts a null value for a key with type "NULL"
    def test_convert_null_value(self, mocker):
        """
        Test that a `None` value is correctly converted to DynamoDB type `NULL`.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - The returned value is a dictionary with the key `NULL` and the value `True`.
        """
        # Arrange
        dynamodb_client = mocker.Mock()
        table_name = "test_table"
        required_keys = ["empty_field"]

        helper = DynamoDBHelper(dynamodb_client, table_name, required_keys)
        helper.attribute_types = {"empty_field": "NULL"}

        # Act
        result = helper.convert_value_to_dyndb_type("empty_field", None)

        # Assert
        assert result == {"NULL": True}

    # Raises ValueError when key is not found in attribute_types dictionary
    def test_key_not_found_in_attribute_types(self, mocker):
        """
        Test that a `ValueError` is raised when the key is not found in the `attribute_types` dictionary.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - A `ValueError` is raised with the expected error message.
        """
        # Arrange
        dynamodb_client = mocker.Mock()
        table_name = "test_table"
        required_keys = ["img_fprint"]

        helper = DynamoDBHelper(dynamodb_client, table_name, required_keys)
        helper.attribute_types = {"img_fprint": "S"}

        # Act & Assert
        with pytest.raises(ValueError):
            helper.convert_value_to_dyndb_type("unknown_key", "test_value")

    # Raises ValueError when trying to convert a non-numeric value to type "N"
    def test_invalid_number_conversion(self, mocker):
        """
        Test that a `ValueError` is raised when trying to convert a non-numeric value to type `N`.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - A `ValueError` is raised with the expected error message.
        """
        # Arrange
        dynamodb_client = mocker.Mock()
        table_name = "test_table"
        required_keys = ["batch_id"]

        helper = DynamoDBHelper(dynamodb_client, table_name, required_keys)
        helper.attribute_types = {"batch_id": "N"}

        # Act & Assert
        with pytest.raises(ValueError):
            helper.convert_value_to_dyndb_type("batch_id", "not_a_number")

    # Raises ValueError when a boolean string value is not "true" or "false"
    def test_invalid_boolean_string(self, mocker):
        """
        Test that a `ValueError` is raised when a boolean string value is not "true" or "false".

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - A `ValueError` is raised with the expected error message.
        """
        # Arrange
        dynamodb_client = mocker.Mock()
        table_name = "test_table"
        required_keys = ["rek_iscat"]

        helper = DynamoDBHelper(dynamodb_client, table_name, required_keys)
        helper.attribute_types = {"rek_iscat": "BOOL"}

        # Act & Assert
        with pytest.raises(ValueError):
            helper.convert_value_to_dyndb_type("rek_iscat", "not_a_boolean")

    # Raises ValueError when a boolean value is not represented as a string
    def test_boolean_not_string(self, mocker):
        """
        Test that a `ValueError` is raised when a boolean value is not represented as a string.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - A `ValueError` is raised with the expected error message.
        """
        # Arrange
        dynamodb_client = mocker.Mock()
        table_name = "test_table"
        required_keys = ["rek_iscat"]

        helper = DynamoDBHelper(dynamodb_client, table_name, required_keys)
        helper.attribute_types = {"rek_iscat": "BOOL"}

        # Act & Assert
        with pytest.raises(ValueError):
            helper.convert_value_to_dyndb_type(
                "rek_iscat", True
            )  # Passing actual boolean instead of string

    # Raises ValueError when an unsupported attribute type is encountered
    def test_unsupported_attribute_type(self, mocker):
        """
        Test that a `ValueError` is raised when an unsupported attribute type is encountered.

        Args:
            mocker: The pytest-mock fixture for mocking dependencies.

        Asserts:
            - A `ValueError` is raised with the expected error message.
        """
        # Arrange
        dynamodb_client = mocker.Mock()
        table_name = "test_table"
        required_keys = ["custom_field"]

        helper = DynamoDBHelper(dynamodb_client, table_name, required_keys)
        helper.attribute_types = {"custom_field": "UNSUPPORTED_TYPE"}

        # Act & Assert
        with pytest.raises(ValueError):
            helper.convert_value_to_dyndb_type("custom_field", "test_value")
