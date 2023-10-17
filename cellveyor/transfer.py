"""Transfer markdown-based reports to a GitHub destination."""

from typing import Dict

from github import Auth, Github, GithubException
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)

CHECKMARK = "✓"

# the dash that separates a GitHub repository prefix
# from the GitHub username that owns the repository
DASH = "-"

# the forward slash used in the fully qualified
# names of GitHub repositories
FORWARD_SLASH = "/"

# indentation needed for nested message display
INDENT = "  "

# the fixed identifier for the pull request that will
# contain the feedback for the specified repository
PULL_REQUEST_ID = 1

# extra space needed in error message output for problematic transfers
SPACE = " "

XMARK = "✕"

# error message to display when transfer problems occur
ERROR_MESSAGE = ":person_shrugging: Exception occurred when interacting with GitHub"

# message to indicate that the transfer will stop
STOP_MESSAGE = "Stopping report transfer to"

# prefix for the details from the error report
DETAILS = "Error:"


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
    """Transfer all reports to GitHub."""
    # extract the keys for the different repositories on
    # GitHub that will receive a report during this transfer
    github_report_keys = github_reports_dict.keys()
    # create a customized progress bar using rich
    progress_bar = Progress(
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        BarColumn(),
        MofNCompleteColumn(),
        TextColumn("•"),
        TimeElapsedColumn(),
        TextColumn("•"),
        TimeRemainingColumn(),
    )
    # create a progress bar context for the transfer process
    with progress_bar as progress:
        # iterate through the list of completed reports;
        # use the progress bar's track function to dynamically
        # track and update the progress bar display in the terminal
        for github_report_key in progress.track(github_report_keys):
            # the current key is the name of the GitHub user
            github_username = github_report_key
            # extract the contents of the report to upload to the pull request comment
            current_github_report_contents = github_reports_dict[github_username]
            # create the fully qualified name of the GitHub repository
            current_github_repository = create_fully_qualified_github_repository(
                github_organization, github_repository_prefix, github_username
            )
            # transfer this specific report to the pull request in the GitHub repository
            # note that this may fail if the repository does not exist or there is some
            # other problem on the side of the GitHub servers and thus a try block is needed
            try:
                transfer_report_to_github(
                    github_token,
                    current_github_repository,
                    current_github_report_contents,
                )
                # use the
                progress.console.print(
                    f"{CHECKMARK}{SPACE}[green]{current_github_repository}"
                )
            # an exception occurred when attempting to perform the transfer:
            # --> display an error message
            # --> give details about the exception
            # --> skip to the next report and attempt to transfer it
            except GithubException as github_exception:
                progress.console.print(
                    f"{XMARK}{SPACE}[red]{current_github_repository}"
                )
                progress.console.print(
                    f"{INDENT}[red]{DETAILS}[/red]{SPACE}{github_exception}"
                )
                continue


def transfer_report_to_github(github_token: str, repository: str, report: str) -> None:
    """Transfer a report to a pull request in a GitHub repository."""
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
