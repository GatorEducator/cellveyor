"""Create reports based on content in dataframes."""

from typing import Dict, List

from pandas import DataFrame

COMMA = ","
NEWLINE = "\n"

HEADER = "header"
FOOTER = "footer"

SUMMARY_LABEL = "Here are your summary scores:"
FEEDBACK_LABEL = "Here is some additional feedback to consider:"


def add_feedback_if_exists(
    report: str, feedback_dict: Dict[str, str], feedback_key: str, make_list: bool = False
) -> str:
    """Add feedback to the provided report if a specified key exists in the dictionary."""
    # the final report will start off as the contents
    # of the report provided as an argument
    final_report = report
    # the feedback dictionary contains the requested key and
    # thus this function should add the key's value to the report
    if feedback_key in feedback_dict:
        feedback = feedback_dict[feedback_key]
        if not make_list:
            final_report = final_report + f"{feedback}{NEWLINE}"
        else:
            final_report = final_report + f"- {feedback}"
    # return the potentially improved feedback report
    return final_report


def create_feedback_list(feedback_comma_list: str) -> List[str]:
    """Create a list of feedback keys from a string with the lists separated by commas."""
    feedback_list = [key.strip() for key in feedback_comma_list.split(COMMA)]
    if "nan" in feedback_list:
        feedback_list.remove("nan")
    return feedback_list


def create_per_key_report(
    key_attribute: str,
    result_dataframe: DataFrame,
    selected_columns: DataFrame,
    feedback_regexp: str,
    feedback_dict: Dict[str, str],
) -> Dict[str, str]:
    """Create a per-key report for the provided dataframe."""
    # create an empty dictionary for the reports, organized as:
    # --> key: the value for the key attribute (normally a GitHub user name)
    # --> value: an entire report, encoded in markdown for display in the terminal
    # or upload to a markdown-aware platform like a GitHub issue or pull request
    markdown_reports: Dict[str, str] = {}
    # extract the column(s) that provide extra feedback in a comma-separate list
    # selected_feedback_columns = selected_columns.filter(regex=feedback_regexp).dropna()
    selected_feedback_columns = selected_columns.filter(regex=feedback_regexp)
    selected_columns = selected_columns.drop(selected_feedback_columns, axis=1)  # type: ignore
    # create a unique message for each row in the dataframe
    for index, row in result_dataframe.iterrows():
        # extract the value of the key attribute
        key_attribute_value = str(row[key_attribute])
        # create a main label for the entire markdown-based report
        current_report = f"**Hello @{key_attribute_value}!**{NEWLINE}{NEWLINE}"
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
        # extract the specific row of feedback from the selected feedback columns
        feedback_comma_list = str(selected_feedback_columns.iloc[index, 0])
        feedback_list = create_feedback_list(feedback_comma_list)
        if feedback_list:
            current_report = (
                current_report
                + f"{NEWLINE}{NEWLINE}**{FEEDBACK_LABEL}**{NEWLINE}{NEWLINE}"
            )
            for feedback_key in feedback_list:
                current_report = add_feedback_if_exists(
                    current_report, feedback_dict, feedback_key, True
                )
                # current_report = current_report + f"- {current_feedback_value}{NEWLINE}{NEWLINE}"
        current_report = current_report + f"{NEWLINE}{NEWLINE}{feedback_dict[FOOTER]}{NEWLINE}"
        # now that creation of the current_report is finished, store it
        # inside of the dictionary of the markdown_reports and move to the next one
        markdown_reports[key_attribute_value] = current_report
    # return all of the reports that are organized in the dictionary
    return markdown_reports
