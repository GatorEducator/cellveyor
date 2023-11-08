import gspread 

gc = gspread.oauth()

sh = gc.open('Cellveyor-Sample-Gradebook-Shared')

#Selecting worksheet 
worksheet = sh.get_worksheet(0)

val = worksheet.acell('B1').value
print(val)