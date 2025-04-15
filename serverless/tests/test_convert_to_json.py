"""
Module: test_convert_to_json

This module contains unit tests for the `convert_to_json` function in the
`serverless.functions.fhelpers` module. The `convert_to_json` function is responsible
for converting Python data structures (e.g., dictionaries, lists) into JSON strings.

The tests in this module ensure that:
- Simple and nested data structures are correctly converted to JSON strings.
- Empty data structures and `None` values are handled appropriately.
- Circular references in data structures are managed gracefully (TODO: fix test).
- The resulting JSON strings are valid and match the expected format.

Dependencies:
- pytest: For test execution and assertions.
- json: For validating and comparing JSON strings.
- serverless.functions.fhelpers.convert_to_json: The function under test.
"""

import json

from serverless.functions.fhelpers import convert_to_json


class TestConvertToJson:
    """
    Test suite for the `convert_to_json` function.
    """

    # Convert a simple dictionary to JSON string
    def test_convert_simple_dict_to_json(self):
        """
        Test that a simple dictionary is correctly converted to a JSON string.

        Asserts:
            - The resulting JSON string matches the expected format.
            - The JSON string can be parsed back into the original dictionary.
        """
        # Arrange
        data = {"name": "John", "age": 30, "city": "New York"}

        # Act
        result = convert_to_json(data)

        # Assert
        expected = json.dumps(data, indent=4)
        assert result == expected
        assert json.loads(result) == data

    # Convert a list of values to JSON string
    def test_convert_list_to_json(self):
        """
        Test that a list of values is correctly converted to a JSON string.

        Asserts:
            - The resulting JSON string matches the expected format.
            - The JSON string can be parsed back into the original list.
        """
        # Arrange
        data = [1, "test", 3.14, True, None]

        # Act
        result = convert_to_json(data)

        # Assert
        expected = json.dumps(data, indent=4)
        assert result == expected
        assert json.loads(result) == data

    # Convert nested data structures (dicts within dicts) to JSON string
    def test_convert_nested_structures_to_json(self):
        """
        Test that nested data structures (e.g., dictionaries within dictionaries)
        are correctly converted to a JSON string.

        Asserts:
            - The resulting JSON string matches the expected format.
            - The JSON string can be parsed back into the original nested structure.
        """
        # Arrange
        data = {
            "person": {
                "name": "Alice",
                "address": {"street": "123 Main St", "city": "Boston", "zip": "02101"},
                "hobbies": ["reading", "hiking", {"name": "photography", "years": 5}],
            }
        }

        # Act
        result = convert_to_json(data)

        # Assert
        expected = json.dumps(data, indent=4)
        assert result == expected
        assert json.loads(result) == data

    # Handle empty data structures (empty dict, empty list)
    def test_convert_empty_structures_to_json(self):
        """
        Test that empty data structures (e.g., empty dictionaries and lists)
        are correctly converted to JSON strings.

        Asserts:
            - The resulting JSON string matches the expected format.
            - The JSON string can be parsed back into the original empty structure.
        """
        # Arrange
        empty_dict = {}
        empty_list = []

        # Act
        dict_result = convert_to_json(empty_dict)
        list_result = convert_to_json(empty_list)

        # Assert
        assert dict_result == json.dumps({}, indent=4)
        assert list_result == json.dumps([], indent=4)
        assert json.loads(dict_result) == empty_dict
        assert json.loads(list_result) == empty_list

    # Handle None value as input
    def test_convert_none_to_json(self):
        """
        Test that a `None` value is correctly converted to a JSON string.

        Asserts:
            - The resulting JSON string matches the expected format ("null").
        """
        # Arrange
        data = None

        # Act
        result = convert_to_json(data)

        # Assert
        expected = json.dumps(None, indent=4)
        assert result == expected
        assert result == "null"

    # TODO: fix the test test_handle_circular_references
    # Handle circular references in data structure
    # def test_handle_circular_references(self):
    #     """
    #     Test that circular references in data structures are handled gracefully.

    #     Asserts:
    #         - The function does not raise an exception when processing circular references.
    #         - The resulting JSON string includes a placeholder for circular references.
    #     """
    #     # Arrange
    #     data = {"name": "Circular"}
    #     data["self_reference"] = data  # Create circular reference

    #     # Act
    #     result = convert_to_json(data)

    #     # Assert
    #     assert result is not None  # Function should return a valid JSON string
    #     assert "<circular-reference: dict>" in result  # Placeholder for circular reference
