import pandas as pd
from googleapiclient.discovery import build
from google.oauth2 import service_account

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SERVICE_ACCOUNT_FILE = '/Users/stephenrodriguez/Documents/software_engineer/cellveyor/service.json'
SAMPLE_SPREADSHEET_ID = "10mMsPZtKWREUIxqOzTQViSiqBsjeDHWqDMJtxOi-L34"

creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)

service = build("sheets", "v4", credentials=creds)
sheets = service.spreadsheets()

# Get a list of all sheets in the spreadsheet
spreadsheet_metadata = sheets.get(spreadsheetId=SAMPLE_SPREADSHEET_ID).execute()
sheet_names = [sheet['properties']['title'] for sheet in spreadsheet_metadata['sheets']]

# Create a dictionary to store DataFrames for each sheet
dataframes = {}

# Iterate through each sheet and fetch the data
for sheet_name in sheet_names:
    result = (
        sheets.values()
        .get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=f"{sheet_name}!A1:S")
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
