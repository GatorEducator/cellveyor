<div align="center">
  <img alt="Cellveyor logo" src="https://raw.githubusercontent.com/GatorEducator/cellveyor/master/.github/images/Cellveyor-Logo.png" width="90%">
</div>

# Cellveyor

[![build](https://github.com/GatorEducator/cellveyor/actions/workflows/build.yml/badge.svg)](https://github.com/GatorEducator/cellveyor/actions/workflows/build.yml)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-Yes-blue.svg)](https://github.com/gkapfham/chasten/graphs/commit-activity)

## Overview

Cellveyor turns the cells of a gradebook spreadsheet into one report
per student. Point it at a sheet, pick the grade columns with a regular
expression, and it prints a markdown report for each row. With
`--transfer-report` it posts each report to the student's GitHub
repository instead of just printing it.

Each row is one student. The key attribute column (normally the GitHub
username) decides who a report belongs to. Rows with an empty key get
no report.

## Requirements

- Python `>=3.12, <3.14`
- `uv` (see the [uv documentation](https://docs.astral.sh/uv/))
- A gradebook in XLSX format (for example, an exported Google Sheet)

## Installation

Run the latest release without installing anything:

```bash
uvx cellveyor --help
```

Or install it so `cellveyor` stays on your `PATH`:

```bash
uv tool install cellveyor
```

To work on the code itself, clone the repository and run it with
`uv run`, which uses the local checkout instead of the release:

```bash
git clone git@github.com:GatorEducator/cellveyor.git
cd cellveyor
uv run cellveyor --help
```

## Usage

```bash
cellveyor \
  --spreadsheet-directory spreadsheets \
  --spreadsheet-file fake_spreadsheet.xlsx \
  --sheet-name Main \
  --key-attribute "Student GitHub" \
  --column-regexp "^(Summary Grade|Final Grade) .*$" \
  --feedback-regexp "Summary Grade 1 - Feedback"
```

Use `--key-value` for a single student:

```bash
cellveyor \
  --spreadsheet-directory spreadsheets \
  --spreadsheet-file fake_spreadsheet.xlsx \
  --sheet-name Main \
  --key-attribute "Student GitHub" \
  --column-regexp "^(Summary Grade|Final Grade) .*$" \
  --feedback-regexp "Summary Grade 1 - Feedback" \
  --key-value gkapfham
```

| Flag | Description |
|---|---|
| `--spreadsheet-directory` / `-d` | Directory holding the spreadsheet |
| `--spreadsheet-file` / `-s` | Spreadsheet file in that directory |
| `--sheet-name` / `-n` | Sheet to read |
| `--key-attribute` / `-a` | Column that names the owner of each row |
| `--column-regexp` / `-c` | Regex that picks the grade columns |
| `--feedback-regexp` / `-r` | Regex that picks the feedback columns |
| `--key-value` / `-v` | Only build the report for this key |
| `--feedback-file` / `-f` | YAML feedback file (repeatable) |
| `--github-token-env` / `-g` | Env var holding the GitHub token |
| `--github-organization` / `-o` | GitHub organization for transfers |
| `--github-repository-prefix` / `-p` | Repository prefix for transfers |
| `--transfer-report` / `-t` | Post reports to GitHub |
| `--fancy` / `-y` | Panel display (use `--no-fancy` for plain markdown) |

Exit code `0` means success, including runs that only print warnings
(no columns matched, no rows left, bad feedback file skipped). Exit
code `1` means something blocked the run: bad path, missing sheet or
key column, bad regex, missing GitHub options, or a failed transfer.

## Feedback files

Feedback files are small YAML files. Each key holds one block of
feedback written as a folded scalar. The keys `header` and `footer`
go at the top and bottom of every report; every other key is used
only when a row's feedback column names it:

```yaml
header: >
  Thanks for your work this week.
congratulations: >
  Strong work, keep it up.
needsimprovement: >
  Review the feedback and resubmit.
footer: >
  Come to office hours with questions.
```

A row's feedback column holds a comma-separated list of keys. Each
key found in a feedback file becomes one bullet in that student's
report. Keys that match nothing are skipped. A file may hold any
subset of keys: a shared file might define only the `footer` while
each assignment gets its own file with a `header` and feedback:

```bash
cellveyor ... \
  --feedback-file feedback/shared.yml \
  --feedback-file feedback/assignment-one.yml
```

Pass `--feedback-file` more than once to merge files; later files
win on conflicts.

## GitHub transfer

Transfers need a token, an organization, and a repository prefix. The
token comes from the environment, never from a flag:

```bash
CELLVEYOR_GITHUB_TOKEN="$(gh auth token)" cellveyor \
  --spreadsheet-directory spreadsheets \
  --spreadsheet-file fake_spreadsheet.xlsx \
  --sheet-name Main \
  --key-attribute "Student GitHub" \
  --column-regexp "^(Summary Grade|Final Grade) .*$" \
  --feedback-regexp "Summary Grade 1 - Feedback" \
  --github-organization <your-organization> \
  --github-repository-prefix <your-prefix> \
  --transfer-report
```

`CELLVEYOR_GITHUB_TOKEN` is read first and `GITHUB_TOKEN` works as a
fallback. A `.env` file works too (see `.env.example`, keep it at
`chmod 600`, never commit it). Use `--github-token-env` to name a
different variable. Each report goes to
`<organization>/<prefix>-<key-value>` as a comment on pull request 1,
the pull request GitHub Classroom opens per student repository.

## Example files

| File | Description |
|---|---|
| `spreadsheets/fake_spreadsheet.xlsx` | Small gradebook used in the examples |
| `spreadsheets/example_spreadsheet.xlsx` | Larger gradebook variant |
| `spreadsheets/feedback.yml` | Sample feedback file |

## Development

Clone the repository, then:

```bash
uv run task all
```

That runs the linters, the type checkers, the tests, and the coverage
check. `uv run task lint` runs the linters only and `uv run task test`
runs the tests only.

## License

GNU General Public License v3.0 (see `LICENSE`).
