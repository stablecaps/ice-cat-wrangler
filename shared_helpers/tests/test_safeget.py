"""
Module: test_safeget

This module contains unit tests for the `safeget` function in the
`shared_helpers.boto3_helpers` module. The `safeget` function is responsible
for safely retrieving a value from a nested dictionary using a sequence of keys.

The tests in this module ensure that:
- The function retrieves values correctly from single-level and nested dictionaries.
- The function handles cases where keys are missing at any level.
- The function works with dictionaries containing various data types as values.
- The function handles edge cases such as empty dictionaries, no keys provided, and non-string keys.

Dependencies:
- pytest: For test execution and assertions.
- shared_helpers.boto3_helpers.safeget: The function under test.

Test Cases:
- `test_single_level_dictionary_valid_key`: Verifies that the function retrieves a value from a single-level dictionary with a valid key.
- `test_nested_dictionary_valid_keys`: Ensures the function retrieves a value from a nested dictionary with valid keys.
- `test_returns_nested_value_when_all_keys_exist`: Verifies that the function returns the nested value when all keys in the path exist.
- `test_handles_deep_nesting`: Ensures the function handles multiple levels of nesting (3+ levels deep).
- `test_different_value_data_types`: Verifies that the function works with different data types as values (strings, numbers, lists, dicts).
- `test_returns_none_when_first_key_missing`: Ensures the function returns `None` when the first key doesn't exist.
- `test_returns_none_when_intermediate_key_missing`: Verifies that the function returns `None` when any intermediate key doesn't exist.
- `test_returns_none_with_empty_dictionary`: Ensures the function returns `None` when the dictionary is empty.
- `test_handles_no_keys_provided`: Verifies that the function handles the case when no keys are provided.
- `test_works_with_non_string_keys`: Ensures the function works with non-string keys (numbers, tuples).
"""

import pytest

from shared_helpers.boto3_helpers import safeget


class TestSafeget:
    """
    Test suite for the `safeget` function.
    """

    # Retrieves a value from a single-level dictionary with a valid key
    def test_single_level_dictionary_valid_key(self):
        """
        Test that the function retrieves a value from a single-level dictionary with a valid key.

        Asserts:
            - The returned value matches the expected value for the given key.
        """
        # Arrange
        test_dict = {"key1": "value1"}

        # Act
        result = safeget(test_dict, "key1")

        # Assert
        assert result == "value1"

    # Retrieves a value from a nested dictionary with valid keys
    def test_nested_dictionary_valid_keys(self):
        """
        Test that the function retrieves a value from a nested dictionary with valid keys.

        Asserts:
            - The returned value matches the expected nested value for the given keys.
        """
        # Arrange
        test_dict = {"level1": {"level2": "nested_value"}}

        # Act
        result = safeget(test_dict, "level1", "level2")

        # Assert
        assert result == "nested_value"

    # Returns the nested value when all keys in the path exist
    def test_returns_nested_value_when_all_keys_exist(self):
        """
        Test that the function returns the nested value when all keys in the path exist.

        Asserts:
            - The returned value matches the expected nested value.
        """
        # Arrange
        test_dict = {"a": {"b": {"c": "target_value"}}}

        # Act
        result = safeget(test_dict, "a", "b", "c")

        # Assert
        assert result == "target_value"

    # Handles multiple levels of nesting (3+ levels deep)
    def test_handles_deep_nesting(self):
        """
        Test that the function handles multiple levels of nesting (3+ levels deep).

        Asserts:
            - The returned value matches the expected deeply nested value.
        """
        # Arrange
        test_dict = {"level1": {"level2": {"level3": {"level4": "deep_value"}}}}

        # Act
        result = safeget(test_dict, "level1", "level2", "level3", "level4")

        # Assert
        assert result == "deep_value"

    # Works with different data types as values (strings, numbers, lists, dicts)
    def test_different_value_data_types(self):
        """
        Test that the function works with different data types as values (strings, numbers, lists, dicts).

        Asserts:
            - The returned value matches the expected value for each data type.
        """
        # Arrange
        test_dict = {
            "string_key": "string_value",
            "number_key": 42,
            "list_key": [1, 2, 3],
            "dict_key": {"nested": "value"},
        }

        # Act & Assert
        assert safeget(test_dict, "string_key") == "string_value"
        assert safeget(test_dict, "number_key") == 42
        assert safeget(test_dict, "list_key") == [1, 2, 3]
        assert safeget(test_dict, "dict_key") == {"nested": "value"}

    # Returns None when the first key doesn't exist
    def test_returns_none_when_first_key_missing(self):
        """
        Test that the function returns `None` when the first key doesn't exist.

        Asserts:
            - The returned value is `None`.
        """
        # Arrange
        test_dict = {"existing_key": "value"}

        # Act
        result = safeget(test_dict, "non_existent_key")

        # Assert
        assert result is None

    # Returns None when any intermediate key doesn't exist
    def test_returns_none_when_intermediate_key_missing(self):
        """
        Test that the function returns `None` when any intermediate key doesn't exist.

        Asserts:
            - The returned value is `None`.
        """
        # Arrange
        test_dict = {"level1": {"level2a": "value"}}

        # Act
        result = safeget(test_dict, "level1", "level2b", "level3")

        # Assert
        assert result is None

    # Returns None when the dictionary is empty
    def test_returns_none_with_empty_dictionary(self):
        """
        Test that the function returns `None` when the dictionary is empty.

        Asserts:
            - The returned value is `None`.
        """
        # Arrange
        test_dict = {}

        # Act
        result = safeget(test_dict, "any_key")

        # Assert
        assert result is None

    # Handles the case when no keys are provided
    def test_handles_no_keys_provided(self):
        """
        Test that the function handles the case when no keys are provided.

        Asserts:
            - The returned value is the original dictionary.
        """
        # Arrange
        test_dict = {"key": "value"}

        # Act
        result = safeget(test_dict)

        # Assert
        assert result == test_dict

    # Works with non-string keys (numbers, tuples)
    def test_works_with_non_string_keys(self):
        """
        Test that the function works with non-string keys (numbers, tuples).

        Asserts:
            - The returned value matches the expected value for each non-string key.
        """
        # Arrange
        test_dict = {
            42: "number_key_value",
            (1, 2): "tuple_key_value",
            "nested": {5: "nested_number_key"},
        }

        # Act & Assert
        assert safeget(test_dict, 42) == "number_key_value"
        assert safeget(test_dict, (1, 2)) == "tuple_key_value"
        assert safeget(test_dict, "nested", 5) == "nested_number_key"
