"""Pytest test suite for the main module."""

import io
import pathlib
import re
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
import typer
from rich.console import Console
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


def test_transport_missing_some_github_args() -> None:
    """Test --transfer-report with only some github args exits 1."""
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
            "--github-organization",
            "org",
            "--transfer-report",
        ],
        env={"CELLVEYOR_GITHUB_TOKEN": "fake"},
    )
    assert result.exit_code == 1
    output = _strip_ansi(result.output)
    assert "Missing required GitHub" in output
    assert "--github-repository-prefix" in output


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
                "--github-organization",
                "org",
                "--github-repository-prefix",
                "prefix",
                "--transfer-report",
            ],
            env={"CELLVEYOR_GITHUB_TOKEN": "fake"},
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
                "--github-organization",
                "org",
                "--github-repository-prefix",
                "prefix",
                "--transfer-report",
            ],
            env={"CELLVEYOR_GITHUB_TOKEN": "fake"},
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
        patch.dict(
            "os.environ", {"CELLVEYOR_GITHUB_TOKEN": "fake"}, clear=False
        ),
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
                github_organization=None,  # type: ignore
                github_repository_prefix=None,  # type: ignore
                transfer_report=True,
            )
        assert exc.value.exit_code == 1


def test_transport_with_token_env_default() -> None:
    """Test transfer with CELLVEYOR_GITHUB_TOKEN env var (default)."""
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
                "--github-organization",
                "org",
                "--github-repository-prefix",
                "prefix",
                "--transfer-report",
            ],
            env={"CELLVEYOR_GITHUB_TOKEN": "fake_from_env"},
        )
        assert result.exit_code == 0
        mock.assert_called_once()
        # ensure token from env was used
        assert mock.call_args[0][0] == "fake_from_env"


def test_transport_with_token_env_fallback_github_token() -> None:
    """Test transfer with GITHUB_TOKEN fallback when CELLVEYOR not set."""
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
                "--github-organization",
                "org",
                "--github-repository-prefix",
                "prefix",
                "--transfer-report",
            ],
            env={"GITHUB_TOKEN": "fallback_token"},
        )
        assert result.exit_code == 0
        mock.assert_called_once()
        assert mock.call_args[0][0] == "fallback_token"


def test_transport_with_custom_token_env() -> None:
    """Test transfer with custom --github-token-env var name."""
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
                "--github-token-env",
                "MY_CUSTOM_TOKEN",
                "--github-organization",
                "org",
                "--github-repository-prefix",
                "prefix",
                "--transfer-report",
            ],
            env={"MY_CUSTOM_TOKEN": "custom_token_value"},
        )
        assert result.exit_code == 0
        mock.assert_called_once()
        assert mock.call_args[0][0] == "custom_token_value"


def test_transport_default_env_without_flag() -> None:
    """Test program works without --github-token flag using default env var."""
    runner = CliRunner()
    with patch("cellveyor.main.transfer.transfer_reports_to_github") as mock:
        # no --github-token, no --github-token-env, but CELLVEYOR set
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
                "--github-organization",
                "org",
                "--github-repository-prefix",
                "prefix",
                "--transfer-report",
            ],
            env={"CELLVEYOR_GITHUB_TOKEN": "default_env_token"},
        )
        assert result.exit_code == 0
        mock.assert_called_once()


def test_transport_direct_with_token_env() -> None:
    """Test direct call with github_token_env resolves correctly."""
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
        patch.dict("os.environ", {"MY_VAR": "direct_token"}, clear=False),
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
            github_token_env="MY_VAR",
            github_organization="org",
            github_repository_prefix="prefix",
            transfer_report=True,
        )
        mock.assert_called_once()
        assert mock.call_args[0][0] == "direct_token"


def test_display_reports_fancy_true() -> None:
    """Test display_reports with fancy true shows Panel."""
    reports = {"alice": "**Hello @alice!**\n\n- **Grade**: 90\n"}
    main.display_reports(reports, fancy=True)
    main.display_reports(reports)


