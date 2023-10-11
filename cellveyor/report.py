"""Create reports based on content in dataframes."""

from typing import Dict

from pandas import DataFrame

NEWLINE = "\n"
HEADER = "header"
FOOTER = "footer"
SUMMARY_LABEL = "Here are your summary scores:"


def add_feedback_if_exists(
    report: str, feedback_dict: Dict[str, str], feedback_key: str
) -> str:
    """Add feedback to the provided report if a specified key exists in the dictionary."""
    # the final report will start off as the contents
    # of the report provided as an argument
    final_report = report
    # the feedback dictionary contains the requested key and
    # thus this function should add the key's value to the report
    if feedback_key in feedback_dict:
        feedback = feedback_dict[feedback_key]
        final_report = final_report + f"{feedback}{NEWLINE}"
    # return the potentially improved feedback report
    return final_report


def create_per_key_report(
    key_attribute: str,
    result_dataframe: DataFrame,
    selected_columns: DataFrame,
    feedback_dict: Dict[str, str],
) -> Dict[str, str]:
    """Create a per-key report for the provided dataframe."""
    # create an empty dictionary for the reports, organized as:
    # --> key: the value for the key attribute (normally a GitHub user name)
    # --> value: an entire report, encoded in markdown for display in the terminal
    # or upload to a markdown-aware platform like a GitHub issue or pull request
    markdown_reports: Dict[str, str] = {}
    # create a unique message for each row in the dataframe
    for _, row in result_dataframe.iterrows():
        # extract the value of the key attribute
        key_attribute_value = str(row[key_attribute])
        # create a main label for the entire markdown-based report
        current_report = f"**Hello @{key_attribute_value}!**{NEWLINE}{NEWLINE}"
        # current_report = current_report + f"{feedback_dict[HEADER]}{NEWLINE}"
        current_report = add_feedback_if_exists(current_report, feedback_dict, HEADER)
        current_report = current_report + f"**{SUMMARY_LABEL}**{NEWLINE}{NEWLINE}"
        # iterate through all of the extracted columns and add them to
        # the report in the following fashion:
        # - Name of the Column: Value of the Column
        # this process should continue to incrementally
        # add data to the current report for every column and its value
        for column_name in selected_columns.columns:
            column_value = row[column_name]
            current_report = (
                current_report + f"- **{column_name}**: {column_value}{NEWLINE}"
            )
        current_report = current_report + f"{feedback_dict[FOOTER]}{NEWLINE}"
        # now that creation of the current_report is finished, store it
        # inside of the dictionary of the markdown_reports and move to the next one
        markdown_reports[key_attribute_value] = current_report
    # return all of the reports that are organized in the dictionary
    return markdown_reports
