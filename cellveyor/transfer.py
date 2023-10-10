"""Transfer markdown-based reports to a GitHub destination."""

from github import Auth, Github

# the fixed identifier for the pull request that will
# contain the feedback for the specified repository
PULL_REQUEST_ID = 1


def transfer_report_to_github(github_token: str, report: str) -> None:
    """Transfer a report to GitHub."""
    authorization = Auth.Token(github_token)
    github = Github(auth=authorization)
    repository = github.get_repo(
        "Allegheny-Computer-Science-203-F2023/computer-science-203-fall-2023-executable-exam-1-gkapfham"
    )
    pull_request = repository.get_pull(PULL_REQUEST_ID)
    pull_request.create_issue_comment(report)