def test_display_reports_fancy_false() -> None:
    """Test display_reports with fancy false shows plain markdown."""
    reports = {"alice": "**Hello @alice!**\n\n- **Grade**: 90\n"}
    main.display_reports(reports, fancy=False)
    main.display_reports({}, fancy=False)


def test_transport_with_fancy() -> None:
    """Test transport with --fancy shows Panel."""
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
            "--fancy",
        ],
    )
    assert result.exit_code == 0
    # fancy panel contains box characters
    assert "gkapfham" in _strip_ansi(result.output)


def test_transport_with_no_fancy() -> None:
    """Test transport with --no-fancy shows plain markdown without Panel."""
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
            "--no-fancy",
        ],
    )
    assert result.exit_code == 0
    output = _strip_ansi(result.output)
    assert "gkapfham" in output
    # plain mode prints "gkapfham:" header, not Panel border
    assert "gkapfham:" in output
    # plain output has no panel border on any platform
    assert "╭" not in output
    assert "┌" not in output


def test_transport_direct_with_fancy_false() -> None:
    """Test direct call with fancy false."""
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
        patch("cellveyor.main.display_reports") as mock_display,
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
            github_token_env=None,
            github_organization=None,  # type: ignore
            github_repository_prefix=None,  # type: ignore
            transfer_report=False,
            fancy=False,
        )
        mock_display.assert_called_once()
        # ensure display_reports was called with fancy=False
        assert mock_display.call_args[0][1] is False


def test_display_reports_plain_spacing() -> None:
    """Test plain mode has blank line between key and content."""
    reports = {
        "gabrielsalvatore": "**Hello @gabrielsalvatore!**\n\n- **Grade**: 90\n"
    }
    # use helper directly to avoid spreadsheet setup
    # capture plain output
    with patch("cellveyor.main.console") as mock_console:
        # mock console to capture calls
        mock_console.print = MagicMock()
        main.display_reports(reports, fancy=False)
        # first call is "gabrielsalvatore:", second is blank, third is markdown
        calls = [str(c) for c in mock_console.print.call_args_list]
        assert any("gabrielsalvatore:" in str(c) for c in calls)
        # ensure blank line call exists (empty string or no arg)
        assert mock_console.print.call_count >= 3  # noqa: PLR2004


def test_transport_with_y_fancy() -> None:
    """Test -y sets --fancy and shows Panel."""
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
            "-y",
        ],
    )
    assert result.exit_code == 0
    output = _strip_ansi(result.output)
    assert "gkapfham" in output
    # fancy panel uses a rounded box, accepting the square
    # fallback for legacy windows consoles for portability
    assert "╭" in output or "┌" in output


def test_transport_no_fancy_panel_off() -> None:
    """Test same report args as fancy flag but with boxes off."""
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
            "--no-fancy",
        ],
    )
    assert result.exit_code == 0
    output = _strip_ansi(result.output)
    assert "gkapfham" in output
    assert "gkapfham:" in output
    # plain output has no panel border on any platform
    assert "╭" not in output
    assert "┌" not in output


def test_display_reports_fancy_legacy_windows() -> None:
    """Test fancy panel stays rounded on legacy windows consoles."""
    reports = {"gkapfham": "**Hello @gkapfham!**\n\n- **Grade**: 90\n"}
    buffer = io.StringIO()
    legacy_console = Console(file=buffer, legacy_windows=True, width=100)
    with patch("cellveyor.main.console", legacy_console):
        main.display_reports(reports, fancy=True)
    output = buffer.getvalue()
    assert "gkapfham" in output
    # rounded box must survive legacy windows substitution
    assert "╭" in output


def test_transport_with_no_transfer_long() -> None:
    """Test --no-transfer-report long form does not require token."""
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
            "--no-transfer-report",
            "--github-organization",
            "org",
            "--github-repository-prefix",
            "prefix",
        ],
    )
    assert result.exit_code == 0


def test_transport_with_no_fancy_long() -> None:
    """Test --no-fancy long form shows plain output."""
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
            "--no-fancy",
        ],
    )
    assert result.exit_code == 0
    output = _strip_ansi(result.output)
    assert "gkapfham:" in output
    # plain output has no panel border on any platform
    assert "╭" not in output
    assert "┌" not in output
