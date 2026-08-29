"""Pytest test suite for the main module."""

import pathlib
import re
from unittest.mock import patch

import pandas as pd
import pytest
import typer
from typer.testing import CliRunner

from cellveyor import main


def _strip_ansi(text: str) -> str:
    """Strip ANSI escape codes for robust output checking."""
    return re.sub(r"\x1b\[[0-9;]*m", "", text)


def test_display_reports() -> None:
    """Test display_reports does not crash."""
    reports = {"alice": "**Hello @alice!**\n\n- **Grade**: 90\n"}
    main.display_reports(reports)
    main.display_reports({})


def test_print_dash_list() -> None:
    """Test _print_dash_list does not crash."""
    main._print_dash_list("Available sheets", ["Main", "TP"], color="red")
    main._print_dash_list("Available columns", [], color="yellow")
    main._print_dash_list("Title", ["a\nb", "c\r d"], color="red")


def test_transport_valid(tmp_path: pathlib.Path) -> None:
    """Test transport with valid spreadsheet."""
    runner = CliRunner()
    result = runner.invoke(
        main.cli,
        [
            "--spreadsheet-directory",
            "spreadsheets",
            "--spreadsheet-file",
            "fake_spreadsheet.xlsx",
            "--sheet-name",
            "Main",
            "--key-attribute",
            "Student GitHub",
            "--column-regexp",
            "^(Summary Grade|Final Grade) .*$",
            "--feedback-regexp",
            "Summary Grade 1 - Feedback",
            "--feedback-file",
            "spreadsheets/feedback.yml",
        ],
    )
    assert result.exit_code == 0
    assert "gkapfham" in _strip_ansi(
        result.output
    ) or "Accessing" in _strip_ansi(result.output)


def test_transport_missing_file() -> None:
    """Test transport with missing file exits 1."""
    runner = CliRunner()
    result = runner.invoke(
        main.cli,
        [
            "--spreadsheet-directory",
            "/tmp",
            "--spreadsheet-file",
            "NOTEXIST.xlsx",
            "--sheet-name",
            "Main",
            "--key-attribute",
            "Student GitHub",
            "--column-regexp",
            ".*",
            "--feedback-regexp",
            ".*",
        ],
    )
    assert result.exit_code == 1
    assert "Unable to access" in _strip_ansi(result.output)


def test_transport_missing_directory() -> None:
    """Test transport with missing directory exits 1."""
    runner = CliRunner()
    result = runner.invoke(
        main.cli,
        [
            "--spreadsheet-directory",
            "/tmp/not_a_dir_xyz_123",
            "--spreadsheet-file",
            "fake.xlsx",
            "--sheet-name",
            "Main",
            "--key-attribute",
            "Student GitHub",
            "--column-regexp",
            ".*",
            "--feedback-regexp",
            ".*",
        ],
    )
    assert result.exit_code == 1
    assert "Directory not found" in _strip_ansi(result.output)


def test_transport_wrong_sheet() -> None:
    """Test transport with wrong sheet exits 1."""
    runner = CliRunner()
    result = runner.invoke(
        main.cli,
        [
            "--spreadsheet-directory",
            "spreadsheets",
            "--spreadsheet-file",
            "fake_spreadsheet.xlsx",
            "--sheet-name",
            "NOTASHEET",
            "--key-attribute",
            "Student GitHub",
            "--column-regexp",
            ".*",
            "--feedback-regexp",
            ".*",
        ],
    )
    assert result.exit_code == 1
    assert "Sheet 'NOTASHEET' not found" in _strip_ansi(result.output)
    assert "Available sheets:" in _strip_ansi(result.output)


def test_transport_wrong_key_attribute() -> None:
    """Test transport with wrong key attribute exits 1."""
    runner = CliRunner()
    result = runner.invoke(
        main.cli,
        [
            "--spreadsheet-directory",
            "spreadsheets",
            "--spreadsheet-file",
            "fake_spreadsheet.xlsx",
            "--sheet-name",
            "Main",
            "--key-attribute",
            "NONEXISTENT",
            "--column-regexp",
            ".*",
            "--feedback-regexp",
            ".*",
        ],
    )
    assert result.exit_code == 1
    assert "Key attribute" in _strip_ansi(result.output)
    assert "Available columns:" in _strip_ansi(result.output)


