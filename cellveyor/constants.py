"""Define constants with dataclasses for use in Cellveyor"""

from dataclasses import dataclass


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
