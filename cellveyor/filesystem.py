"""Check and access contents of the filesystem."""

from pathlib import Path
from typing import Dict
from typing import List

import yaml


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
    # confirm that the directory that should contain the file is valid
    valid_directory = confirm_valid_directory(directory)
    # when the directory is valid, confirm that the file is valid
    if valid_directory:
        valid_file = confirm_valid_file(directory / file)
        # if the directory is valid and the file that is inside
        # of the directory is also valid, then it is a valid combination
        if valid_file:
            return True
    # the combination of the provided file and directory are not valid
    return False


def read_feedback_files(feedback_files_list: List[Path]) -> Dict[str, str]:
    """Read all of the feedback files and return them in a combined dictionary."""
    feedback_dict_list: List[Dict[str, str]] = []
    # iterate through all of the provided feedback files
    for feedback_file_path in feedback_files_list:
        # confirm that the file is valid; if it is valid
        # then its contents will be read and converted to a dictionary
        if confirm_valid_file(feedback_file_path):
            # read the contents of the file, which are a string
            # that contains within it the contents of the YAML file
            feedback_file_contents = feedback_file_path.read_text()
            # convert the string that encodes a YAML file to a dictionary
            feedback_file_contents_dict = yaml.safe_load(feedback_file_contents)
            # add the dictionary to the overall list of feedback dictionaries
            feedback_dict_list.append(feedback_file_contents_dict)
    # create an empty dictionary and then use it to store the
    # unified contents of all of the other dictionaries coming from
    # the previously input YAML files that contains the feedback pairs
    feedback_dict_combined: Dict[str, str] = {}
    for current_feedback_dict in feedback_dict_list:
        feedback_dict_combined.update(current_feedback_dict)
    # return the final dictionary that combines all dictionaries
    return feedback_dict_combined
