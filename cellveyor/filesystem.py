"""Check and access contents of the filesystem."""

from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml
from pydantic import BaseModel, ConfigDict


class FeedbackFile(BaseModel):
    """Validated shape of a feedback file: header, footer, open keys."""

    model_config = ConfigDict(extra="allow")

    header: Optional[str] = None
    footer: Optional[str] = None


def load_feedback_file(
    feedback_file_path: Path,
) -> Tuple[Dict[str, str], str]:
    """Load one feedback file, returning its entries and a warning in cases when there was a malformed file."""
    # the warning is empty when the file loaded correctly;
    # otherwise it explains why the file was skipped entirely
    try:
        loaded_content = yaml.safe_load(
            feedback_file_path.read_text(encoding="utf-8")
        )
    except (OSError, yaml.YAMLError) as exc:
        return {}, f"unreadable content: {exc}"
    # empty files cannot provide any feedback entries
    if loaded_content is None:
        return {}, "empty file"
    # valid YAML that is not a mapping cannot provide feedback entries
    if not isinstance(loaded_content, dict):
        return {}, "expected a mapping of feedback entries"
    # coerce every key and value to text, mirroring how reports
    # already stringify non-string feedback; this keeps files like
    # the sample feedback.yml (with a list footer) loading cleanly
    coerced = {
        key if isinstance(key, str) else str(key): value
        if isinstance(value, str)
        else str(value)
        for key, value in loaded_content.items()
    }
    # validate the open-ended shape of the coerced mapping
    validated = FeedbackFile.model_validate(coerced)
    combined = dict(validated.model_extra or {})
    if validated.header is not None:
        combined["header"] = validated.header
    if validated.footer is not None:
        combined["footer"] = validated.footer
    return combined, ""


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


def read_feedback_files_with_warnings(
    feedback_files_list: List[Path] | None,
) -> Tuple[Dict[str, str], List[Path]]:
    """Read feedback files, returning combined entries and skipped paths."""
    # handle the case where no feedback files were provided
    if feedback_files_list is None:
        return {}, []
    feedback_dict_list: List[Dict[str, str]] = []
    skipped_paths: List[Path] = []
    # parse each file exactly once, sorting usable entries
    # from skipped paths as they are encountered
    for feedback_file_path in feedback_files_list:
        if confirm_valid_file(feedback_file_path):
            feedback_content, warning = load_feedback_file(feedback_file_path)
            if warning:
                skipped_paths.append(feedback_file_path)
            elif feedback_content:
                feedback_dict_list.append(feedback_content)
    # create an empty dictionary and then use it to store the
    # unified contents of all of the other dictionaries coming from
    # the previously input YAML files that contains the feedback pairs
    feedback_dict_combined: Dict[str, str] = {}
    for current_feedback_dict in feedback_dict_list:
        feedback_dict_combined.update(current_feedback_dict)
    # return the combined entries along with every path that was skipped
    return feedback_dict_combined, skipped_paths


def read_feedback_files(
    feedback_files_list: List[Path] | None,
) -> Dict[str, str]:
    """Read all of the feedback files and return them in a combined dictionary."""
    # reuse the single-pass reader, discarding the skipped paths here;
    # callers that warn about skipped files use the reader above directly
    combined, _ = read_feedback_files_with_warnings(feedback_files_list)
    return combined
