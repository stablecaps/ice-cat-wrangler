from rich import print
from rich.console import Console
from rich.table import Table


def get_rek_iscat_color(rek_iscat):
    """
    Determines the color for rek_iscat based on its value.

    Args:
        rek_iscat (str): The rekognition result indicating if the image contains a cat.

    Returns:
        str: The color corresponding to the rek_iscat value.
    """
    if rek_iscat == "N/A":
        return "red"
    elif rek_iscat.lower() == "true":
        return "green"
    elif rek_iscat.lower() == "false":
        return "red"
    else:
        return "yellow"


def rich_display_table(data, title="Table", columns=None):
    """
    Displays a formatted table using the Rich library.

    Args:
        data (list of dict): A list of dictionaries containing the data to display.
        title (str): The title of the table.
        columns (list of dict): A list of dictionaries defining the columns. Each dictionary should have:
            - "header" (str): The column header.
            - "key" (str): The key in the data dictionary corresponding to this column.
            - "style" (str, optional): The style for the column (default is None).
            - "justify" (str, optional): The justification for the column (default is "left").
            - "no_wrap" (bool, optional): Whether to disable wrapping for the column (default is False).

    Example:
        columns = [
            {"header": "rek_iscat", "key": "rek_iscat", "style": "green"},
            {"header": "batch_id", "key": "batch_id", "style": "magenta"},
            {"header": "img_fprint", "key": "img_fprint", "style": "yellow"},
        ]
        rich_display_table(data=iscat_results, title="Rekognition Results", columns=columns)
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
