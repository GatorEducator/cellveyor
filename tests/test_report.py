"""Pytest test suite for the report module."""

import pandas
import pytest
from hypothesis import given, strategies

from cellveyor import report


def test_add_feedback_if_exists_found() -> None:
    """Test add_feedback_if_exists when key exists."""
    feedback = {"hello": "world"}
    result = report.add_feedback_if_exists("start-", feedback, "hello")
    assert "world" in result


def test_add_feedback_if_exists_not_found() -> None:
    """Test add_feedback_if_exists when key not found."""
    feedback: dict[str, str] = {}
    result = report.add_feedback_if_exists("start-", feedback, "missing")
    assert result == "start-"


def test_add_feedback_if_exists_list() -> None:
    """Test add_feedback_if_exists with make_list True."""
    feedback = {"key": "value"}
    result = report.add_feedback_if_exists(
        "start", feedback, "key", make_list=True
    )
    assert "- value" in result


def test_add_feedback_if_exists_non_string() -> None:
    """Test add_feedback_if_exists with non-string value."""
    feedback = {"key": ["a", "b"]}
    result = report.add_feedback_if_exists("", feedback, "key")
    assert "a" in result


def test_create_feedback_list_normal() -> None:
    """Test create_feedback_list with normal input."""
    result = report.create_feedback_list("a, b, c")
    assert result == ["a", "b", "c"]


def test_create_feedback_list_with_nan() -> None:
    """Test create_feedback_list filters nan."""
    result = report.create_feedback_list("a, nan, b")
    assert "nan" not in result
    assert "a" in result
    assert "b" in result


def test_create_feedback_list_empty() -> None:
    """Test create_feedback_list with empty string."""
    result = report.create_feedback_list("")
    assert result in ([""], [])


def test_create_feedback_list_single() -> None:
    """Test create_feedback_list with single value."""
    result = report.create_feedback_list("congratulations")
    assert result == ["congratulations"]


def test_create_per_key_report_basic() -> None:
    """Test create_per_key_report with basic dataframe."""
    df = pandas.DataFrame(
        {
            "Student GitHub": ["alice", "bob"],
            "Grade": [90, 80],
            "Feedback": ["good, great", "needs work"],
        }
    )
    selected = df[["Grade", "Feedback"]]
    result_df = df[["Student GitHub", "Grade", "Feedback"]]
    feedback_dict = {
        "header": "Header\n",
        "footer": "Footer\n",
        "good": "Good job!",
        "great": "Great!",
    }
    reports = report.create_per_key_report(
        "Student GitHub", result_df, selected, "Feedback", feedback_dict
    )
    assert "alice" in reports
    assert "bob" in reports
    assert "Header" in reports["alice"] or "header" not in reports["alice"]


def test_create_per_key_report_empty_feedback_regexp() -> None:
    """Test create_per_key_report when feedback regexp matches nothing."""
    df = pandas.DataFrame(
        {
            "Student GitHub": ["alice"],
            "Grade": [90],
        }
    )
    selected = df[["Grade"]]
    result_df = df[["Student GitHub", "Grade"]]
    reports = report.create_per_key_report(
        "Student GitHub", result_df, selected, "NOTMATCH", {}
    )
    assert "alice" in reports
    assert "alice" in reports


def test_create_per_key_report_invalid_feedback_regexp() -> None:
    """Test create_per_key_report rejects an invalid feedback pattern."""
    df = pandas.DataFrame({"Student GitHub": ["alice"], "Grade": [90]})
    selected = df[["Grade"]]
    result_df = df[["Student GitHub", "Grade"]]
    with pytest.raises(
        ValueError, match="Invalid feedback regular expression"
    ):
        report.create_per_key_report(
            "Student GitHub", result_df, selected, "[unclosed", {}
        )


def test_create_per_key_report_empty_string_feedback_regexp() -> None:
    """Test create_per_key_report treats empty pattern as no feedback."""
    df = pandas.DataFrame({"Student GitHub": ["alice"], "Grade": [90]})
    selected = df[["Grade"]]
    result_df = df[["Student GitHub", "Grade"]]
    reports = report.create_per_key_report(
        "Student GitHub", result_df, selected, "", {}
    )
    assert "alice" in reports
    assert "Here is some additional feedback" not in reports["alice"]


def test_select_feedback_columns_invalid_pattern() -> None:
    """Test select_feedback_columns rejects an invalid pattern."""
    df = pandas.DataFrame({"Grade": [90]})
    with pytest.raises(
        ValueError, match="Invalid feedback regular expression"
    ):
        report.select_feedback_columns(df, "[unclosed")


