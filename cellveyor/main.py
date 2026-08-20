"""🚚 Cellveyor is a conveyor for the cells in spreadsheets."""

from pathlib import Path
from typing import Dict, List

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from cellveyor import constants, data, filesystem, report, transfer

# create a Typer object to support the command-line interface
cli = typer.Typer(no_args_is_help=True)

# create a default console
console = Console()


def display_reports(reports_dict: Dict[str, str]) -> None:
    """Display all of the reports in the reports dictionary."""
    # iterate through all of the keys
    for current_report_key in reports_dict.keys():
        # extract the report for the current key
        current_report = reports_dict[current_report_key]
        # display the report inside of a rich panel, using
        # a markdown-based formatter for the report's contents;
        # note that use of console.print must occur in two
        # stages when displaying markdown-based content in a Panel
        markdown_current_report = Markdown(current_report)
        console.print(f"{constants.markers.Indent}")
        console.print(
            Panel(
                markdown_current_report, title=current_report_key, expand=False
            )
        )


@cli.command()
def transport(  # noqa: PLR0912, PLR0913, PLR0915
    spreadsheet_directory: Path = typer.Option(
        ...,
        "--spreadsheet-directory",
        "-d",
        help="Directory with spreadsheet file(s).",
    ),
    spreadsheet_file: Path = typer.Option(
        ...,
        "--spreadsheet-file",
        "-s",
        help="Spreadsheet file in the specified directory.",
    ),
    sheet_name: str = typer.Option(
        ...,
        "--sheet-name",
        "-n",
        help="Name of specific sheet in spreadsheet file",
    ),
    key_attribute: str = typer.Option(
        ...,
        "--key-attribute",
        "-a",
        help="Name of key attribute in specific sheet of spreadsheet file",
    ),
    column_regexp: str = typer.Option(
        ...,
        "--column-regexp",
        "-c",
        help="Regular expression for matching columns in specific sheet",
    ),
    feedback_regexp: str = typer.Option(
        ...,
        "--feedback-regexp",
        "-r",
        help="Regular expression for matching feedback columns in specific sheet",
    ),
    key_value: str = typer.Option(
        None,
        "--key-value",
        "-v",
        help="Value of key attribute in specific sheet of spreadsheet file",
    ),
    feedback_file: List[Path] = typer.Option(
        None,
        "--feedback-file",
        "-f",
        help="Feedback file(s) in JSON format",
    ),
    github_token: str = typer.Option(
        None,
        "--github-token",
        "-g",
        help="GitHub authorization token",
    ),
    github_organization: str = typer.Option(
        None,
        "--github-organization",
        "-o",
        help="GitHub organization that stores all matching repositories ",
    ),
    github_repository_prefix: str = typer.Option(
        None,
        "--github-repository-prefix",
        "-p",
        help="Prefix for all GitHub repositories used as a destination",
    ),
    transfer_report: bool = typer.Option(
        False,
        help="Transfer a report to GitHub",
    ),
) -> None:
    """Transport a specified spreadsheet."""
    # determine if the provided directory and file are valid
    if not filesystem.confirm_valid_file_in_directory(
        spreadsheet_file, spreadsheet_directory
    ):
        console.print(
            "[red]:person_shrugging: Unable to access file and/or directory[/red]"
        )
        # provide more specific diagnostics
        if not filesystem.confirm_valid_directory(spreadsheet_directory):
            console.print(
                f"[red]  Directory not found: {spreadsheet_directory}[/red]"
            )
        else:
            console.print(
                f"[red]  File not found in directory: {spreadsheet_directory / spreadsheet_file}[/red]"
            )
        raise typer.Exit(code=1)
    # access all of the sheets inside of the valid spreadsheet file
    fully_qualified_spreadsheet_file = spreadsheet_directory / spreadsheet_file
    console.print(
        f":delivery_truck: Accessing: {fully_qualified_spreadsheet_file}"
    )
    # warn about any feedback files that do not exist
    if feedback_file is not None:
        for fb_path in feedback_file:
            if not filesystem.confirm_valid_file(fb_path):
                console.print(
                    f"[yellow]:warning: Feedback file not found, skipping: {fb_path}[/yellow]"
                )
    # access all of the feedback files and combine them into a single
    # dictionary organized in the following fashion:
    # --> key: label like "header" or "footer" or a label
    #          that is found inside of a Google Sheet like "reassess"
    # --> value: the actual content that will be placed in the location of the final
    #            message in, for instance, the header or the footer or, alternatively,
    #            in the list of extra feedback
    combined_feedback_dict = filesystem.read_feedback_files(feedback_file)
    # access the dictionary of all of the dataframes in the speadsheet;
    # note that each sheet in the spreadsheet can be accessed by:
    # --> name of the sheet: str
    # --> dataframe of the sheet: pandas dataframe
    try:
        sheet_dataframe_dict = data.access_dataframes(
            fully_qualified_spreadsheet_file
        )
    except FileNotFoundError:
        console.print(
            f"[red]:person_shrugging: Spreadsheet file not found: {fully_qualified_spreadsheet_file}[/red]"
        )
        raise typer.Exit(code=1)
    except Exception as exc:
        console.print(
            f"[red]:person_shrugging: Failed to read spreadsheet: {exc}[/red]"
        )
        raise typer.Exit(code=1)
    # validate that the requested sheet exists
    if sheet_name not in sheet_dataframe_dict:
        available_sheets = ", ".join(sheet_dataframe_dict.keys())
        console.print(
            f"[red]:person_shrugging: Sheet '{sheet_name}' not found[/red]"
        )
        console.print(f"[red]  Available sheets: {available_sheets}[/red]")
        raise typer.Exit(code=1)
    # console.print(sheet_dataframe_dict.keys())
    # access the requested sheet within the spreadsheet
    sheet_dataframe = sheet_dataframe_dict[sheet_name]
    # access the data for:
    # --> the key attribute
    # --> the column(s) that match the regular expression
    try:
        selected_columns, result_df = data.key_attribute_column_filter(
            sheet_dataframe, key_attribute, column_regexp, key_value
        )
    except ValueError as exc:
        console.print(f"[red]:person_shrugging: {exc}[/red]")
        # also show available columns for key attribute errors
        if "Key attribute" in str(exc):
            available_cols = ", ".join(
                map(str, sheet_dataframe.columns.tolist())
            )
            console.print(
                "[red]  Hint: check --key-attribute and --column-regexp[/red]"
            )
        raise typer.Exit(code=1)
    except Exception as exc:
        console.print(
            f"[red]:person_shrugging: Failed to filter columns: {exc}[/red]"
        )
        raise typer.Exit(code=1)
    # warn if column regexp matched no columns
    if selected_columns.empty or len(selected_columns.columns) == 0:
        console.print(
            f"[yellow]:warning: No columns matched --column-regexp '{column_regexp}'[/yellow]"
        )
        available_cols = ", ".join(map(str, sheet_dataframe.columns.tolist()))
        console.print(
            f"[yellow]  Available columns: {available_cols}[/yellow]"
        )
    # warn if result has no rows
    if result_df.empty:
        console.print(
            "[yellow]:warning: No rows found after filtering — check --key-attribute and --column-regexp[/yellow]"
        )
    # create a unique message for each row in the dataframe
    try:
        per_key_report = report.create_per_key_report(
            key_attribute,
            result_df,
            selected_columns,
            feedback_regexp,
            combined_feedback_dict,
        )
    except Exception as exc:
        console.print(
            f"[red]:person_shrugging: Failed to create reports: {exc}[/red]"
        )
        raise typer.Exit(code=1)
    if not per_key_report:
        console.print(
            "[yellow]:warning: No reports generated (no matching rows)[/yellow]"
        )
    # display the generated reports
    display_reports(per_key_report)
    # if the --transfer flag was enabled then this means
    # that the generated reports should be uploaded to GitHub
    # as a comment inside of the standard pull request
    if transfer_report:
        # validate required GitHub arguments before attempting transfer
        missing_github_args = []
        if not github_token:
            missing_github_args.append("--github-token")
        if not github_organization:
            missing_github_args.append("--github-organization")
        if not github_repository_prefix:
            missing_github_args.append("--github-repository-prefix")
        if missing_github_args:
            console.print(
                f"[red]:person_shrugging: Missing required GitHub arguments for --transfer-report: {', '.join(missing_github_args)}[/red]"
            )
            console.print(
                "[red]  Hint: provide all GitHub options or omit --transfer-report[/red]"
            )
            raise typer.Exit(code=1)
        try:
            transfer.transfer_reports_to_github(
                github_token,
                github_organization,
                github_repository_prefix,
                per_key_report,
            )
        except Exception as exc:
            console.print(
                f"[red]:person_shrugging: GitHub transfer failed: {exc}[/red]"
            )
            raise typer.Exit(code=1)
