"""Check and access contents of the filesystem."""

from pathlib import Path


def confirm_valid_file(file: Path) -> bool:
    """Confirm that the provided file is a valid path that is a file."""
    # determine if the file is not None and if it is a file
    if file is not None:
        # the file is valid
        if file.is_file() and file.exists():
            return True
    # the file was either none or not valid
    return False


def confirm_valid_directory(directory: Path) -> bool:
    """Confirm that the provided directory is a valid path that is a directory."""
    # determine if the file is not None and if it is a file
    if directory is not None:
        # the file is valid
        if directory.is_dir() and directory.exists():
            return True
    # the directory was either none or not valid
    return False


def confirm_valid_file_in_directory(
    file: Path,
    directory: Path,
) -> bool:
    """Confirm that the file exists in a directory and then return it along with signal."""
    valid_directory = confirm_valid_directory(directory)
    if valid_directory:
        valid_file = confirm_valid_file(directory / file)
        if valid_file:
            return True
    return False