def test_transport_no_columns_matched() -> None:
    """Test transport with no columns matched warns but does not crash."""
    runner = CliRunner()
    result = runner.invoke(
        main.cli,
        [
            "--spreadsheet-directory",
            "spreadsheets",
            "--spreadsheet-file",
            "fake_spreadsheet.xlsx",
            "--sheet-name",
            "Main",
            "--key-attribute",
            "Student GitHub",
            "--column-regexp",
            "^NONEXISTENT.*$",
            "--feedback-regexp",
            "NOTMATCH",
            "--feedback-file",
            "spreadsheets/feedback.yml",
        ],
    )
    assert result.exit_code == 0
    assert "No columns matched" in _strip_ansi(result.output)
    assert "Available columns:" in _strip_ansi(result.output)


def test_transport_invalid_regex() -> None:
    """Test transport with invalid regex exits 1."""
    runner = CliRunner()
    result = runner.invoke(
        main.cli,
        [
            "--spreadsheet-directory",
            "spreadsheets",
            "--spreadsheet-file",
            "fake_spreadsheet.xlsx",
            "--sheet-name",
            "Main",
            "--key-attribute",
            "Student GitHub",
            "--column-regexp",
            "[unclosed",
            "--feedback-regexp",
            ".*",
        ],
    )
    assert result.exit_code == 1


def test_transport_missing_github_args() -> None:
    """Test transport with --transfer-report but missing github args exits 1."""
    runner = CliRunner()
    result = runner.invoke(
        main.cli,
        [
            "--spreadsheet-directory",
            "spreadsheets",
            "--spreadsheet-file",
            "fake_spreadsheet.xlsx",
            "--sheet-name",
            "Main",
            "--key-attribute",
            "Student GitHub",
            "--column-regexp",
            ".*",
            "--feedback-regexp",
            ".*",
            "--transfer-report",
        ],
    )
    assert result.exit_code == 1
    assert "Missing required GitHub" in _strip_ansi(result.output)


def test_transport_with_feedback_missing_file() -> None:
    """Test transport with missing feedback file warns."""
    runner = CliRunner()
    result = runner.invoke(
        main.cli,
        [
            "--spreadsheet-directory",
            "spreadsheets",
            "--spreadsheet-file",
            "fake_spreadsheet.xlsx",
            "--sheet-name",
            "Main",
            "--key-attribute",
            "Student GitHub",
            "--column-regexp",
            "^(Summary Grade|Final Grade) .*$",
            "--feedback-regexp",
            "Summary Grade 1 - Feedback",
            "--feedback-file",
            "/tmp/notexist.yml",
        ],
    )
    assert result.exit_code == 0
    assert "Feedback file(s) not found" in _strip_ansi(result.output)


def test_transport_with_key_value_filter() -> None:
    """Test transport with --key-value filter."""
    runner = CliRunner()
    result = runner.invoke(
        main.cli,
        [
            "--spreadsheet-directory",
            "spreadsheets",
            "--spreadsheet-file",
            "fake_spreadsheet.xlsx",
            "--sheet-name",
            "Main",
            "--key-attribute",
            "Student GitHub",
            "--column-regexp",
            "^(Summary Grade|Final Grade) .*$",
            "--feedback-regexp",
            "Summary Grade 1 - Feedback",
            "--key-value",
            "gkapfham",
        ],
    )
    assert result.exit_code == 0


def test_transport_no_reports_generated(tmp_path: pathlib.Path) -> None:
    """Test transport when filter yields no rows warns."""
    runner = CliRunner()
    result = runner.invoke(
        main.cli,
        [
            "--spreadsheet-directory",
            "spreadsheets",
            "--spreadsheet-file",
            "fake_spreadsheet.xlsx",
            "--sheet-name",
            "Main",
            "--key-attribute",
            "Student GitHub",
            "--column-regexp",
            "^(Summary Grade|Final Grade) .*$",
            "--feedback-regexp",
            "Summary Grade 1 - Feedback",
            "--key-value",
            "nonexistent_user_xyz",
        ],
    )
    # should warn about no reports or no rows
    assert result.exit_code == 0
    assert (
        "No reports generated" in _strip_ansi(result.output)
        or "No rows found" in _strip_ansi(result.output)
        or "gkapfham" not in _strip_ansi(result.output)
    )


