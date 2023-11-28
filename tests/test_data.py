"""Pytest test suite for the filesystem module."""

import pytest

import pandas as pd
from cellveyor import data
from pathlib import Path


def test_access_dataframes() -> None:
    spreadsheet_file = "spreadsheets/fake_spreadsheet.xlsx"
    result = data.access_dataframes(spreadsheet_file)
    expected_sheet1 = pd.DataFrame({'column1': [1, 2, 3], 'column2': ['A', 'B', 'C']})
    expected_sheet2 = pd.DataFrame({'columnA': [4, 5, 6], 'columnB': ['X', 'Y', 'Z']})

    assert pd.DataFrame.equals(result['Sheet1'], expected_sheet1)
    assert pd.DataFrame.equals(result['Sheet2'], expected_sheet2)