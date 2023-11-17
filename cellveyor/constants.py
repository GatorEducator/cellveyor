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

# logger constant
@dataclass(frozen=True)
class Logger:
    """Define the Logger dataclass for constant(s)."""

    Function_Prefix: str
    Richlog: str
    Syslog: str


logger = Logger(
    Function_Prefix="configure_logging_",
    Richlog="cellveyor-richlog",
    Syslog="cellveyor-syslog",
)


# logging constant
@dataclass(frozen=True)
class Logging:
    """Define the Logging dataclass for constant(s)."""

    Debug: str
    Info: str
    Warning: str
    Error: str
    Critical: str
    Console_Logging_Destination: str
    Default_Logging_Destination: str
    Default_Logging_Level: str
    Format: str
    Rich: str


logging = Logging(
    Info="INFO",
    Warning="WARNING",
    Error="ERROR",
    Critical="CRITICAL",
    Console_Logging_Destination="CONSOLE",
    Default_Logging_Destination="console",
    Default_Logging_Level="ERROR",
    Format="%(message)s",
    Rich="Rich",
)

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
    Small_Bullet_Unicode: str
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
    Small_Bullet_Unicode="\u2022",
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

    Syslog: str
    Test_Start: str


output = Output(

    Syslog="",
    Test_Start=":sparkles: Start to run test suite for the specified program",
)
