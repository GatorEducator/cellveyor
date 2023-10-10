"""Transfer markdown-based reports to a GitHub destination."""

from typing import Dict

from github import Auth
from github import Github

# the fixed identifier for the pull request that will
# contain the feedback for the specified repository
PULL_REQUEST_ID = 1
FORWARD_SLASH = "/"
DASH = "-"


def create_fully_qualified_github_repository(
    github_organization: str, github_repository_prefix: str, github_username: str
) -> str:
    """Create a fully qualified GitHub repository name using provied parts."""
    fully_qualified_github_repo_name = (
        f"{github_organization}{FORWARD_SLASH}{github_repository_prefix}"
    )
    fully_qualified_github_repo_name = (
        f"{fully_qualified_github_repo_name}{DASH}{github_username}"
    )
    return fully_qualified_github_repo_name


def transfer_reports_to_github(
    github_token: str,
    github_organization: str,
    github_repository_prefix: str,
    github_reports_dict: Dict[str, str],
) -> None:
    """Transfer a report to GitHub."""
    for github_report_key in github_reports_dict.keys():
        github_username = github_report_key
        current_github_report_contents = github_reports_dict[github_username]
        current_github_repository = create_fully_qualified_github_repository(
            github_organization, github_repository_prefix, github_username
        )
        transfer_report_to_github(
            github_token, current_github_repository, current_github_report_contents
        )


def transfer_report_to_github(github_token: str, repository: str, report: str) -> None:
    """Transfer a report to GitHub."""
    # authorize the conveyor app to access GitHub through
    # the use of the provided personal access token
    authorization = Auth.Token(github_token)
    github = Github(auth=authorization)
    github_repository = github.get_repo(repository)
    pull_request = github_repository.get_pull(PULL_REQUEST_ID)
    pull_request.create_issue_comment(report)
