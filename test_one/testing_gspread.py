import gspread

gc = gspread.oauth()

sh = gc.open('JEFF_YAY')

sh1 = gc.open_by_key('1Gpiv00YfOFccwAR_Gm28lgp5WjhdRRQqkIvmVYRKP1I')

## worksheet 

worksheet = sh.get_worksheet(0)

val = worksheet.acell('B1').value
print(val)


