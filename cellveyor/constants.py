"""Define constants with dataclasses for use in Cellveyor"""

from dataclasses import dataclass


# cellveyor constant
@dataclass(frozen=True)
class Cellveyor:
    """Define the Cellveyor dataclass for constant(s)."""

    Application_Name: str
    Application_Author: str
    Cellveyor_Database_View: str
    Https: str
    Name: str
    Programming_Language: str
    Separator: str
    Server_Shutdown: str
    Tagline: str
    Theme_Background: str
    Theme_Colors: str
    Website: str


cellveyor = Cellveyor(
    Application_Name="cellveyor",
    Application_Author="CellveyorTeam",
    Cellveyor_Database_View="cellveyor_complete",
    Https="https://",
    Name="cellveyor",
    Programming_Language="python",
    Separator="/",
    Server_Shutdown=":person_shrugging: Shut down cellveyor's server",
    Tagline="Cellveyor: The conveyor for spreadsheet cells",
    Theme_Background="default",
    Theme_Colors="ansi_dark",
    Website=":link: GitHub: https://github.com/GatorEducator/cellveyor",
)

# checks constant
@dataclass(frozen=True)
class Checks:
    """Define the Checks dataclass for constant(s)."""

    Check_Cellveyor: str
    Check_Code: str
    Check_Count: str
    Check_Confidence: int
    Check_Spreadsheet: str
    Check_Id: str
    Checks_Label: str
    Check_Name: str
    Check_Cell: str


checks = Checks(
    Check_Cellveyor="cellveyor",
    Check_Code="code",
    Check_Count="count",
    Check_Confidence=80,
    Check_Spreadsheet="spreadsheet",
    Check_Id="id",
    Checks_Label="checks",
    Check_Name="name",
    Check_Cell="cell",
)

# filesystem constant
@dataclass(frozen=True)
class Filesystem:
    """Define the Filesystem dataclass for constant(s)."""

    Current_Directory: str
    Dash: str
    Dot: str
    Main_Configuration_File: str
    Main_Checks_File: str
    Current_Report_Name: str
    Cell_Name: str
    Results_Extension: str


filesystem = Filesystem(
    Current_Directory=".",
    Dash="-",
    Dot=".",
    Main_Configuration_File="config.yml",
    Main_Checks_File="checks.yml",
    Current_Report_Name="cellveyor-report",
    Cell_Name="cell-report",
    Results_Extension="",
)

# humanreadable constant
@dataclass(frozen=True)
class Humanreadable:
    """Define the Humanreadable dataclass for constant(s)."""

    Yes: str
    No: str


humanreadable = Humanreadable(Yes="Yes", No="No")


# markers constant
@dataclass(frozen=True)
class Markers:
    """Define the Markers dataclass for constant(s)."""

    Comma_Space: str
    Empty_Bytes: bytes
    Empty_String: str
    Ellipse: str
    Forward_Slash: str
    Dot: str
    Hidden: str
    Indent: str
    Newline: str
    Non_Zero_Exit: int
    Nothing: str
    Single_Quote: str
    Slice_One: int
    Space: str
    Tab: str
    Underscore: str
    Xml: str
    Zero: int
    Zero_Exit: int


markers = Markers(

    Comma_Space=", ",
    Empty_Bytes=b"",
    Empty_String="",
    Ellipse="...",
    Forward_Slash="/",
    Dot=".",
    Hidden=".",
    Indent="   ",
    Newline="\n",
    Non_Zero_Exit=1,
    Nothing="",
    Single_Quote="'",
    Slice_One=1,
    Space=" ",
    Tab="\t",
    Underscore="_",
    Xml="xml",
    Zero=0,
    Zero_Exit=0,
)


# output constant
@dataclass(frozen=True)
class Output:
    """Define the Output dataclass for constant(s)."""

    Test_Start: str


output = Output(

    Test_Start=":sparkles: Start to run test suite for the specified program",
)
