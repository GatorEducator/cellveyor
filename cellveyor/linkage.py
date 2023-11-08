import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Load your credentials from the JSON file
credentials = ServiceAccountCredentials.from_json_keyfile_name('your-credentials.json', ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive'])

# Authenticate with the Google Sheets API
gc = gspread.authorize(credentials)

# Open the Google Sheets document by its title or URL
spreadsheet = gc.open('Your Spreadsheet Name')

# Access a specific worksheet
worksheet = spreadsheet.get_worksheet(0)

# Now you can work with the worksheet, for example, reading or writing data
cell_value = worksheet.cell(1, 1).value
print(f"Value at (1, 1): {cell_value}")

# To write data
worksheet.update('A2', 'New Value')

# To read data
cell_value = worksheet.cell(2, 1).value
print(f"Value at (2, 1): {cell_value}")
