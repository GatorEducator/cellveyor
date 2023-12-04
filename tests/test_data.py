"""Pytest test suite for the filesystem module."""

import pytest

import pandas as pd
from cellveyor import data
from pathlib import Path


def test_access_dataframes() -> None:
    spreadsheet_file_one = Path("spreadsheets/fake_spreadsheet.xlsx")
    spreadsheet_file_two = Path("spreadsheets/example_spreadsheet.xlsx")
    test_one = data.access_dataframes(spreadsheet_file_one)
    test_two = data.access_dataframes(spreadsheet_file_two)
    assert test_one != test_two


def test_key_attribute_column_filter() -> None:
    # Test key_attribute_column_filter function
    dataframes_dict = data.access_dataframes(Path("spreadsheets/fake_spreadsheet.xlsx"))
    sheet1_dataframe = dataframes_dict["Main"]

    # Test filtering with a key attribute and columns regex
    key_attribute_name = "Student GitHub"
    column_regexp = "^(Summary Grade|Final Grade) .*$"
    key_attribute_value = "gkapfham"
    selected_columns, result_df = data.key_attribute_column_filter(
        sheet1_dataframe, key_attribute_name, column_regexp, key_attribute_value
    )

    assert ("Summary Grade for Team Participation") in selected_columns.columns
    assert ("Student GitHub") in result_df.columns
    assert key_attribute_value in result_df["Student GitHub"].values
