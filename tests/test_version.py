"""Pytest test suite for the version module."""

import toml

from cellveyor import version


def test_version_exists() -> None:
    """Test that version constant exists and is a string."""
    assert hasattr(version, "CELLVEYOR_VERSION")
    assert isinstance(version.CELLVEYOR_VERSION, str)
    assert version.CELLVEYOR_VERSION == "0.1.0"


def test_version_matches_pyproject() -> None:
    """Test that version matches pyproject.toml."""
    with open("pyproject.toml", encoding="utf-8") as f:
        data = toml.load(f)
    pyproject_version = data["project"]["version"]
    assert version.CELLVEYOR_VERSION == pyproject_version
