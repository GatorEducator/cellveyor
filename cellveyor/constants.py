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


# filesystem constant
@dataclass(frozen=True)
class Filesystem:
    """Define the Filesystem dataclass for constant(s)."""

    Current_Directory: str
    Dash: str
    Dot: str


filesystem = Filesystem(
    Current_Directory=".",
    Dash="-",
    Dot=".",
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

    Indent: str
    Newline: str


markers = Markers(
    Indent="    ",
    Newline="\n",
)
