"""🚚 Cellveyor is a conveyor for the cells in spreadsheets."""

from pathlib import Path
from typing import Dict, List

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from googleapiclient.discovery import build


from cellveyor import data, filesystem, report, transfer, linkage
import pandas as pd
from google.oauth2 import service_account


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
        # a markdown-based formatter for the report's contents
        console.print(Panel(Markdown(current_report), title="Report", expand=False))
        console.print()

creds = None

@cli.command()
def transport(  # noqa: PLR0913
    spreadsheet_directory: Path = typer.Option(
        ...,
        "--spreadsheet-directory",
        "-d",
        help="Directory with spreadsheet file(s).",
    ),
    spreadsheet_file: Path = typer.Option(
        ...,
        "--spreadsheet-file",
        "-f",
        help="Spreadsheet file in the specified directory.",
    ),
    sheet_name: str = typer.Option(
        ...,
        "--sheet-name",
        "-s",
        help="Name of specific sheet in spreadsheet file",
    ),
    save_credentials: bool = typer.Option(
        False,
        "--save-credentials",
        "-sc",
        help="Save credentials.json file and service account file",
    ),
    service_account_file: str = typer.Option(
        ...,
        "--service-account-file",
        help="Path to the service account JSON file for linkage",
    ),
    spreadsheet_id: str = typer.Option(
        ...,
        "--spreadsheet-id",
        help="ID of the Google Spreadsheet for linkage",
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
        "-f",
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
    update_spreadsheet: bool = typer.Option(
        False,
        "--update-spreadsheet",
        help="Update the Google Sheet with the generated report",
    ),
) -> None:
    dataframes = None
    """Transport a specified spreadsheet."""
    # determine if the provided directory and file are valid
    if not filesystem.confirm_valid_file_in_directory(
        spreadsheet_file, spreadsheet_directory
    ):
        console.print(":person_shrugging: Unable to access file and/or directory")
    # access all of the sheets inside of the valid spreadsheet file
    fully_qualified_spreadsheet_file = spreadsheet_directory / spreadsheet_file
    console.print(f":delivery_truck: Accessing: {fully_qualified_spreadsheet_file}")
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
    sheet_dataframe_dict = data.access_dataframes(fully_qualified_spreadsheet_file)
    # console.print(sheet_dataframe_dict.keys())
    # access the requested sheet within the spreadsheet
    sheet_dataframe = sheet_dataframe_dict[sheet_name]
    # access the data for:
    # --> the key attribute
    # --> the column(s) that match the regular expression
    selected_columns, result_df = data.key_attribute_column_filter(
        sheet_dataframe, key_attribute, column_regexp, key_value
    )
    # create a unique message for each row in the dataframe
    per_key_report = report.create_per_key_report(
        key_attribute,
        result_df,
        selected_columns,
        feedback_regexp,
        combined_feedback_dict,
    )
    # Debug print
    print(f"Generated report for {sheet_name}:\n{per_key_report}")
    # display the generated reports
    display_reports(per_key_report)
    # if the --transfer flag was enabled then this means
    # that the generated reports should be uploaded to GitHub
    # as a comment inside of the standard pull request
    if save_credentials:
        linkage.save_credentials_file(creds)
        if transfer_report:
            transfer.transfer_reports_to_github(
                github_token, github_organization, github_repository_prefix, per_key_report
            )
 # Call fetch_data function directly from linkage.py
    if save_credentials:
        service_account_file_path = Path(service_account_file)
        if not service_account_file_path.exists():
            raise FileNotFoundError(f"Service account file not found: {service_account_file_path}")
         
         # Call fetch_data function from linkage.py
        dataframes = linkage.fetch_data(
            service_account_file=service_account_file_path.resolve(),
            spreadsheet_id=spreadsheet_id,
        )

    # Access the DataFrames as needed
    if dataframes is not None:
        for sheet_name, df in dataframes.items():
            print(f"Sheet Name: {sheet_name}")
            print(df)
            print("=" * 50)

            # Create a report for each sheet
            per_key_report = report.create_per_key_report(
                key_attribute,
                df,
                selected_columns,
                feedback_regexp,
                combined_feedback_dict,
            )

            # Debug print
            print(f"Generated report for {sheet_name}:\n{per_key_report}")

            # Display the generated reports
            display_reports(per_key_report)

            # If the --update-spreadsheet flag was enabled, update the Google Sheet
            if update_spreadsheet:
                # Convert the DataFrame to a dictionary to fit into the Google Sheets API
                per_key_report_dict = per_key_report.to_dict(orient="records")
    
   # If the --update-spreadsheet flag is provided, update the Google Sheet
    if update_spreadsheet and dataframes is not None:
        # Assuming per_key_report is a DataFrame
        # Convert the DataFrame to a dictionary to fit into the Google Sheets API
        per_key_report_dict = per_key_report.to_dict(orient="records")

        # Load credentials from the provided service account file
        creds = service_account.Credentials.from_service_account_file(
            service_account_file_path, scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )

        # Build the service for Google Sheets API
        service = build("sheets", "v4", credentials=creds)

        # Prepare the data to be written to the Google Sheet
        values = [list(per_key_report.columns)] + [list(row.values()) for row in per_key_report_dict]

        # Write data to the Google Sheet
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=sheet_name,
            body={"values": values},
            valueInputOption="RAW"
        ).execute()

        console.print("Report updated in Google Sheet!")


        # Call fetch_data function from linkage.py
        linkage.fetch_data(
            service_account_file=service_account_file_path.resolve(),
            spreadsheet_id=spreadsheet_id,
        )
    # if transfer_report:
    #     transfer.transfer_reports_to_github(
    #         github_token, github_organization, github_repository_prefix, per_key_report
    #         )
    #  # Call fetch_data function directly from linkage.py
    # if save_credentials:
    #     # Check if service account file exists for linkage
    #     service_account_file_path = Path(service_account_file)
    #     if not service_account_file_path.exists():
    #         raise FileNotFoundError(f"Service account file not found: {service_account_file_path}")

    #     # Call fetch_data function from linkage.py
    #     linkage.fetch_data(
    #         service_account_file=service_account_file_path.resolve(),
    #         spreadsheet_id=spreadsheet_id,
    #     )


