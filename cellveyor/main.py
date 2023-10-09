"""🚚 Cellveyor is a conveyor for the cells in spreadsheets."""

from pathlib import Path

import typer
from rich.console import Console

from cellveyor import data, filesystem

# create a Typer object to support the command-line interface
cli = typer.Typer(no_args_is_help=True)

# create a default console
console = Console()


@cli.command()
def transport(
    spreadsheet_directory: Path = typer.Option(
        ...,
        "--spreadsheet-directory",
        "-d",
        help="A directory with spreadsheet file(s).",
    ),
    spreadsheet_file: Path = typer.Option(
        ...,
        "--spreadsheet-file",
        "-f",
        help="A spreadsheet file in the specified directory.",
    ),
) -> None:
    """Transport a specified spreadsheet."""
    # determine if the provided directory and file are valid
    if not filesystem.confirm_valid_file_in_directory(
        spreadsheet_file, spreadsheet_directory
    ):
        console.print(":person_shrugging: Unable to access file and/or directory!")
    # access all of the sheets inside of the valid spreadsheet file
    fully_qualified_spreadsheet_file = spreadsheet_directory / spreadsheet_file
    console.print(f":delivery_truck: Accessing: {fully_qualified_spreadsheet_file}")
    # access the dictionary of all of the dataframes in the speadsheet;
    # note that each sheet in the spreadsheet can be accessed by:
    # --> name of the sheet: str
    # --> dataframe of the sheet: pandas dataframe
    spreadsheet_dataframe_dict = data.access_dataframes(
        fully_qualified_spreadsheet_file
    )
    console.print(spreadsheet_dataframe_dict.keys())
