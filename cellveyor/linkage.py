import pandas as pd
from googleapiclient.discovery import build
from google.oauth2 import service_account
import typer

cli = typer.Typer(no_args_is_help=True)

@cli.command()
def fetch_data(
    service_account_file: str = typer.Option(
        ...,
        "--service-account-file",
        "-s",
        help="Path to the service account JSON file",
    ),
    spreadsheet_id: str = typer.Option(
        ...,
        "--spreadsheet-id",
        "-i",
        help="ID of the Google Spreadsheet",
    ),
) -> None:
    """Fetch data from a specified Google Spreadsheet."""
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

    # Load credentials from the provided service account file
    creds = service_account.Credentials.from_service_account_file(
        service_account_file, scopes=SCOPES
    )

    service = build("sheets", "v4", credentials=creds)
    sheets = service.spreadsheets()

    # Getting list of all sheets in the spreadsheet
    spreadsheet_metadata = sheets.get(spreadsheetId=spreadsheet_id).execute()
    sheet_names = [sheet['properties']['title'] for sheet in spreadsheet_metadata['sheets']]

    # Create a dictionary to store DataFrames for each sheet
    dataframes = {}

    # Iterate through each sheet and fetch the data
    for sheet_name in sheet_names:
        result = (
            sheets.values()
            .get(spreadsheetId=spreadsheet_id, range=f"{sheet_name}!A1:S")
            .execute()
        )

        values = result.get("values", [])

        # Convert the data to a Pandas DataFrame
        if values:
            df = pd.DataFrame(values[1:], columns=values[0])
            dataframes[sheet_name] = df

    # Access the DataFrames as needed
    for sheet_name, df in dataframes.items():
        print(f"Sheet Name: {sheet_name}")
        print(df)
        print("=" * 50)

if __name__ == "__main__":
    typer.run(fetch_data)

