"""Access and manipulate data."""

from pathlib import Path
from typing import Dict, Tuple

import pandas

ALL = "all"


def access_dataframes(spreadsheet_file: Path) -> Dict[str, pandas.DataFrame]:
    """Access all dataframes from the provided spreadsheet file."""
    # read all of the dataframes from the provided spreadsheet file;
    # this will return a dictionary where the key is a string that
    # gives the name of a specific sheet and then the value is the dataframe
    name_to_dataframe_dict = pandas.read_excel(
        spreadsheet_file, sheet_name=None
    )
    return name_to_dataframe_dict


def key_attribute_column_filter(
    sheet_dataframe: pandas.DataFrame,
    key_attribute_name: str,
    column_regexp: str,
    key_attribute_value: str = "",
) -> Tuple[pandas.DataFrame, pandas.DataFrame]:
    """Extract a region of a dataframe defined by a key attribute and columns that match a regular expression."""
    # use the provided regular expression to extract from the data frame
    # only those columns that have a name that matches the regular expression
    # selected_columns = sheet_dataframe.filter(regex=column_regexp).dropna()
    selected_columns = sheet_dataframe.filter(regex=column_regexp)
    # extract the attribute that has the key name and also select all of
    # those columns that matched the regular expression
    result_df = sheet_dataframe[
        [key_attribute_name] + list(selected_columns.columns)  # noqa: RUF005
    ].dropna(how=ALL)  # type: ignore
    # filter down further for the specific value of the key attribute;
    # this is particularly useful when extracting and reporting data
    # for a specific row inside of the matching dataframe
    if key_attribute_value:
        result_df = result_df[
            result_df[key_attribute_name] == key_attribute_value
        ]
    # for both of the two previous steps, make sure to drop any rows that contain NA values
    # return the columns that were selected and then the resulting dataframe
    return (selected_columns, result_df)  # type: ignore