def test_transport_with_transfer_mock() -> None:
    """Test transport with mocked GitHub transfer."""
    runner = CliRunner()
    with patch("cellveyor.main.transfer.transfer_reports_to_github") as mock:
        result = runner.invoke(
            main.cli,
            [
                "--spreadsheet-directory",
                "spreadsheets",
                "--spreadsheet-file",
                "fake_spreadsheet.xlsx",
                "--sheet-name",
                "Main",
                "--key-attribute",
                "Student GitHub",
                "--column-regexp",
                ".*",
                "--feedback-regexp",
                ".*",
                "--github-token",
                "fake",
                "--github-organization",
                "org",
                "--github-repository-prefix",
                "prefix",
                "--transfer-report",
            ],
        )
        assert result.exit_code == 0
        mock.assert_called_once()


def test_transport_transfer_failure() -> None:
    """Test transport handles transfer failure."""
    runner = CliRunner()
    with patch(
        "cellveyor.main.transfer.transfer_reports_to_github",
        side_effect=Exception("fail"),
    ):
        result = runner.invoke(
            main.cli,
            [
                "--spreadsheet-directory",
                "spreadsheets",
                "--spreadsheet-file",
                "fake_spreadsheet.xlsx",
                "--sheet-name",
                "Main",
                "--key-attribute",
                "Student GitHub",
                "--column-regexp",
                ".*",
                "--feedback-regexp",
                ".*",
                "--github-token",
                "fake",
                "--github-organization",
                "org",
                "--github-repository-prefix",
                "prefix",
                "--transfer-report",
            ],
        )
        assert result.exit_code == 1
        assert "GitHub transfer failed" in _strip_ansi(result.output)


def test_transport_spreadsheet_read_filenotfound() -> None:
    """Test transport when the spreadsheet read raises FileNotFoundError."""
    runner = CliRunner()
    with patch(
        "cellveyor.main.data.access_dataframes",
        side_effect=FileNotFoundError("missing"),
    ):
        result = runner.invoke(
            main.cli,
            [
                "--spreadsheet-directory",
                "spreadsheets",
                "--spreadsheet-file",
                "fake_spreadsheet.xlsx",
                "--sheet-name",
                "Main",
                "--key-attribute",
                "Student GitHub",
                "--column-regexp",
                ".*",
                "--feedback-regexp",
                ".*",
            ],
        )
    assert result.exit_code == 1
    assert "Spreadsheet file not found" in _strip_ansi(result.output)


def test_transport_spreadsheet_read_generic_error() -> None:
    """Test transport when reading the spreadsheet fails unexpectedly."""
    runner = CliRunner()
    with patch(
        "cellveyor.main.data.access_dataframes",
        side_effect=Exception("boom"),
    ):
        result = runner.invoke(
            main.cli,
            [
                "--spreadsheet-directory",
                "spreadsheets",
                "--spreadsheet-file",
                "fake_spreadsheet.xlsx",
                "--sheet-name",
                "Main",
                "--key-attribute",
                "Student GitHub",
                "--column-regexp",
                ".*",
                "--feedback-regexp",
                ".*",
            ],
        )
    assert result.exit_code == 1
    assert "Failed to read spreadsheet" in _strip_ansi(result.output)


def test_transport_column_filter_generic_error() -> None:
    """Test transport when the column filter fails unexpectedly."""
    runner = CliRunner()
    with patch(
        "cellveyor.main.data.key_attribute_column_filter",
        side_effect=RuntimeError("boom"),
    ):
        result = runner.invoke(
            main.cli,
            [
                "--spreadsheet-directory",
                "spreadsheets",
                "--spreadsheet-file",
                "fake_spreadsheet.xlsx",
                "--sheet-name",
                "Main",
                "--key-attribute",
                "Student GitHub",
                "--column-regexp",
                ".*",
                "--feedback-regexp",
                ".*",
            ],
        )
    assert result.exit_code == 1
    assert "Failed to filter columns" in _strip_ansi(result.output)


