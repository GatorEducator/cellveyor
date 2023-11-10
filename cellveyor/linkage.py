import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Load your credentials from the JSON file
credentials = ServiceAccountCredentials.from_json_keyfile_name(['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive'])

# Authenticate with the Google Sheets API
gc = gspread.authorize(Cellveyor-Sample-Gradebook-Shared)

# Open the Google Sheets document by its title or URL
spreadsheet = gc.open('https://docs.google.com/spreadsheets/d/10mMsPZtKWREUIxqOzTQViSiqBsjeDHWqDMJtxOi-L34/edit#gid=0')

# Access a specific worksheet
worksheet = spreadsheet.get_worksheet(0)






# cell_value = worksheet.cell(1, 1).value
# print(f"Value at (1, 1): {cell_value}")


# worksheet.update('A2', 'New Value')


# cell_value = worksheet.cell(2, 1).value
# print(f"Value at (2, 1): {cell_value}")
