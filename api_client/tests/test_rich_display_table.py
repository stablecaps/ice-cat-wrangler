"""
Module: test_rich_display_table

This module contains unit tests for the `rich_display_table` function in the
`api_client.helpers.rich_printer` module. The `rich_display_table` function is responsible
for displaying data in a formatted table using the `rich` library.

The tests in this module ensure that:
- The function correctly displays tables with valid data and column definitions.
- The function supports custom table titles, column styles, and justifications.
- The function handles edge cases such as empty data lists, missing keys, and non-string values.
- The function raises appropriate exceptions for invalid input, such as missing column definitions.

Dependencies:
- pytest: For test execution and assertions.
- unittest.mock: For mocking dependencies and verifying function behavior.
- api_client.helpers.rich_printer.rich_display_table: The function under test.

Test Cases:
- `test_display_table_with_valid_data`: Verifies that the function displays a table with valid data and column definitions.
- `test_display_table_with_custom_title`: Ensures the function supports custom table titles.
- `test_display_table_with_custom_column_styles`: Verifies that the function applies custom styles to columns.
- `test_display_table_with_different_justifications`: Ensures the function supports different column justifications.
- `test_display_table_with_no_wrap_option`: Verifies that the function handles the `no_wrap` option for specific columns.
- `test_raise_value_error_when_columns_is_none`: Ensures the function raises a `ValueError` when the `columns` parameter is `None`.
- `test_handle_empty_data_list`: Verifies that the function handles empty data lists correctly.
- `test_process_data_with_missing_keys`: Ensures the function handles missing keys in the data by displaying "N/A".
- `test_handle_non_string_values`: Verifies that the function converts non-string values to strings before displaying them.
"""

from unittest.mock import MagicMock, patch

import pytest

from api_client.helpers.rich_printer import rich_display_table