def test_transport_report_creation_error() -> None:
    """Test transport when report creation fails unexpectedly."""
    runner = CliRunner()
    with patch(
        "cellveyor.main.report.create_per_key_report",
        side_effect=RuntimeError("boom"),
    ):
        result = runner.invoke(
            main.cli,
            [
                "--spreadsheet-directory",
                "spreadsheets",
                "--spreadsheet-file",
                "fake_spreadsheet.xlsx",
                "--sheet-name",
                "Main",
                "--key-attribute",
                "Student GitHub",
                "--column-regexp",
                ".*",
                "--feedback-regexp",
                ".*",
            ],
        )
    assert result.exit_code == 1
    assert "Failed to create reports" in _strip_ansi(result.output)


def test_transport_direct_success() -> None:
    """Test direct call to transport succeeds with mocked dependencies."""
    # create minimal dataframe and mock all internal calls
    fake_df = pd.DataFrame({"Student GitHub": ["alice"], "Grade": [90]})
    fake_dict = {"Main": fake_df}
    selected = fake_df[["Grade"]]
    result_df = fake_df
    with (
        patch(
            "cellveyor.main.filesystem.confirm_valid_file_in_directory",
            return_value=True,
        ),
        patch(
            "cellveyor.main.filesystem.read_feedback_files", return_value={}
        ),
        patch(
            "cellveyor.main.filesystem.confirm_valid_file", return_value=True
        ),
        patch("cellveyor.main.data.access_dataframes", return_value=fake_dict),
        patch(
            "cellveyor.main.data.key_attribute_column_filter",
            return_value=(selected, result_df),
        ),
        patch(
            "cellveyor.main.report.create_per_key_report",
            return_value={"alice": "report"},
        ),
        patch("cellveyor.main.display_reports"),
    ):
        # direct call should not raise
        main.transport(
            spreadsheet_directory=pathlib.Path("spreadsheets"),
            spreadsheet_file=pathlib.Path("fake_spreadsheet.xlsx"),
            sheet_name="Main",
            key_attribute="Student GitHub",
            column_regexp=".*",
            feedback_regexp=".*",
            key_value=None,  # type: ignore
            feedback_file=None,  # type: ignore
            github_token=None,  # type: ignore
            github_organization=None,  # type: ignore
            github_repository_prefix=None,  # type: ignore
            transfer_report=False,
        )


def test_transport_direct_invalid_directory() -> None:
    """Test direct call to transport with invalid directory exits."""
    with pytest.raises(typer.Exit) as exc:
        main.transport(
            spreadsheet_directory=pathlib.Path("/tmp/not_a_dir_xyz_12345"),
            spreadsheet_file=pathlib.Path("fake.xlsx"),
            sheet_name="Main",
            key_attribute="Student GitHub",
            column_regexp=".*",
            feedback_regexp=".*",
            key_value=None,  # type: ignore
            feedback_file=None,  # type: ignore
            github_token=None,  # type: ignore
            github_organization=None,  # type: ignore
            github_repository_prefix=None,  # type: ignore
            transfer_report=False,
        )
    assert exc.value.exit_code == 1


def test_transport_direct_invalid_file_in_valid_directory(
    tmp_path: pathlib.Path,
) -> None:
    """Test direct call with valid directory but missing file exits."""
    with pytest.raises(typer.Exit) as exc:
        main.transport(
            spreadsheet_directory=tmp_path,
            spreadsheet_file=pathlib.Path("nonexistent.xlsx"),
            sheet_name="Main",
            key_attribute="Student GitHub",
            column_regexp=".*",
            feedback_regexp=".*",
            key_value=None,  # type: ignore
            feedback_file=None,  # type: ignore
            github_token=None,  # type: ignore
            github_organization=None,  # type: ignore
            github_repository_prefix=None,  # type: ignore
            transfer_report=False,
        )
    assert exc.value.exit_code == 1


