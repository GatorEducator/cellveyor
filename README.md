<img src="https://github.com/GatorEducator/cellveyor/blob/master/.github/images/cellveyor-logo.svg" alt="Cellveyor Logo"
title="Cellveyor Logo" />

# Cellveyor

[![build](https://github.com/GatorEducator/cellveyor/actions/workflows/build.yml/badge.svg)](https://github.com/GatorEducator/cellveyor/actions/workflows/build.yml)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-Yes-blue.svg)](https://github.com/gkapfham/chasten/graphs/commit-activity)
[![License LGPL v3](https://img.shields.io/badge/License-LGPL%20v3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)

## Overview

Cellveyor is a command-line tool that automatically turns the cells of a
spreadsheet into per-student grade reports. You point Cellveyor at a gradebook
spreadsheet, describe which columns hold grades and which hold feedback, and it
creates one markdown report per student. Cellveyor displays directly in the
terminal or, with the `--transfer-report` option, posts it as a comment on the
student's GitHub pull request, often created with GitHub Classroom (i.e., cs50).

Cellveyor is designed for the gradebook spreadsheets used in GitHub
Classroom-based courses. The spreadsheet follows a fixed shape: each row is
one student, each column is one assignment grade or one piece of feedback,
and a "key attribute" column (normally the student's GitHub username)
identifies the owner of each row. Cellveyor reads that sheet, filters it
down to the columns you ask for, and produces a report for every row whose
key is not empty.

No setup beyond a spreadsheet is required when you only want reports in the
terminal. Sending reports to GitHub additionally needs a GitHub token, the
name of the GitHub organization that stores the repositories, and the prefix
shared by those repositories.

## Requirements

- Python `>= 3.11, < 3.14`
- `uv` (see the [uv documentation](https://docs.astral.sh/uv/) for installation)
- A local spreadsheet in XLSX format (e.g., an exported Google Sheet)

## Installation

Clone the repository and run the tool with `uv`:

```bash
git clone git@github.com:GatorEducator/cellveyor.git
cd cellveyor
uv run cellveyor --help
```

The first `uv run` command resolves the dependencies and creates the project
environment; subsequent commands start instantly.

## Usage

Cellveyor exposes a single command, `transport`. It is the default command,
so there is no sub-command to type: all options are given directly after
`cellveyor`.

```bash
uv run cellveyor <options>
```

### `transport` — Generate per-student grade reports

```bash
uv run cellveyor \
  --spreadsheet-directory spreadsheets \
  --spreadsheet-file fake_spreadsheet.xlsx \
  --sheet-name Main \
  --key-attribute "Student GitHub" \
  --column-regexp "^(Summary Grade|Final Grade) .*$" \
  --feedback-regexp "Summary Grade 1 - Feedback"
```

The command reads the requested sheet from the spreadsheet, keeps the key
attribute column plus every column whose name matches `--column-regexp`, and
then creates one markdown report per remaining row. Rows that are completely
empty are dropped by the column filter, and a row whose key attribute is
empty never produces a report. Each report is displayed inside a rich panel,
titled with the student's key value.

**Required options:**

| Flag | Description |
|---|---|
| `--spreadsheet-directory` / `-d` | Directory that contains the spreadsheet file |
| `--spreadsheet-file` / `-s` | Spreadsheet file inside the directory |
| `--sheet-name` / `-n` | Name of the sheet inside the spreadsheet to read |
| `--key-attribute` / `-a` | Column that identifies each row (normally the GitHub username) |
| `--column-regexp` / `-c` | Regular expression that selects the grade columns of the sheet |
| `--feedback-regexp` / `-r` | Regular expression that selects the feedback columns of the sheet |

**Optional options:**

| Flag | Description | Default |
|---|---|---|
| `--key-value` / `-v` | Only produce a report for this value of the key attribute | all rows |
| `--feedback-file` / `-f` | Feedback file(s) in YAML format (repeatable) | none |
| `--github-token` / `-g` | GitHub authorization token for `--transfer-report` | none |
| `--github-organization` / `-o` | GitHub organization that stores the destination repositories | none |
| `--github-repository-prefix` / `-p` | Prefix shared by the destination repositories | none |
| `--transfer-report` | Post each report as a comment on the student's GitHub pull request | off |

**Examples:**

```bash
# Reports for every student row in the Main sheet
uv run cellveyor \
  --spreadsheet-directory spreadsheets \
  --spreadsheet-file fake_spreadsheet.xlsx \
  --sheet-name Main \
  --key-attribute "Student GitHub" \
  --column-regexp "^(Summary Grade|Final Grade) .*$" \
  --feedback-regexp "Summary Grade 1 - Feedback"

# Only the report for one student
uv run cellveyor \
  --spreadsheet-directory spreadsheets \
  --spreadsheet-file fake_spreadsheet.xlsx \
  --sheet-name Main \
  --key-attribute "Student GitHub" \
  --column-regexp "^(Summary Grade|Final Grade) .*$" \
  --feedback-regexp "Summary Grade 1 - Feedback" \
  --key-value gkapfham

# Reports for one sheet, with feedback files added to every report
uv run cellveyor \
  --spreadsheet-directory spreadsheets \
  --spreadsheet-file fake_spreadsheet.xlsx \
  --sheet-name EXE \
  --key-attribute "Student GitHub" \
  --column-regexp "^(Executable Examination|Summary Grade) .*$" \
  --feedback-regexp "Feedback$" \
  --feedback-file spreadsheets/feedback.yml

# Reports posted to each student's GitHub pull request
uv run cellveyor \
  --spreadsheet-directory spreadsheets \
  --spreadsheet-file fake_spreadsheet.xlsx \
  --sheet-name Main \
  --key-attribute "Student GitHub" \
  --column-regexp "^(Summary Grade|Final Grade) .*$" \
  --feedback-regexp "Summary Grade 1 - Feedback" \
  --github-token <your-github-token> \
  --github-organization <your-organization> \
  --github-repository-prefix <your-repository-prefix> \
  --transfer-report
```

**Column filtering.** `--column-regexp` uses `pandas` regex filtering
(`re.search` semantics on the column names), so `^(Summary Grade|Final Grade) .*$` selects every column that starts with "Summary Grade" or
"Final Grade". The key attribute column is always kept regardless of the
regular expression. If the regular expression matches no columns, or the
filter leaves no rows, Cellveyor prints a yellow warning and continues
(exit code `0`). An invalid regular expression stops the command with exit
code `1`.

**Feedback columns.** Columns matched by `--feedback-regexp` are removed
from the summary bullet list and treated as feedback instead. For each row,
the first matching feedback column is read as a comma-separated list of
feedback keys; each key that also exists in a `--feedback-file` becomes one
bullet under "Here is some additional feedback for you to consider". If
none of the comma-separated keys resolve to a feedback file entry, the
feedback section is omitted. See [Feedback files](#feedback-files).

**Errors.** Cellveyor validates its inputs before doing any work, printing a
specific diagnostic and exiting with code `1` when:

- the spreadsheet directory or file does not exist (it prints which one is missing),
- the requested sheet is not in the spreadsheet (it lists the available sheets),
- the key attribute column is not in the sheet (it lists the available columns),
- `--transfer-report` is given without `--github-token`, `--github-organization`, or `--github-repository-prefix` (it lists the missing options),
- reading the spreadsheet or transferring reports to GitHub fails.

Missing or malformed feedback files are skipped with a yellow warning
instead of stopping the command.

## Report format

Every report is markdown that can be displayed in the terminal or rendered
anywhere that markdown is understood, such as a GitHub pull request comment.
A report built from the `Main` sheet looks like this when displayed in the
terminal:

```text
🚚 Accessing: spreadsheets/fake_spreadsheet.xlsx

╭────────────────────────────────── gkapfham ──────────────────────────────────╮
│ Hello @gkapfham!                                                             │
│                                                                              │
│ 📔 Here are your summary scores:                                             │
│                                                                              │
│  • Summary Grade for Team Participation: 0.49                                │
│  • Summary Grade for In-Person Assessment: 0.3916666667                      │
│  • Summary Grade for Executable Midterms: 0.88                               │
│  • Summary Grade for Executable Final: 1.0                                   │
│  • Summary Grade for Professional Development: 0.6688888889                  │
│  • Summary Grade for Technical Development: 0.4111111111                     │
│  • Summary Grade for Project Development: 0.82                               │
│  • Final Grade - Percentage: 0.7220833333                                    │
│  • Final Grade - Letter: C-                                                  │
│                                                                              │
│ [{'type': 'markdown', 'attributes': None, 'value': 'This is a footer'}]      │
╰──────────────────────────────────────────────────────────────────────────────╯
```

The same report as plain markdown (this is the text that is posted to
GitHub when `--transfer-report` is enabled):

```markdown
**Hello @gkapfham!**

**📔 Here are your summary scores:**

- **Summary Grade for Team Participation**: 0.49
- **Summary Grade for In-Person Assessment**: 0.3916666667
- **Summary Grade for Executable Midterms**: 0.88
- **Summary Grade for Executable Final**: 1.0
- **Summary Grade for Professional Development**: 0.6688888889
- **Summary Grade for Technical Development**: 0.4111111111
- **Summary Grade for Project Development**: 0.82
- **Final Grade - Percentage**: 0.7220833333
- **Final Grade - Letter**: C-

[{'type': 'markdown', 'attributes': None, 'value': 'This is a footer'}]
```

The structure of each report is fixed:

1. **Greeting** — `**Hello @<key-value>!**`, where the key value is the
   student's value in the key attribute column (normally the GitHub
   username).
1. **Header** — the value of the `header` key in the feedback files, when
   present.
1. **Summary scores** — one bullet per selected grade column, rendered as
   `- **<column name>**: <value>` in the sheet's column order.
1. **Additional feedback** — one bullet per resolved feedback key, only when
   at least one key in the row's feedback column exists in the feedback
   files.
1. **Footer** — the value of the `footer` key in the feedback files, when
   present.

The header and footer are expected to be strings. Non-string values (like the
list of markup objects in `spreadsheets/feedback.yml`) are converted to their
string representation, which is why that footer appears as
`[{'type': 'markdown', 'attributes': None, 'value': 'This is a footer'}]` in
the sample output.

## Feedback files

Feedback files are YAML dictionaries that supply the header, the footer, and
the text behind each feedback key. (The `--help` text still says "JSON", but
the files are parsed as YAML.) A feedback file with all three kinds of
content looks like this:

```yaml
header: "This is a header"
footer: "This is a footer"
congratulations: "Fantastic work on this assignment!"
needsimprovement: "Please review the feedback and then try again."
buildfailure: "Your repository does not currently build correctly."
```

The keys `header` and `footer` have fixed meanings and are placed at the
top and bottom of every report. Every other key is a feedback key: it is
used when a row's feedback column contains that key in its comma-separated
list. For example, a feedback column cell containing
`congratulations, needsimprovement` adds both of those bullets to that
student's report. Keys that appear in the spreadsheet but not in any
feedback file are silently ignored.

Pass multiple files with repeated options; the dictionaries are merged in
order, so a later file overrides an earlier file on key conflicts:

```bash
uv run cellveyor ... \
  --feedback-file feedback/all.yml \
  --feedback-file feedback/project-development.yml
```

This is useful when the same spreadsheet powers different kinds of reports
and different feedback files are relevant for different sheets.

## GitHub transfer

With `--transfer-report`, Cellveyor posts each generated report to GitHub
instead of only displaying it. The destination repository for a student is
derived from the key value using the GitHub Classroom naming convention:

```text
<organization>/<repository-prefix>-<key-value>
```

For example, a student with GitHub username `gkapfham` in the organization
`Allegheny-Computer-Science-203-F2023` with the prefix
`computer-science-203-fall-2023-course-assessment` receives the report in:

```text
Allegheny-Computer-Science-203-F2023/computer-science-203-fall-2023-course-assessment-gkapfham
```

Each report is posted as an issue comment on pull request number 1 of that
repository — the pull request that GitHub Classroom opens for every student
repository. The transfer runs with a progress bar that shows the elapsed and
remaining time; a green checkmark marks a successful transfer and a red
cross marks a failed one. Failures (for example, a repository that does not
exist) print the error details and are skipped, and the transfer continues
with the remaining reports.

To transfer reports you must supply all three GitHub options. Reports are
generated first and displayed before any transfer begins, so you can verify
the reports in the terminal before the command starts uploading them.

## Exit codes

| Code | Meaning |
|---|---|
| `0` | Success, including runs that only emitted warnings (e.g., no columns matched, no rows found, malformed feedback files skipped) |
| `1` | A blocking error: invalid directory/file, sheet or key attribute not found, invalid regular expression, missing GitHub options with `--transfer-report`, spreadsheet read failure, or GitHub transfer failure |

## Example spreadsheet

The `spreadsheets/` directory contains a small example gradebook that all of
the examples above use:

| File | Description |
|---|---|
| `fake_spreadsheet.xlsx` | A gradebook with multiple sheets (`Main`, `TP`, `IPA`, `EXE`, `PFD`, `TCD`, `PRD`, `WEB`, `Tokens`, `Feedback`, `Lookup`) |
| `feedback.yml` | A feedback file that only supplies a `footer` |

The `Main` sheet holds summary grades and final grades per student, `EXE`
holds per-exam grades, and so on. The `Feedback` sheet and the `Lookup` sheet
(letter-to-GPA) exist in the same workbook because that is how the original
Google Sheet was structured; Cellveyor only reads the sheet named by
`--sheet-name`.

## License

GNU General Public License v3.0 (see the `LICENSE` file in this repository).