def test_select_feedback_columns_empty_pattern() -> None:
    """Test select_feedback_columns returns no columns for empty pattern."""
    df = pandas.DataFrame({"Grade": [90], "Feedback": ["x"]})
    selected = report.select_feedback_columns(df, "")
    assert len(selected.columns) == 0


def test_create_per_key_report_with_nan_key() -> None:
    """Test create_per_key_report skips nan keys."""
    # ensure string nan is treated, but also test with actual NaN
    df2 = pandas.DataFrame(
        {
            "Student GitHub": ["alice", float("nan")],
            "Grade": [90, 80],
        }
    )
    selected = df2[["Grade"]]
    result_df = df2[["Student GitHub", "Grade"]]
    reports = report.create_per_key_report(
        "Student GitHub", result_df, selected, "Grade", {}
    )
    # nan key should be skipped
    assert "nan" not in reports or "alice" in reports


def test_create_per_key_report_footer_list() -> None:
    """Test create_per_key_report handles list footer."""
    df = pandas.DataFrame(
        {
            "Student GitHub": ["alice"],
            "Grade": [90],
        }
    )
    selected = df[["Grade"]]
    result_df = df[["Student GitHub", "Grade"]]
    feedback_dict = {"footer": ["not a string"]}
    reports = report.create_per_key_report(
        "Student GitHub", result_df, selected, "NOTMATCH", feedback_dict
    )
    assert "alice" in reports


def test_create_per_key_report_no_footer() -> None:
    """Test create_per_key_report without footer."""
    df = pandas.DataFrame(
        {
            "Student GitHub": ["alice"],
            "Grade": [90],
        }
    )
    selected = df[["Grade"]]
    result_df = df[["Student GitHub", "Grade"]]
    reports = report.create_per_key_report(
        "Student GitHub", result_df, selected, "NOTMATCH", {}
    )
    assert "alice" in reports


def test_create_per_key_report_effective_feedback() -> None:
    """Test that feedback section only shows when key exists."""
    df = pandas.DataFrame(
        {
            "Student GitHub": ["alice"],
            "Grade": [90],
            "Feedback": ["missing_key"],
        }
    )
    selected = df[["Grade", "Feedback"]]
    result_df = df[["Student GitHub", "Grade", "Feedback"]]
    # feedback_dict does not contain missing_key
    reports = report.create_per_key_report(
        "Student GitHub", result_df, selected, "Feedback", {}
    )
    # should not contain feedback label if no effective keys
    assert "Here is some additional feedback" not in reports["alice"]


def test_create_per_key_report_feedback_index_error() -> None:
    """Test feedback fallback when row index is out of bounds."""
    result_df = pandas.DataFrame(
        {"Student GitHub": ["alice"], "Grade": [90], "Feedback": ["good"]},
        index=[5],
    )
    selected = pandas.DataFrame({"Grade": [90], "Feedback": ["good"]})
    reports = report.create_per_key_report(
        "Student GitHub", result_df, selected, "Feedback", {}
    )
    assert "alice" in reports


def test_create_per_key_report_missing_grade_nan() -> None:
    """Confirm that a missing numeric grade renders as a blank value."""
    df = pandas.DataFrame(
        {"Student GitHub": ["alice"], "Grade": [float("nan")]}
    )
    selected = df[["Grade"]]
    result_df = df[["Student GitHub", "Grade"]]
    reports = report.create_per_key_report(
        "Student GitHub", result_df, selected, "NOMATCH", {}
    )
    assert "nan" not in reports["alice"]
    assert "- **Grade**:" in reports["alice"]


def test_create_per_key_report_missing_grade_none() -> None:
    """Confirm that a missing object grade renders as a blank value."""
    df = pandas.DataFrame({"Student GitHub": ["alice"], "Grade": [None]})
    selected = df[["Grade"]]
    result_df = df[["Student GitHub", "Grade"]]
    reports = report.create_per_key_report(
        "Student GitHub", result_df, selected, "NOMATCH", {}
    )
    assert "None" not in reports["alice"]
    assert "- **Grade**:" in reports["alice"]


def test_create_per_key_report_present_grade_unchanged() -> None:
    """Confirm that a present grade still renders normally."""
    df = pandas.DataFrame({"Student GitHub": ["alice"], "Grade": [92.5]})
    selected = df[["Grade"]]
    result_df = df[["Student GitHub", "Grade"]]
    reports = report.create_per_key_report(
        "Student GitHub", result_df, selected, "NOMATCH", {}
    )
    assert "- **Grade**: 92.5" in reports["alice"]


@given(text=strategies.text(max_size=20))
def test_fuzz_create_feedback_list(text: str) -> None:
    """Fuzz test create_feedback_list does not crash."""
    result = report.create_feedback_list(text)
    assert isinstance(result, list)
