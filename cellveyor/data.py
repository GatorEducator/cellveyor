"""Access and manipulate data."""

from pathlib import Path
from typing import Dict, Tuple

import pandas


def access_dataframes(spreadsheet_file: Path) -> Dict[str, pandas.DataFrame]:
    """Access all dataframes from the provided spreadsheet file."""
    name_to_dataframe_dict = pandas.read_excel(spreadsheet_file, sheet_name=None)
    return name_to_dataframe_dict


def key_attribute_column_filter(
    sheet_dataframe: pandas.DataFrame, key_attribute_name: str, column_regexp: str
) -> Tuple[pandas.DataFrame, pandas.DataFrame]:
    """Extract a region of a dataframe defined by a key attribute and columns that match a regular expression."""
    selected_columns = sheet_dataframe.filter(regex=column_regexp).dropna()
    result_df = sheet_dataframe[
        [key_attribute_name] + list(selected_columns.columns)  # noqa: RUF005
    ].dropna()
    return (selected_columns, result_df)  # type: ignore
