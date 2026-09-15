"""Pytest test suite for the data module."""

from pathlib import Path

import pandas

from cellveyor import data, report


def test_access_dataframes() -> None:
    """Test that access_dataframes returns different results for different files."""
    spreadsheet_file_one = Path("spreadsheets/fake_spreadsheet.xlsx")
    spreadsheet_file_two = Path("spreadsheets/example_spreadsheet.xlsx")
    test_one = data.access_dataframes(spreadsheet_file_one)
    test_two = data.access_dataframes(spreadsheet_file_two)
    assert test_one != test_two


def test_key_attribute_column_filter() -> None:
    """Test key_attribute_column_filter function."""
    dataframes_dict = data.access_dataframes(
        Path("spreadsheets/fake_spreadsheet.xlsx")
    )
    sheet1_dataframe = dataframes_dict["Main"]
    # test filtering with a key attribute and columns regex
    key_attribute_name = "Student GitHub"
    column_regexp = "^(Summary Grade|Final Grade) .*$"
    key_attribute_value = "gkapfham"
    selected_columns, result_df = data.key_attribute_column_filter(
        sheet1_dataframe,
        key_attribute_name,
        column_regexp,
        key_attribute_value,
    )
    assert ("Summary Grade for Team Participation") in selected_columns.columns
    assert ("Student GitHub") in result_df.columns
    assert key_attribute_value in result_df["Student GitHub"].values


def test_key_attribute_column_filter_does_not_duplicate_key() -> None:
    """Regression: column_regexp matching the key must not duplicate it."""
    # fake sheet where ".*" would otherwise match the key column itself
    dataframes_dict = data.access_dataframes(
        Path("spreadsheets/fake_spreadsheet.xlsx")
    )
    sheet_dataframe = dataframes_dict["Main"]
    key_attribute_name = "Student GitHub"
    for column_regexp in [".*", "Student.*", "Student GitHub"]:
        selected_columns, result_df = data.key_attribute_column_filter(
            sheet_dataframe, key_attribute_name, column_regexp
        )
        # selected must not contain the key — fix is to drop it
        assert key_attribute_name not in selected_columns.columns
        # result must have exactly one key column, no duplicates
        assert list(result_df.columns).count(key_attribute_name) == 1
        assert result_df.columns.duplicated().sum() == 0
        # row[key] must be scalar string, not a Series dump
        first_valid_key = result_df[result_df[key_attribute_name].notna()][
            key_attribute_name
        ].iloc[0]
        assert isinstance(first_valid_key, str)
        # end-to-end: report titles must be clean github handles
        per_key = report.create_per_key_report(
            key_attribute_name,
            result_df,
            selected_columns,
            "NONE",
            {},
        )
        # no garbled Series string like "Student GitHub    gkapfham"
        assert "gkapfham" in per_key
        assert not any(
            "Student GitHub    gkapfham" in title for title in per_key
        )
        assert not any("dtype: object" in title for title in per_key)


def test_key_attribute_column_filter_duplicate_key_minimal_dataframe() -> None:
    """Regression with minimal dataframe: ensure no duplicate when regexp is '.*'."""
    df = pandas.DataFrame(
        {
            "Student GitHub": ["alice", "bob", float("nan")],
            "Student Name": ["Alice", "Bob", float("nan")],
            "Grade": [90, 80, float("nan")],
        }
    )
    selected_columns, result_df = data.key_attribute_column_filter(
        df, "Student GitHub", ".*"
    )
    assert "Student GitHub" not in selected_columns.columns
    assert list(result_df.columns).count("Student GitHub") == 1
    # naN-key rows survive data filter (dropna how="all" keeps rows with any grade),
    # but report must still skip them — ensure data layer doesn't create Series
    per_key = report.create_per_key_report(
        "Student GitHub", result_df, selected_columns, "NONE", {}
    )
    assert "alice" in per_key
    assert "bob" in per_key
    assert "nan" not in per_key
    assert not any("dtype: object" in k for k in per_key)
