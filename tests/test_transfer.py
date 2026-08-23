"""Pytest test suite for the transfer module."""

from unittest.mock import MagicMock, patch

import pytest

from cellveyor import transfer


def test_create_fully_qualified_github_repository() -> None:
    """Test repository name creation."""
    result = transfer.create_fully_qualified_github_repository(
        "org", "prefix", "user"
    )
    assert result == "org/prefix-user"


def test_create_fully_qualified_github_repository_with_dash() -> None:
    """Test repository name creation with special characters."""
    result = transfer.create_fully_qualified_github_repository(
        "Allegheny-Computer-Science-580-S2026",
        "junior-seminar-course-assessment",
        "gkapfham",
    )
    assert (
        result
        == "Allegheny-Computer-Science-580-S2026/junior-seminar-course-assessment-gkapfham"
    )


def test_transfer_reports_to_github_missing_token() -> None:
    """Test transfer_reports_to_github with missing token returns early."""
    transfer.transfer_reports_to_github(
        "", "org", "prefix", {"user": "report"}
    )
    transfer.transfer_reports_to_github(
        None,  # type: ignore
        "org",
        "prefix",
        {"user": "report"},
    )


def test_transfer_reports_to_github_missing_org() -> None:
    """Test transfer with missing organization."""
    transfer.transfer_reports_to_github(
        "token", "", "prefix", {"user": "report"}
    )
    transfer.transfer_reports_to_github(
        "token",
        None,  # type: ignore
        "prefix",
        {"user": "report"},
    )


def test_transfer_reports_to_github_missing_prefix() -> None:
    """Test transfer with missing prefix."""
    transfer.transfer_reports_to_github("token", "org", "", {"user": "report"})


def test_transfer_reports_to_github_empty_dict() -> None:
    """Test transfer with empty reports dict."""
    transfer.transfer_reports_to_github("token", "org", "prefix", {})


def test_transfer_reports_to_github_success() -> None:
    """Test successful transfer with mocked GitHub."""
    with patch("cellveyor.transfer.Github") as mock_github:
        mock_repo = MagicMock()
        mock_pull = MagicMock()
        mock_github.return_value.get_repo.return_value = mock_repo
        mock_repo.get_pull.return_value = mock_pull

        transfer.transfer_reports_to_github(
            "fake_token", "org", "prefix", {"alice": "report content"}
        )

        mock_github.return_value.get_repo.assert_called_once_with(
            "org/prefix-alice"
        )
        mock_pull.create_issue_comment.assert_called_once_with(
            "report content"
        )


def test_transfer_reports_to_github_handles_exception() -> None:
    """Test transfer handles GithubException per repo."""
    with patch("cellveyor.transfer.Github") as mock_github:
        mock_github.return_value.get_repo.side_effect = Exception(
            "repo not found"
        )

        # should not raise, should handle exception and continue
        transfer.transfer_reports_to_github(
            "fake_token", "org", "prefix", {"alice": "report"}
        )


def test_transfer_report_to_github_success() -> None:
    """Test transfer_report_to_github success with mock."""
    with (
        patch("cellveyor.transfer.Github") as mock_github,
        patch("cellveyor.transfer.Auth"),
    ):
        mock_repo = MagicMock()
        mock_pull = MagicMock()
        mock_github.return_value.get_repo.return_value = mock_repo
        mock_repo.get_pull.return_value = mock_pull

        transfer.transfer_report_to_github(
            "token", "org/prefix-user", "report"
        )
        mock_pull.create_issue_comment.assert_called_once_with("report")


def test_transfer_report_to_github_invalid_token() -> None:
    """Test transfer_report_to_github with invalid token raises."""
    with pytest.raises(ValueError):
        transfer.transfer_report_to_github("", "org/prefix-user", "report")
    with pytest.raises(ValueError):
        transfer.transfer_report_to_github(None, "org/prefix-user", "report")  # type: ignore


def test_transfer_report_to_github_invalid_repo() -> None:
    """Test transfer_report_to_github with invalid repo raises."""
    with pytest.raises(ValueError):
        transfer.transfer_report_to_github("token", "", "report")
    with pytest.raises(ValueError):
        transfer.transfer_report_to_github("token", None, "report")  # type: ignore


def test_transfer_report_to_github_handles_generic_exception() -> None:
    """Test transfer_report_to_github wraps generic exceptions."""
    with (
        patch("cellveyor.transfer.Github") as mock_github,
        patch("cellveyor.transfer.Auth"),
    ):
        mock_github.return_value.get_repo.side_effect = RuntimeError(
            "unexpected"
        )
        with pytest.raises(Exception):
            transfer.transfer_report_to_github(
                "token", "org/prefix-user", "report"
            )