def test_transport_direct_wrong_sheet() -> None:
    """Test direct call with wrong sheet triggers exit."""
    fake_df = pd.DataFrame({"Student GitHub": ["alice"], "Grade": [90]})
    fake_dict = {"Main": fake_df}
    with (
        patch(
            "cellveyor.main.filesystem.confirm_valid_file_in_directory",
            return_value=True,
        ),
        patch(
            "cellveyor.main.filesystem.read_feedback_files", return_value={}
        ),
        patch("cellveyor.main.data.access_dataframes", return_value=fake_dict),
    ):
        with pytest.raises(typer.Exit) as exc:
            main.transport(
                spreadsheet_directory=pathlib.Path("spreadsheets"),
                spreadsheet_file=pathlib.Path("fake_spreadsheet.xlsx"),
                sheet_name="NOTASHEET",
                key_attribute="Student GitHub",
                column_regexp=".*",
                feedback_regexp=".*",
                key_value=None,  # type: ignore
                feedback_file=None,  # type: ignore
                github_token=None,  # type: ignore
                github_organization=None,  # type: ignore
                github_repository_prefix=None,  # type: ignore
                transfer_report=False,
            )
        assert exc.value.exit_code == 1


def test_transport_direct_wrong_key_attribute() -> None:
    """Test direct call with wrong key attribute triggers exit."""
    fake_df = pd.DataFrame({"Student GitHub": ["alice"], "Grade": [90]})
    fake_dict = {"Main": fake_df}
    with (
        patch(
            "cellveyor.main.filesystem.confirm_valid_file_in_directory",
            return_value=True,
        ),
        patch(
            "cellveyor.main.filesystem.read_feedback_files", return_value={}
        ),
        patch("cellveyor.main.data.access_dataframes", return_value=fake_dict),
        patch(
            "cellveyor.main.data.key_attribute_column_filter",
            side_effect=ValueError("Key attribute 'BAD' not found"),
        ),
    ):
        with pytest.raises(typer.Exit) as exc:
            main.transport(
                spreadsheet_directory=pathlib.Path("spreadsheets"),
                spreadsheet_file=pathlib.Path("fake_spreadsheet.xlsx"),
                sheet_name="Main",
                key_attribute="BAD",
                column_regexp=".*",
                feedback_regexp=".*",
                key_value=None,  # type: ignore
                feedback_file=None,  # type: ignore
                github_token=None,  # type: ignore
                github_organization=None,  # type: ignore
                github_repository_prefix=None,  # type: ignore
                transfer_report=False,
            )
        assert exc.value.exit_code == 1


def test_transport_direct_with_feedback_missing_file() -> None:
    """Test direct call warns about missing feedback file but succeeds."""
    fake_df = pd.DataFrame({"Student GitHub": ["alice"], "Grade": [90]})
    fake_dict = {"Main": fake_df}
    selected = fake_df[["Grade"]]
    result_df = fake_df
    with (
        patch(
            "cellveyor.main.filesystem.confirm_valid_file_in_directory",
            return_value=True,
        ),
        patch(
            "cellveyor.main.filesystem.confirm_valid_file", return_value=False
        ),
        patch(
            "cellveyor.main.filesystem.read_feedback_files", return_value={}
        ),
        patch("cellveyor.main.data.access_dataframes", return_value=fake_dict),
        patch(
            "cellveyor.main.data.key_attribute_column_filter",
            return_value=(selected, result_df),
        ),
        patch(
            "cellveyor.main.report.create_per_key_report",
            return_value={"alice": "report"},
        ),
        patch("cellveyor.main.display_reports"),
    ):
        main.transport(
            spreadsheet_directory=pathlib.Path("spreadsheets"),
            spreadsheet_file=pathlib.Path("fake_spreadsheet.xlsx"),
            sheet_name="Main",
            key_attribute="Student GitHub",
            column_regexp=".*",
            feedback_regexp=".*",
            key_value=None,  # type: ignore
            feedback_file=[pathlib.Path("/tmp/notexist.yml")],
            github_token=None,  # type: ignore
            github_organization=None,  # type: ignore
            github_repository_prefix=None,  # type: ignore
            transfer_report=False,
        )


