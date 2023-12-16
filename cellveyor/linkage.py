import pandas as pd
from googleapiclient.discovery import build
from google.oauth2 import service_account
import typer

cli = typer.Typer(no_args_is_help=True)

def fetch_data(service_account_file, spreadsheet_id):
    """Fetch data from Google Sheets API."""
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
            .get(spreadsheetId=spreadsheet_id, range=f"{sheet_name}!A1:S1")
            .execute()
        )

        values = result.get("values", [])

        # Convert the data to a Pandas DataFrame
        if values:
            df = pd.DataFrame(values[1:], columns=values[0])
            dataframes[sheet_name] = df

    # Access the DataFrames as needed
    for sheet_name, df in dataframes.items():
        typer.echo(f"Sheet Name: {sheet_name}")
        typer.echo(df)
        typer.echo("=" * 50)

if __name__ == "__main__":
    typer.run(fetch_data)
