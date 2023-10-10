"""Create reports based on content in dataframes."""

from typing import Dict

from pandas import DataFrame

NEWLINE = "\n"


def create_per_key_report(
    key_attribute: str, result_dataframe: DataFrame, selected_columns: DataFrame
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
        current_report = f"**Hello @{key_attribute_value}! Here are your summary scores:**{NEWLINE}{NEWLINE}"
        # iterate through all of the extracted columns and add them to
        # the report in the following fashion:
        # - Name of the Column: Value of the Column
        # this process should continue to incrementally
        # add data to the current report for every column and its value
        for column_name in selected_columns.columns:
            column_value = row[column_name]
            current_report = current_report + f"- **{column_name}**: {column_value}{NEWLINE}"
        # now that creation of the current_report is finished, store it
        # inside of the dictionary of the markdown_reports and move to the next one
        markdown_reports[key_attribute_value] = current_report
    # return all of the reports that are organized in the dictionary
    return markdown_reports
