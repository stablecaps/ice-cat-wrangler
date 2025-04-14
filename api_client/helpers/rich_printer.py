"""
rich_printer.py

This module provides utility functions for displaying data in a formatted table using the `rich` library
and for determining colors based on specific conditions. These utilities are used to enhance console
output with visually appealing tables and color-coded information.

Functions:
    - get_rek_iscat_color: Determines the color for displaying Rekognition results.
    - rich_display_table: Displays data in a formatted table using the `rich` library.

Usage:
    Import the required function from this module to display tables or determine colors.

    Example:
        from helpers.rich_printer import get_rek_iscat_color, rich_display_table

        # Get a color for Rekognition results
        color = get_rek_iscat_color("true")
        print(color)

        # Display a table
        data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
        columns = [{"header": "Name", "key": "name"}, {"header": "Age", "key": "age"}]
        rich_display_table(data, title="Example Table", columns=columns)

Dependencies:
    - Python 3.12 or higher
    - `rich` library for enhanced console output
"""

from rich.console import Console
from rich.table import Table


def get_rek_iscat_color(rek_iscat):
    """
    Determines the color for displaying Rekognition results based on the `rek_iscat` value.

    Args:
        rek_iscat (str): The Rekognition result value. Expected values are "true", "false", or "N/A".

    Returns:
        str: The color name ("green", "red", or "yellow") based on the `rek_iscat` value.
    """
    if rek_iscat == "N/A":
        return "red"

    if rek_iscat.lower() == "true":
        return "green"

    if rek_iscat.lower() == "false":
        return "red"

    return "yellow"


def rich_display_table(data, title="Table", columns=None):
    """
    Displays data in a formatted table using the `rich` library.

    Args:
        data (list of dict): The data to display in the table. Each dictionary represents a row.
        title (str, optional): The title of the table. Defaults to "Table".
        columns (list of dict): A list of column definitions. Each column definition is a dictionary
            with the following keys:
            - "header" (str): The column header.
            - "key" (str): The key in the data dictionary to display in this column.
            - "style" (str, optional): The style (color) of the column. Defaults to None.
            - "justify" (str, optional): The justification of the column ("left", "center", "right").
              Defaults to "left".
            - "no_wrap" (bool, optional): Whether to disable text wrapping for the column. Defaults to False.

    Raises:
        ValueError: If the `columns` argument is not provided.

    Returns:
        None
    """
    if columns is None:
        raise ValueError("Columns must be defined to display the table.")

    table = Table(title=title)

    # Add columns to the table
    for column in columns:
        table.add_column(
            column["header"],
            justify=column.get("justify", "left"),
            style=column.get("style"),
            no_wrap=column.get("no_wrap", False),
        )

    # Add rows to the table
    for row in data:
        table.add_row(*[str(row.get(column["key"], "N/A")) for column in columns])

    console = Console()
    console.print(table)
