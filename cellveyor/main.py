"""🚚 Cellveyor is a conveyor for the cells in spreadsheets."""

import os
from pathlib import Path
from typing import Dict, List

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from cellveyor import constants, data, filesystem, report, transfer

# load CELLVEYOR_GITHUB_TOKEN (and other env vars) from .env if present;
# env vars already set in the shell take precedence (override=False)
load_dotenv()

# create a Typer object to support the command-line interface
cli = typer.Typer(no_args_is_help=True)

# create a default console
console = Console()


def _print_dash_list(title: str, items: List[str], color: str = "red") -> None:
    """Print a title followed by a dash-prefixed list with spacing."""
    console.print(f"  {title}:", style=color)
    console.print()
    for item in items:
        # sanitize items: replace newlines and collapse whitespace to avoid broken dash lists
        clean_item = str(item).replace("\n", " ").replace("\r", " ")
        # collapse multiple spaces
        clean_item = " ".join(clean_item.split())
        # use style instead of markup to avoid interpreting brackets in item names
        console.print(f"    - {clean_item}", style=color)
    console.print()


def display_reports(reports_dict: Dict[str, str], fancy: bool = True) -> None:
    """Display all of the reports in the reports dictionary."""
    # iterate through all of the keys
    for current_report_key, current_report in reports_dict.items():
        # when fancy is false, print plain markdown for copying;
        # when fancy is true, wrap in rich panel with title
        if not fancy:
            console.print(f"{current_report_key}:")
            console.print()
            console.print(Markdown(current_report))
            console.print()
            continue
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
def transport(  # noqa: PLR0912, PLR0913, PLR0915, PLR0917
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
        help="Regular expression for matching feedback columns in the sheet",
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
        help="Feedback file(s) in YAML format",
    ),
    github_token_env: str | None = typer.Option(
        None,
        "--github-token-env",
        "-g",
        help="Name of env var for GitHub token (CELLVEYOR_GITHUB_TOKEN or GITHUB_TOKEN)",
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
        "--transfer-report/--no-transfer-report",
        "-t",
        help="Transfer a report to GitHub",
    ),
    fancy: bool = typer.Option(
        True,
        "--fancy/--no-fancy",
        "-y",
        help="Display reports with rich Panel (default: fancy); use --no-fancy for plain markdown for copying",
    ),
) -> None:
    """Generate per-student grade reports from spreadsheet cells and optionally transfer them to GitHub."""
    # handle direct calls where typer defaults are OptionInfo
    if type(transfer_report).__name__ == "OptionInfo":  # type: ignore[unreachable]
        transfer_report = False  # type: ignore[assignment]
    if type(fancy).__name__ == "OptionInfo":  # type: ignore[unreachable]
        fancy = True  # type: ignore[assignment]
    # resolve GitHub token from env var name (default CELLVEYOR_GITHUB_TOKEN, fallback GITHUB_TOKEN)
    # handle direct calls where typer default is OptionInfo (type checker sees str, so use name check)
    if (
        github_token_env is None
        or type(github_token_env).__name__ == "OptionInfo"
    ):  # type: ignore[unreachable]
        github_token_env = "CELLVEYOR_GITHUB_TOKEN"
    # load_dotenv() already populated os.environ from .env
    github_token: str | None = os.getenv(github_token_env)
    # fallback to GITHUB_TOKEN when using the default var name
    if not github_token and github_token_env == "CELLVEYOR_GITHUB_TOKEN":
        fallback = os.getenv("GITHUB_TOKEN")
        if fallback:
            github_token = fallback
    # determine if the provided directory and file are valid
    if not filesystem.confirm_valid_file_in_directory(
        spreadsheet_file, spreadsheet_directory
    ):
        console.print()
        console.print(
            ":person_shrugging: Unable to access file and/or directory",
            style="red",
        )
        console.print()
        # provide more specific diagnostics
        if not filesystem.confirm_valid_directory(spreadsheet_directory):
            console.print("  Directory not found:", style="red")
            console.print()
            console.print(f"    - {spreadsheet_directory}", style="red")
            console.print()
        else:
            console.print("  File not found in directory:", style="red")
            console.print()
            console.print(
                f"    - {spreadsheet_directory / spreadsheet_file}",
                style="red",
            )
            console.print()
        raise typer.Exit(code=1)
    # access all of the sheets inside of the valid spreadsheet file
    fully_qualified_spreadsheet_file = spreadsheet_directory / spreadsheet_file
    console.print(
        f":delivery_truck: Accessing: {fully_qualified_spreadsheet_file}"
    )
    console.print()
    # warn about any feedback files that do not exist
    if feedback_file is not None:
        missing_feedback = [
            fb for fb in feedback_file if not filesystem.confirm_valid_file(fb)
        ]
        if missing_feedback:
            console.print(
                ":warning: Feedback file(s) not found, skipping:",
                style="yellow",
            )
            console.print()
            for fb_path in missing_feedback:
                console.print(f"    - {fb_path}", style="yellow")
            console.print()
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
            f":person_shrugging: Spreadsheet file not found: {fully_qualified_spreadsheet_file}",
            style="red",
        )
        console.print()
        raise typer.Exit(code=1)
    except Exception as exc:
        console.print(
            f":person_shrugging: Failed to read spreadsheet: {exc}",
            style="red",
        )
        console.print()
        raise typer.Exit(code=1)
    # validate that the requested sheet exists
    if sheet_name not in sheet_dataframe_dict:
        console.print(
            f":person_shrugging: Sheet '{sheet_name}' not found", style="red"
        )
        console.print()
        _print_dash_list(
            "Available sheets",
            list(sheet_dataframe_dict.keys()),
            color="red",
        )
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
        console.print(f":person_shrugging: {exc}", style="red")
        console.print()
        # also show available columns for key attribute errors
        if "Key attribute" in str(exc):
            _print_dash_list(
                "Available columns",
                list(map(str, sheet_dataframe.columns.tolist())),
                color="red",
            )
            console.print(
                "  Hint: check --key-attribute and --column-regexp",
                style="red",
            )
            console.print()
        raise typer.Exit(code=1)
    except Exception as exc:
        console.print(
            f":person_shrugging: Failed to filter columns: {exc}",
            style="red",
        )
        console.print()
        raise typer.Exit(code=1)
    # warn if column regexp matched no columns
    if selected_columns.empty or len(selected_columns.columns) == 0:
        console.print(
            f":warning: No columns matched --column-regexp '{column_regexp}'",
            style="yellow",
        )
        console.print()
        _print_dash_list(
            "Available columns",
            list(map(str, sheet_dataframe.columns.tolist())),
            color="yellow",
        )
    # warn if result has no rows
    if result_df.empty:
        console.print(
            ":warning: No rows found after filtering — check --key-attribute and --column-regexp",
            style="yellow",
        )
        console.print()
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
            f":person_shrugging: Failed to create reports: {exc}", style="red"
        )
        console.print()
        raise typer.Exit(code=1)
    if not per_key_report:
        console.print(
            ":warning: No reports generated (no matching rows)", style="yellow"
        )
        console.print()
    # display the generated reports
    display_reports(per_key_report, fancy)
    # if the --transfer flag was enabled then this means
    # that the generated reports should be uploaded to GitHub
    # as a comment inside of the standard pull request
    if transfer_report:
        # validate required GitHub arguments before attempting transfer
        missing_github_args = []
        if not github_token:
            missing_github_args.append(
                "--github-token-env (or set CELLVEYOR_GITHUB_TOKEN / GITHUB_TOKEN in env/.env)"
            )
        if not github_organization:
            missing_github_args.append("--github-organization")
        if not github_repository_prefix:
            missing_github_args.append("--github-repository-prefix")
        if missing_github_args:
            console.print(
                ":person_shrugging: Missing required GitHub arguments for --transfer-report:",
                style="red",
            )
            console.print()
            _print_dash_list(
                "Missing options", missing_github_args, color="red"
            )
            console.print(
                "  Hint: set CELLVEYOR_GITHUB_TOKEN in env/.env or use --github-token-env <VAR_NAME>",
                style="red",
            )
            console.print()
            raise typer.Exit(code=1)
        assert github_token is not None
        try:
            transfer.transfer_reports_to_github(
                github_token,
                github_organization,
                github_repository_prefix,
                per_key_report,
            )
        except Exception as exc:
            console.print(
                f":person_shrugging: GitHub transfer failed: {exc}",
                style="red",
            )
            console.print()
            raise typer.Exit(code=1)
