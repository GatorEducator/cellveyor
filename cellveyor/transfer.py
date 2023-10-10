"""Transfer markdown-based reports to a GitHub destination."""

from typing import Dict

from github import Auth, Github

# the fixed identifier for the pull request that will
# contain the feedback for the specified repository
PULL_REQUEST_ID = 1
FORWARD_SLASH = "/"
DASH = "-"


def create_fully_qualified_github_repository(
    github_organization: str, github_repository_prefix: str, github_username: str
) -> str:
    """Create a fully qualified GitHub repository name using provided naming parts."""
    # create fully qualified name of a GitHub repository:
    # --> Add the organization and the prefix of the repository
    fully_qualified_github_repo_name = (
        f"{github_organization}{FORWARD_SLASH}{github_repository_prefix}"
    )
    # --> Add the dash separator and then the GitHub username
    fully_qualified_github_repo_name = (
        f"{fully_qualified_github_repo_name}{DASH}{github_username}"
    )
    # Example of a fully qualified name, using the GitHub Classroom format:
    # Allegheny-Computer-Science-203-F2023/computer-science-203-fall-2023-executable-exam-1-gkapfham
    return fully_qualified_github_repo_name


def transfer_reports_to_github(
    github_token: str,
    github_organization: str,
    github_repository_prefix: str,
    github_reports_dict: Dict[str, str],
) -> None:
    """Transfer a report to GitHub."""
    # iterate through the list of completed reports
    for github_report_key in github_reports_dict.keys():
        # the current key is the name of the GitHub user
        github_username = github_report_key
        # extract the contents of the report to upload to the pull request comment
        current_github_report_contents = github_reports_dict[github_username]
        # create the fully qualified name of the GitHub repository
        current_github_repository = create_fully_qualified_github_repository(
            github_organization, github_repository_prefix, github_username
        )
        # transfer this specific report to the pull request in the GitHub repository
        transfer_report_to_github(
            github_token, current_github_repository, current_github_report_contents
        )


def transfer_report_to_github(github_token: str, repository: str, report: str) -> None:
    """Transfer a report to GitHub."""
    # authorize the conveyor app to access GitHub through
    # the use of the provided personal access token
    authorization = Auth.Token(github_token)
    github = Github(auth=authorization)
    # use the fully qualified name of the GitHub repository to
    # create a connection to it
    github_repository = github.get_repo(repository)
    # access the default pull request according to the
    # convention established by GitHub Classroom
    pull_request = github_repository.get_pull(PULL_REQUEST_ID)
    # create an issue comment in this specific pull request;
    # note that this is a stand-alone comment for a pull request
    # and not specifically connected to the review of the pull
    # request itself; this is the reason why it is actually
    # using the issue GitHub API to create the comment
    pull_request.create_issue_comment(report)