def test_transport_direct_no_columns_matched() -> None:
    """Test direct call with no columns matched warns but succeeds."""
    fake_df = pd.DataFrame({"Student GitHub": ["alice"], "Grade": [90]})
    fake_dict = {"Main": fake_df}
    selected = pd.DataFrame()
    result_df = fake_df
    with (
        patch(
            "cellveyor.main.filesystem.confirm_valid_file_in_directory",
            return_value=True,
        ),
        patch(
            "cellveyor.main.filesystem.read_feedback_files", return_value={}
        ),
        patch("cellveyor.main.data.access_dataframes", return_value=fake_dict),
        patch(
            "cellveyor.main.data.key_attribute_column_filter",
            return_value=(selected, result_df),
        ),
        patch(
            "cellveyor.main.report.create_per_key_report",
            return_value={"alice": "report"},
        ),
        patch("cellveyor.main.display_reports"),
    ):
        main.transport(
            spreadsheet_directory=pathlib.Path("spreadsheets"),
            spreadsheet_file=pathlib.Path("fake_spreadsheet.xlsx"),
            sheet_name="Main",
            key_attribute="Student GitHub",
            column_regexp="^NONEXISTENT.*$",
            feedback_regexp=".*",
            key_value=None,  # type: ignore
            feedback_file=None,  # type: ignore
            github_token=None,  # type: ignore
            github_organization=None,  # type: ignore
            github_repository_prefix=None,  # type: ignore
            transfer_report=False,
        )


def test_transport_direct_transfer_with_mock() -> None:
    """Test direct call with transfer enabled and mocked github."""
    fake_df = pd.DataFrame({"Student GitHub": ["alice"], "Grade": [90]})
    fake_dict = {"Main": fake_df}
    selected = fake_df[["Grade"]]
    result_df = fake_df
    with (
        patch(
            "cellveyor.main.filesystem.confirm_valid_file_in_directory",
            return_value=True,
        ),
        patch(
            "cellveyor.main.filesystem.read_feedback_files", return_value={}
        ),
        patch("cellveyor.main.data.access_dataframes", return_value=fake_dict),
        patch(
            "cellveyor.main.data.key_attribute_column_filter",
            return_value=(selected, result_df),
        ),
        patch(
            "cellveyor.main.report.create_per_key_report",
            return_value={"alice": "report"},
        ),
        patch("cellveyor.main.display_reports"),
        patch("cellveyor.main.transfer.transfer_reports_to_github") as mock,
    ):
        main.transport(
            spreadsheet_directory=pathlib.Path("spreadsheets"),
            spreadsheet_file=pathlib.Path("fake_spreadsheet.xlsx"),
            sheet_name="Main",
            key_attribute="Student GitHub",
            column_regexp=".*",
            feedback_regexp=".*",
            key_value=None,  # type: ignore
            feedback_file=None,  # type: ignore
            github_token="fake",
            github_organization="org",
            github_repository_prefix="prefix",
            transfer_report=True,
        )
        mock.assert_called_once()


def test_transport_direct_missing_github_args() -> None:
    """Test direct call with transfer but missing github args exits."""
    fake_df = pd.DataFrame({"Student GitHub": ["alice"], "Grade": [90]})
    fake_dict = {"Main": fake_df}
    selected = fake_df[["Grade"]]
    result_df = fake_df
    with (
        patch(
            "cellveyor.main.filesystem.confirm_valid_file_in_directory",
            return_value=True,
        ),
        patch(
            "cellveyor.main.filesystem.read_feedback_files", return_value={}
        ),
        patch("cellveyor.main.data.access_dataframes", return_value=fake_dict),
        patch(
            "cellveyor.main.data.key_attribute_column_filter",
            return_value=(selected, result_df),
        ),
        patch(
            "cellveyor.main.report.create_per_key_report",
            return_value={"alice": "report"},
        ),
        patch("cellveyor.main.display_reports"),
    ):
        with pytest.raises(typer.Exit) as exc:
            main.transport(
                spreadsheet_directory=pathlib.Path("spreadsheets"),
                spreadsheet_file=pathlib.Path("fake_spreadsheet.xlsx"),
                sheet_name="Main",
                key_attribute="Student GitHub",
                column_regexp=".*",
                feedback_regexp=".*",
                key_value=None,  # type: ignore
                feedback_file=None,  # type: ignore
                github_token=None,  # type: ignore
                github_organization=None,  # type: ignore
                github_repository_prefix=None,  # type: ignore
                transfer_report=True,
            )
        assert exc.value.exit_code == 1