class TestRichDisplayTable:
    """
    Test suite for the `rich_display_table` function.
    """

    # Display a table with valid data and column definitions
    def test_display_table_with_valid_data(self):
        """
        Test that the function displays a table with valid data and column definitions.

        Asserts:
            - The function does not raise any exceptions when displaying valid data.
        """

        data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
        columns = [{"header": "Name", "key": "name"}, {"header": "Age", "key": "age"}]

        # Since the function prints to console, we're testing it doesn't raise exceptions
        rich_display_table(data, title="Test Table", columns=columns)
        # If we reach here without exception, the test passes

    # Display a table with a custom title
    def test_display_table_with_custom_title(self):
        """
        Test that the function supports custom table titles.

        Asserts:
            - The `Table` object is created with the specified custom title.
        """

        data = [{"name": "Alice", "age": 30}]
        columns = [{"header": "Name", "key": "name"}, {"header": "Age", "key": "age"}]
        custom_title = "Custom Table Title"

        with patch("api_client.helpers.rich_printer.Table") as mock_table:
            mock_table_instance = MagicMock()
            mock_table.return_value = mock_table_instance

            rich_display_table(data, title=custom_title, columns=columns)

            # Verify Table was created with the custom title
            mock_table.assert_called_once_with(title=custom_title)

    # Display a table with custom column styles
    def test_display_table_with_custom_column_styles(self):
        """
        Test that the function applies custom styles to columns.

        Asserts:
            - The `add_column` method is called with the correct styles for each column.
        """

        data = [{"name": "Alice", "age": 30}]
        columns = [
            {"header": "Name", "key": "name", "style": "bold red"},
            {"header": "Age", "key": "age", "style": "blue"},
        ]

        with patch("api_client.helpers.rich_printer.Table") as mock_table:
            mock_table_instance = MagicMock()
            mock_table.return_value = mock_table_instance

            rich_display_table(data, columns=columns)

            # Verify add_column was called with the correct styles
            mock_table_instance.add_column.assert_any_call(
                "Name", justify="left", style="bold red", no_wrap=False
            )
            mock_table_instance.add_column.assert_any_call(
                "Age", justify="left", style="blue", no_wrap=False
            )

    # Display a table with different column justifications
    def test_display_table_with_different_justifications(self):
        """
        Test that the function supports different column justifications.

        Asserts:
            - The `add_column` method is called with the correct justification for each column.
        """

        data = [{"name": "Alice", "age": 30}]
        columns = [
            {"header": "Name", "key": "name", "justify": "left"},
            {"header": "Age", "key": "age", "justify": "right"},
            {"header": "Status", "key": "status", "justify": "center"},
        ]

        with patch("api_client.helpers.rich_printer.Table") as mock_table:
            mock_table_instance = MagicMock()
            mock_table.return_value = mock_table_instance

            rich_display_table(data, columns=columns)

            # Verify add_column was called with the correct justifications
            mock_table_instance.add_column.assert_any_call(
                "Name", justify="left", style=None, no_wrap=False
            )
            mock_table_instance.add_column.assert_any_call(
                "Age", justify="right", style=None, no_wrap=False
            )
            mock_table_instance.add_column.assert_any_call(
                "Status", justify="center", style=None, no_wrap=False
            )

    # Display a table with no_wrap option for specific columns
    def test_display_table_with_no_wrap_option(self):
        """
        Test that the function handles the `no_wrap` option for specific columns.

        Asserts:
            - The `add_column` method is called with the correct `no_wrap` setting for each column.
        """

        data = [{"name": "Alice with a very long name", "age": 30}]
        columns = [
            {"header": "Name", "key": "name", "no_wrap": True},
            {"header": "Age", "key": "age", "no_wrap": False},
        ]

        with patch("api_client.helpers.rich_printer.Table") as mock_table:
            mock_table_instance = MagicMock()
            mock_table.return_value = mock_table_instance

            rich_display_table(data, columns=columns)

            # Verify add_column was called with the correct no_wrap settings
            mock_table_instance.add_column.assert_any_call(
                "Name", justify="left", style=None, no_wrap=True
            )
            mock_table_instance.add_column.assert_any_call(
                "Age", justify="left", style=None, no_wrap=False
            )

    # Raise ValueError when columns parameter is None
    def test_raise_value_error_when_columns_is_none(self):
        """
        Test that the function raises a `ValueError` when the `columns` parameter is `None`.

        Asserts:
            - A `ValueError` is raised with the correct error message.
        """
        data = [{"name": "Alice", "age": 30}]

        with pytest.raises(ValueError) as excinfo:
            rich_display_table(data, columns=None)

        assert "Columns must be defined to display the table." in str(excinfo.value)

    # Handle empty data list (no rows)
    def test_handle_empty_data_list(self):
        """
        Test that the function handles empty data lists correctly.

        Asserts:
            - Columns are added to the table, but no rows are added.
        """

        data = []
        columns = [{"header": "Name", "key": "name"}, {"header": "Age", "key": "age"}]

        with patch("api_client.helpers.rich_printer.Table") as mock_table:
            mock_table_instance = MagicMock()
            mock_table.return_value = mock_table_instance

            rich_display_table(data, columns=columns)

            # Verify columns were added but no rows
            assert mock_table_instance.add_column.call_count == 2
            assert mock_table_instance.add_row.call_count == 0

    # Handle empty columns list
    # TODO: fix this test
    # def test_handle_empty_columns_list(self):
    #
    #
    #     from unittest.mock import patch, MagicMock

    #     data = [{"name": "Alice", "age": 30}]
    #     columns = []

    #     with patch('api_client.helpers.rich_printer.Table') as mock_table:
    #         mock_table_instance = MagicMock()
    #         mock_table.return_value = mock_table_instance

    #         rich_display_table(data, columns=columns)

    #         # Verify no columns were added
    #         assert mock_table_instance.add_column.call_count == 0
    #         # Verify no rows were added (since there are no columns)
    #         assert mock_table_instance.add_row.call_count == 0

    # Process data with missing keys specified in columns
    def test_process_data_with_missing_keys(self):
        """
        Test that the function handles missing keys in the data by displaying "N/A".

        Asserts:
            - Rows are added with "N/A" for missing keys.
        """

        data = [
            {"name": "Alice"},  # Missing 'age' key
            {"age": 25},  # Missing 'name' key
        ]
        columns = [{"header": "Name", "key": "name"}, {"header": "Age", "key": "age"}]

        with patch("api_client.helpers.rich_printer.Table") as mock_table:
            mock_table_instance = MagicMock()
            mock_table.return_value = mock_table_instance

            rich_display_table(data, columns=columns)

            # Verify rows were added with 'N/A' for missing values
            mock_table_instance.add_row.assert_any_call("Alice", "N/A")
            mock_table_instance.add_row.assert_any_call("N/A", "25")

    # Handle non-string values in data by converting to string
    def test_handle_non_string_values(self):
        """
        Test that the function converts non-string values to strings before displaying them.

        Asserts:
            - All values in the table rows are converted to strings.
        """

        data = [
            {
                "name": "Alice",
                "age": 30,
                "active": True,
                "score": 95.5,
                "items": [1, 2, 3],
            }
        ]
        columns = [
            {"header": "Name", "key": "name"},
            {"header": "Age", "key": "age"},
            {"header": "Active", "key": "active"},
            {"header": "Score", "key": "score"},
            {"header": "Items", "key": "items"},
        ]

        with patch("api_client.helpers.rich_printer.Table") as mock_table:
            mock_table_instance = MagicMock()
            mock_table.return_value = mock_table_instance

            rich_display_table(data, columns=columns)

            # Verify all values were converted to strings
            mock_table_instance.add_row.assert_called_once_with(
                "Alice", "30", "True", "95.5", "[1, 2, 3]"
            )
