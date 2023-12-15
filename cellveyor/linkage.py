import pandas as pd
from googleapiclient.discovery import build
from google.oauth2 import service_account
from typing import Dict

def fetch_data(
    service_account_file: str,
    spreadsheet_id: str,
) -> Dict[str, pd.DataFrame]:
    # ...

    # Getting list of all sheets in the spreadsheet
    spreadsheet_metadata = sheets.get(spreadsheetId=spreadsheet_id).execute()
    sheet_names = [sheet['properties']['title'] for sheet in spreadsheet_metadata['sheets']]

    # Create a dictionary to store DataFrames for each sheet
    dataframes = {}

    # Iterate through each sheet and fetch the data
    for sheet_name in sheet_names:
        range_ = f"{sheet_name}!A1:S1"  # Adjust the range as needed

        result = (
            sheets.values()
            .get(spreadsheetId=spreadsheet_id, range=range_)
            .execute()
        )

        values = result.get("values", [])

        # Convert the data to a Pandas DataFrame
        if values:
            df = pd.DataFrame(values[1:], columns=values[0])
            dataframes[sheet_name] = df

    return dataframes

# Additional function to generate a report
def generate_report(dataframe: pd.DataFrame) -> str:
    if dataframe.empty:
        return "No data available."

    report = f"Hello @{dataframe['GitHub Username'].iloc[0]}!\n\n"
    report += "**📔 Here are your summary scores:**\n\n"

    # Iterate through columns to include in the report
    for column in dataframe.columns:
        if column != "GitHub Username":
            report += f"- **{column}**: {dataframe[column].iloc[0]}\n"

    report += "\n**🤝 Here is some additional feedback for you to consider:**\n\n"
    report += "\n".join(dataframe["Feedback"].tolist())

    return report
