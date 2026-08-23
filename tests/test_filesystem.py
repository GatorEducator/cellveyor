"""Pytest test suite for the filesystem module."""

import pathlib
from unittest.mock import patch

import pytest
from hypothesis import given, strategies

from cellveyor import filesystem


def test_valid_directory() -> None:
    """Confirm that a valid directory is found."""
    directory_str = "./tests/"
    directory = pathlib.Path(directory_str)
    confirmation = filesystem.confirm_valid_directory(directory)
    assert confirmation is True


def test_invalid_directory() -> None:
    """Confirm that a valid directory is found."""
    directory_str = "./testsNOT/"
    directory = pathlib.Path(directory_str)
    confirmation = filesystem.confirm_valid_directory(directory)
    assert confirmation is False


def test_valid_file() -> None:
    """Confirm that a valid directory is found."""
    file_str = "./tests/test_filesystem.py"
    this_file = pathlib.Path(file_str)
    confirmation = filesystem.confirm_valid_file(this_file)
    assert confirmation is True


def test_invalid_file() -> None:
    """Confirm that a valid directory is found."""
    file_str = "./tests/test_filesystemNOT.py"
    this_file_not = pathlib.Path(file_str)
    confirmation = filesystem.confirm_valid_file(this_file_not)
    assert confirmation is False


@given(directory=strategies.builds(pathlib.Path))
@pytest.mark.fuzz
def test_fuzz_confirm_valid_directory_using_builds(
    directory: pathlib.Path,
) -> None:
    """Confirm that the function does not crash."""
    filesystem.confirm_valid_directory(directory=directory)


@given(file=strategies.builds(pathlib.Path))
@pytest.mark.fuzz
def test_fuzz_confirm_valid_file_using_builds(file: pathlib.Path) -> None:
    """Confirm that the function does not crash."""
    filesystem.confirm_valid_file(file=file)


def test_confirm_valid_file_none() -> None:
    """Confirm that a none file is not valid."""
    confirmation = filesystem.confirm_valid_file(None)  # type: ignore
    assert confirmation is False


def test_confirm_valid_directory_none() -> None:
    """Confirm that a none directory is not valid."""
    confirmation = filesystem.confirm_valid_directory(None)  # type: ignore
    assert confirmation is False


def test_read_feedback_files_none() -> None:
    """Confirm that a none feedback file list returns an empty dictionary."""
    assert filesystem.read_feedback_files(None) == {}


def test_read_feedback_files_empty(tmp_path: pathlib.Path) -> None:
    """Confirm that an empty feedback file is skipped."""
    empty_file = tmp_path / "empty.yml"
    empty_file.write_text("")
    assert filesystem.read_feedback_files([empty_file]) == {}


def test_read_feedback_files_non_dict(tmp_path: pathlib.Path) -> None:
    """Confirm that a non-dictionary feedback file is skipped."""
    list_file = tmp_path / "list.yml"
    list_file.write_text("- a\n- b\n")
    assert filesystem.read_feedback_files([list_file]) == {}


def test_read_feedback_files_malformed_yaml(tmp_path: pathlib.Path) -> None:
    """Confirm that a malformed feedback file is skipped."""
    bad_file = tmp_path / "bad.yml"
    bad_file.write_text("key: [unclosed\n")
    assert filesystem.read_feedback_files([bad_file]) == {}


def test_read_feedback_files_unreadable(tmp_path: pathlib.Path) -> None:
    """Confirm that an unreadable feedback file is skipped."""
    unreadable_file = tmp_path / "unreadable.yml"
    unreadable_file.write_text("header: Hello\n")
    with patch("pathlib.Path.read_text", side_effect=OSError("cannot read")):
        assert filesystem.read_feedback_files([unreadable_file]) == {}


def test_read_feedback_files_merge_order(tmp_path: pathlib.Path) -> None:
    """Confirm that later feedback files override earlier files."""
    first_file = tmp_path / "first.yml"
    first_file.write_text("header: First\nfooter: First footer\n")
    second_file = tmp_path / "second.yml"
    second_file.write_text("footer: Second footer\n")
    combined = filesystem.read_feedback_files([first_file, second_file])
    assert combined == {"header": "First", "footer": "Second footer"}
