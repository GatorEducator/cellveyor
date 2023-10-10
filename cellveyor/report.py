"""Create reports based on content in dataframes."""

from typing import Dict

from pandas import DataFrame


def create_per_key_report(
    key_attribute: str, result_dataframe: DataFrame, selected_columns: DataFrame
) -> Dict[str, str]:
    """Create a per-key report for the provided dataframe."""
    markdown_reports: Dict[str, str] = {}
    # create a unique message for each row in the dataframe
    for _, row in result_dataframe.iterrows():
        student_github = str(row[key_attribute])
        for column_name in selected_columns.columns:
            exam_value = row[column_name]
            current_report = f"{key_attribute}: {student_github}, {column_name}: {exam_value}"
            markdown_reports[student_github] = current_report
    return markdown_reports
