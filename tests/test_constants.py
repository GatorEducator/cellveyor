"""Pytest test suite for the constants module."""

from dataclasses import FrozenInstanceError

import pytest
from hypothesis import given, strategies

from cellveyor import constants


def test_filesystem_constants():
    """Confirm default values of constants."""
    assert constants.filesystem.Current_Directory == "."
    assert constants.filesystem.Main_Configuration_File == "config.yml"
    assert constants.humanreadable.Yes == "Yes"
    assert constants.humanreadable.No == "No"


@given(
    directory=strategies.text(),
    configfile=strategies.text(),
    checksfile=strategies.text(),
    extra=strategies.text(),
    yes=strategies.text(),
    no=strategies.text(),
)
@pytest.mark.fuzz
def test_fuzz_init(directory, configfile, checksfile, extra, yes, no):  # noqa: PLR0913
    """Use Hypothesis to confirm that initial value is set correctly."""
    fs = constants.Filesystem(
        directory, configfile, checksfile, extra, extra, extra, extra, extra, extra
    )
    assert fs.Current_Directory == directory
    hr = constants.Humanreadable(yes, no)
    assert hr.Yes == yes
    assert hr.No == no


@given(
    fs=strategies.builds(constants.Filesystem),
    hr=strategies.builds(constants.Humanreadable),
)
@pytest.mark.fuzz
def test_fuzz_immutable(fs, hr):
    """Use Hypothesis to confirm that attribute's value cannot be re-assigned."""
    with pytest.raises(FrozenInstanceError):
        fs.Current_Directory = "/new/path"
    with pytest.raises(FrozenInstanceError):
        hr.Yes = "YES"
    with pytest.raises(FrozenInstanceError):
        hr.No = "NO"
