"""Create reports based on content in dataframes."""

from typing import Any, Dict, List

from pandas import DataFrame

COMMA = ","
DASH = "-"
NEWLINE = "\n"
SPACE = " "

NAN = "nan"

HEADER = "header"
FOOTER = "footer"

FEEDBACK_LABEL = "🤝 Here is some additional feedback for you to consider:"
GREETING_LABEL = "Hello"
SUMMARY_LABEL = "📔 Here are your summary scores:"


def add_feedback_if_exists(
    report: str,
    feedback_dict: Dict[str, Any],
    feedback_key: str,
    make_list: bool = False,
) -> str:
    """Add feedback to the provided report if a specified key exists in the dictionary."""
    # the final report will start off as the contents
    # of the report provided as an argument
    final_report = report
    # the feedback dictionary contains the requested key and
    # thus this function should add the key's value to the report
    if feedback_key in feedback_dict:
        # extract the specific feedback from the dictionary
        feedback = feedback_dict[feedback_key]
        # handle non-string feedback values (e.g., list/dict from YAML) gracefully
        if not isinstance(feedback, str):
            feedback = str(feedback)
        # if the function was not asked to create a list, then
        # add the feedback and then a newline, a space, and then
        # the message; since lists do not need newlines after them,
        # then do not add that to the end of the feedback
        if not make_list:
            final_report = final_report + f"{feedback}{NEWLINE}"
        # if the feedback should appear in a list, then make sure
        # that it is prefaced with a dash and then a space
        else:
            # ensure each list entry ends with a newline
            final_report = final_report + f"{DASH}{SPACE}{feedback}{NEWLINE}"
    # return the potentially improved feedback report
    return final_report


def create_feedback_list(feedback_comma_list: str) -> List[str]:
    """Create a list of feedback keys from a string with the lists separated by commas."""
    # extract all of the feedback that is in a comma separated string so that
    # each of the entries within the comma-separated string are then their
    # own entries inside of a list. Note that this will also extract data
    # values that are "nan" because they were a part of a row that had some
    # values in it mixed with "nan" values; these will be removed next
    feedback_list = [key.strip() for key in feedback_comma_list.split(COMMA)]
    # if there is a "nan" value inside of the list, then go ahead and remove it
    if NAN in feedback_list:
        feedback_list.remove(NAN)
    # return the completed list of feedback that results from converting
    # a string that contains values to a list that contains those values
    return feedback_list


def create_per_key_report(
    key_attribute: str,
    result_dataframe: DataFrame,
    selected_columns: DataFrame,
    feedback_regexp: str,
    feedback_dict: Dict[str, Any],
) -> Dict[str, str]:
    """Create a per-key report for the provided dataframe."""
    # create an empty dictionary for the reports, organized as:
    # --> key: the value for the key attribute (normally a GitHub user name)
    # --> value: an entire report, encoded in markdown for display in the terminal
    # or upload to a markdown-aware platform like a GitHub issue or pull request
    markdown_reports: Dict[str, str] = {}
    # extract the column(s) that provide extra feedback in a comma-separate list
    selected_feedback_columns = selected_columns.filter(regex=feedback_regexp)
    selected_columns = selected_columns.drop(selected_feedback_columns, axis=1)  # type: ignore
    # create a unique message for each row in the dataframe
    for index, row in result_dataframe.iterrows():
        # extract the value of the key attribute
        key_attribute_value = str(row[key_attribute])
        # the key attribute value is "nan" (i.e., it is NaN from a Pandas dataframe), then
        # this function does not need to create a report for it and we can move to the
        # next value for the index and the row. Note that this NaN value might not have
        # already been filtered from the dataframe because of the fact that previously
        # called functions would have only removed a row if it was only made of NaNs
        if key_attribute_value == NAN:
            continue
        # create a main label for the entire markdown-based report
        current_report = f"**{GREETING_LABEL}{SPACE}@{key_attribute_value}!**{NEWLINE}{NEWLINE}"
        current_report = add_feedback_if_exists(
            current_report, feedback_dict, HEADER
        )
        current_report = (
            current_report + f"**{SUMMARY_LABEL}**{NEWLINE}{NEWLINE}"
        )
        # iterate through all of the extracted columns and add them to
        # the report in the following fashion:
        # - Name of the Column: Value of the Column
        # this process should continue to incrementally
        # add data to the current report for every column and its value
        for column_name in selected_columns.columns:
            column_value = row[column_name]
            current_report = (
                current_report
                + f"{DASH}{SPACE}**{column_name}**:{SPACE}{column_value}{NEWLINE}"
            )
        # extract the specific row of feedback from the selected feedback columns
        # handle case where feedback_regexp matches no columns or index out of range
        if (
            selected_feedback_columns.empty
            or selected_feedback_columns.shape[1] == 0
        ):
            feedback_list: List[str] = []
        else:
            try:
                feedback_comma_list = str(
                    selected_feedback_columns.iloc[index, 0]  # type: ignore
                )
            except (IndexError, KeyError):
                feedback_comma_list = ""
            # create a, potentially empty, list of feedback
            feedback_list = create_feedback_list(feedback_comma_list)
        # if there is feedback, then add each of the feedback points
        # in a list and then add the content that belongs in the footer
        # only show feedback section if at least one key exists in the dict
        effective_feedback_keys = [
            k for k in feedback_list if k in feedback_dict
        ]
        if effective_feedback_keys:
            current_report = (
                current_report
                + f"{NEWLINE}{NEWLINE}**{FEEDBACK_LABEL}**{NEWLINE}{NEWLINE}"
            )
            # make an entry for each of the types of feedback, ensuring that
            # each feedback is an entry inside of a list
            for feedback_key in effective_feedback_keys:
                # only add feedback in a list-based fashion when there is
                # a feedback value for the key inside of the feedback dictionary
                current_report = add_feedback_if_exists(
                    current_report, feedback_dict, feedback_key, make_list=True
                )
        # add the footer to the feedback report, making sure to add newlines that
        # will provide adequate separation from the potential feedback list
        footer_content = feedback_dict.get(FOOTER, "")
        # handle case where footer value is not a string (e.g., list from YAML)
        if isinstance(footer_content, list):
            footer_content = str(footer_content)
        if footer_content:
            current_report = (
                current_report + f"{NEWLINE}{NEWLINE}{footer_content}{NEWLINE}"
            )
        # now that creation of the current_report is finished, store it
        # inside of the dictionary of the markdown_reports and move to the next one
        markdown_reports[key_attribute_value] = current_report
    # return all of the reports that are organized in the dictionary
    return markdown_reports
