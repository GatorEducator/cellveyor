"""Pytest test suite for the constants module."""

from cellveyor import constants


def test_humanreadable_constants() -> None:
    """Test Humanreadable constants have expected values."""
    assert constants.humanreadable.Yes == "Yes"
    assert constants.humanreadable.No == "No"


def test_markers_constants() -> None:
    """Test Markers constants have expected values."""
    assert constants.markers.Indent == "    "
    assert constants.markers.Newline == "\n"


def test_humanreadable_frozen() -> None:
    """Test Humanreadable dataclass is frozen."""
    try:
        constants.humanreadable.Yes = "No"  # type: ignore
        assert False, "should have raised"
    except AttributeError:
        assert True


def test_markers_frozen() -> None:
    """Test Markers dataclass is frozen."""
    try:
        constants.markers.Indent = "  "  # type: ignore
        assert False, "should have raised"
    except AttributeError:
        assert True
