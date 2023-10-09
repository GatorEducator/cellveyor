"""Access and manipulate data."""

from pathlib import Path
from typing import Dict

import pandas


def access_dataframes(spreadsheet_file: Path) -> Dict[str, pandas.DataFrame]:
    """Access all dataframes from the provided spreadsheet file."""
    name_to_dataframe_dict = pandas.read_excel(spreadsheet_file, sheet_name=None)
    return name_to_dataframe_dict
