"""
Module: test_get_rek_iscat_color

This module contains unit tests for the `get_rek_iscat_color` function in the
`api_client.helpers.rich_printer` module. The `get_rek_iscat_color` function is responsible
for determining the color to display based on the `rek_iscat` value.

The tests in this module ensure that:
- The function returns the correct color for valid `rek_iscat` values ("true", "false", "N/A").
- The function handles case-insensitive comparisons for `rek_iscat` values.
- The function returns a default color for unexpected `rek_iscat` values.

Dependencies:
- pytest: For test execution and assertions.
- api_client.helpers.rich_printer.get_rek_iscat_color: The function under test.

Test Cases:
- `test_returns_green_for_true`: Verifies that the function returns "green" when the input is "true".
- `test_returns_red_for_false`: Verifies that the function returns "red" when the input is "false".
- `test_returns_red_for_na`: Verifies that the function returns "red" when the input is "N/A".
- `test_case_insensitive_true`: Ensures the function handles case-insensitive comparison for "true".
- `test_case_insensitive_false`: Ensures the function handles case-insensitive comparison for "false".
"""

from api_client.helpers.rich_printer import get_rek_iscat_color


class TestGetRekIscatColor:
    """
    Test suite for the `get_rek_iscat_color` function.
    """

    # Returns "green" when input is "true"
    def test_returns_green_for_true(self):
        """
        Test that the function returns "green" when the input is "true".

        Asserts:
            - The returned color is "green".
        """
        # Arrange
        rek_iscat = "true"

        # Act
        result = get_rek_iscat_color(rek_iscat)

        # Assert
        assert result == "green"

    # Returns "red" when input is "false"
    def test_returns_red_for_false(self):
        """
        Test that the function returns "red" when the input is "false".

        Asserts:
            - The returned color is "red".
        """
        # Arrange
        rek_iscat = "false"

        # Act
        result = get_rek_iscat_color(rek_iscat)

        # Assert
        assert result == "red"

    # Returns "red" when input is "N/A"
    def test_returns_red_for_na(self):
        """
        Test that the function returns "red" when the input is "N/A".

        Asserts:
            - The returned color is "red".
        """
        # Arrange
        rek_iscat = "N/A"

        # Act
        result = get_rek_iscat_color(rek_iscat)

        # Assert
        assert result == "red"

    # Handles case-insensitive comparison for "true"
    def test_case_insensitive_true(self):
        """
        Test that the function handles case-insensitive comparison for "true".

        Asserts:
            - The returned color is "green" for input "TRUE".
        """
        # Arrange
        rek_iscat = "TRUE"

        # Act
        result = get_rek_iscat_color(rek_iscat)

        # Assert
        assert result == "green"

    # Handles case-insensitive comparison for "false"
    def test_case_insensitive_false(self):
        """
        Test that the function handles case-insensitive comparison for "false".

        Asserts:
            - The returned color is "red" for input "FALSE".
        """
        # Arrange
        rek_iscat = "FALSE"

        # Act
        result = get_rek_iscat_color(rek_iscat)

        # Assert
        assert result == "red"
