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
        key_attribute_value = str(row[key_attribute])
        current_report = f"**Hello @{key_attribute_value}! Here are your summary scores:**\n\n"
        for column_name in selected_columns.columns:
            exam_value = row[column_name]
            current_report = current_report + f"- **{column_name}**: {exam_value}\n"
            markdown_reports[key_attribute_value] = current_report
    return markdown_reports
