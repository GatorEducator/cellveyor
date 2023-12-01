"""Pytest test suite for the filesystem module."""

import pytest

import pandas as pd
from cellveyor import data
from pathlib import Path


def test_access_dataframes() -> None:
    spreadsheet_file_one = "spreadsheets/fake_spreadsheet.xlsx"
    spreadsheet_file_two = "spreadsheets/example_spreadsheet.xlsx"
    test_one= data.access_dataframes(spreadsheet_file_one)
    test_two = data.access_dataframes(spreadsheet_file_two)
    assert test_one != test_two
