# AGENTS.md

This document provides guidelines for AI agents contributing to the
**Cellveyor** repository.

## Overview of Instructions

- **Always use `uv`:** This project uses `uv` for all dependency management,
  virtual environments, and task running. Do not use `pip`, `venv`, or
  `poetry` directly. Commands like `uv sync`, `uv run`, and `uv add` are the
  only correct workflow.
- **Follow all guidelines:** This document contains the complete set of
  guidelines for this project. You must follow them strictly. For build
  architecture and implementation details, consult `README.md`, `pyproject.toml`,
  and `WORKFLOW.md` at the repository root.
- **Verify your changes:** Before declaring any task complete, you must run all
  linters and tests to ensure correctness and style compliance. The canonical
  verification command is `uv run task all`.
- **Line width:** Python source code must respect **79 characters** (enforced
  by `ruff`). Markdown and other prose files should wrap at **80 characters**.
- **Permission to run commands:** You have permission to run all commands in
  this file to verify their functionality.
- **Incremental changes:** Make small, incremental changes. This makes review
  easier and catches errors early.
- **Communicate clearly:** When you propose changes, explain what you have
  done and why.
- **Be transparent about mistakes:** Although you should
  avoid making mistakes, when an action overwrites, deletes,
  or damages user data (for example, replacing a database file
  during testing), report it immediately and explicitly: name
  the file, what happened, why, and what is recoverable. Never
  hide damage or wait for the human to discover it.
  Acknowledge the error and offer remediation.
- **Create and follow a TODO list:** Always create a TODO list and then follow
  it. Do not stop until the tools you call confirm that all tasks in the list
  are completed.
- **Do not close the TODO:** Only the user closes the TODO. The agent must
  never mark a TODO as closed or call update_goal with status complete. The
  agent reports completion and waits for the user to confirm and close.

## Notification Instructions

- The user has given permission to use `notify-send` to signal task completion
  or request feedback. Example:

  ```bash
  notify-send "Question from Coding Agent" \
    "Please clarify how to complete the testing task."
  ```

- Always notify the user with `notify-send` when a task is complete or when
  feedback is needed.

- When working inside a Zellij session, use the `zjstatus::notify` pipe
  protocol. The full two-step pattern is:

  ```bash
  # Step 1: Send the notification (displays for show_interval seconds)
  timeout 2 zellij pipe -- \
    "zjstatus::notify::󰵰 Task complete. " 2>/dev/null

  # Step 2: After the interval expires, force a re-render to clear it
  timeout 8 bash -c \
    "sleep 6 && zellij pipe -- 'zjstatus::pipe::clear:: '" 2>/dev/null || true
  ```

  The `sleep` duration must be at least `show_interval + 1` seconds.
  The trailing space in the notify message is required.

## Build, Lint, and Test Commands

These commands are defined via **taskipy** in `pyproject.toml` and executed
through `uv run task <name>`:

- **Run all verification:** `uv run task all` (= `task check && task test && task test-coverage-check`)
- **Run all linters + typecheck:** `uv run task check` (= `task lint && task typecheck`)
- **Lint suite:** `uv run task lint` (= `ruff-format && ruff-check && comments-check && vsc && rumdl-check`)
- **Typecheck suite:** `uv run task typecheck` (= `mypy && ty && pyrefly && zuban && symbex`)
- **Format check:** `uv run task ruff-format` (check only)
- **Format fix:** `uv run task ruff-format-fix` / `uv run task format-fix`
- **Lint check:** `uv run task ruff-check`
- **Individual type checkers:** `uv run task mypy`, `uv run task ty`, `uv run task pyrefly`, `uv run task zuban`, `uv run task symbex`, `uv run task symbex-typed`, `uv run task symbex-documented`
- **Comment check/fix:** `uv run task comments-check` / `uv run task comments-fix` (via `scripts/ccl.py`)
- **Version sync check:** `uv run task vsc` (verifies `cellveyor/version.py` matches `pyproject.toml`)
- **Markdown lint/fix:** `uv run task rumdl-check` / `uv run task rumdl-fix`
- **Test suite:** `uv run task test` (`pytest -x -s -vv -n auto` with randomly + xdist)
- **Test variants:** `uv run task test-not-randomly`, `uv run task test-not-xdist`, `uv run task test-silent`, `uv run task test-parallel`
- **Test with coverage:** `uv run task test-coverage` (enforces `fail_under = 98` in `pyproject.toml`)
- **Direct coverage check:** `uv run task test-coverage-check` (enforces `directtestedfailunder = 75` via `scripts/tsc.py`)
- **Run a single test:**
  `uv run pytest tests/test_file.py::test_function -x -s -vv`

## Code Requirements

All Python code must follow these standards:

- **Cross-platform code:** Source code must run unchanged on macOS,
  Linux, and Windows. Write filesystem logic with `pathlib` and never
  embed path separators in strings; a leading-slash path without a
  drive letter is not absolute on Windows. Normalize any path that
  appears in a stable identifier or output with `Path.as_posix()` so
  results are identical on every platform.
- **Function bodies:** No blank lines within function bodies. Keep code
  contiguous from the function signature to the final `return`.
- **Docstrings:** Single-line docstrings starting with a capital letter and
  ending with a period. Follow this for new files. In existing files, preserve
  the established docstring style.
- **Comments:** Start with a lowercase letter. Preserve existing comments
  during refactoring. The only exception is when the first word is a proper
  noun (e.g., `Cellveyor`, `GitHub`) or an identifier that must be
  capitalized (e.g., `GITHUB_ENV`).
- **Sentences in comments:** Use exactly one space between the period and the
  following sentence.
- **No backticks in comments:** Do not use backticks in comments, docstrings,
  or any prose inside source files. Backticks are reserved for Markdown
  formatting in `.md` files only. Refer to identifiers plainly
  (e.g., "pandas" not "`pandas`").
- **Imports:** Group in this order: standard library, third-party, local.
  Use absolute imports (`from cellveyor.module import <name>`). Place all
  imports at the top of the file. Never place imports inside functions or
  classes.
- **Formatting:** `ruff format` enforces line length 79. Use trailing commas.
  Run via `uv run task ruff-format-fix`.
- **Types:** All functions must have type hints for parameters and return
  values.
- **Naming:** `snake_case` for functions and variables, `PascalCase` for
  classes, `UPPER_SNAKE_CASE` for constants.
- **Constants over literals:** All hard-coded strings, integers, and floats
  must be extracted into named constants at the top of the module. Use the
  constant everywhere, never the raw literal.
- **File operations:** Use `pathlib.Path` for all filesystem operations. Never
  use string paths.
- **Error handling:** Raise specific exception types, not generic `Exception`.
  Provide meaningful error messages.

## Project Structure Requirements

- Source code lives in `cellveyor/` (`constants.py`, `data.py`, `filesystem.py`, `main.py`, `report.py`, `transfer.py`, `version.py`).
- Tests live in `tests/` with structure mirroring the source modules (`test_data.py`, `test_report.py`, etc.).
- Helper scripts live in `scripts/` (`ccl.py`, `tsc.py`, `vsc.py`).
- Example gradebooks live in `spreadsheets/` (`fake_spreadsheet.xlsx`, `feedback.yml`).
- Use `uv` for dependency management, virtual environments, and task running.
- Supports Python `>=3.12, <3.14` on macOS, Linux, and Windows (see `pyproject.toml` `requires-python` and `README.md`).
- CLI is built with `typer` (`cellveyor/main.py:cli`) and terminal output with `rich`; spreadsheet I/O uses `pandas` + `openpyxl`; GitHub transfer uses `PyGithub`; feedback files are `yaml`.

## Testing Requirements

All tests must follow these standards:

- **Cross-platform tests:** Tests must pass unchanged on macOS, Linux,
  and Windows. Never assert hardcoded POSIX-style paths; derive the
  expected string from the same `Path` object under test (for example,
  `str(spreadsheet_path)` instead of a `/custom/...` literal) and remember that
  leading-slash paths without a drive letter are not absolute on
  Windows. Use platform-neutral fixtures such as `tmp_path`.
- Tests are Python functions and therefore follow all code requirements above.
- Test names start with `test_` and are descriptive.
- Group tests by the function or module they exercise.
- Order tests logically for readability.
- Tests must be independent — runnable in random order without side effects.
- Tests must pass on local machines and in CI on macOS, Linux, and Windows.
- Aim for full function, statement, and branch coverage (global `fail_under = 98`, direct coverage `>= 75%` via `scripts/tsc.py`).
- Property-based tests using `hypothesis` must be marked with
  `@pytest.mark.propertybased` or `@pytest.mark.fuzz`.
- Tests must not produce console output.

## CLI Output Testing and Rich Encoding Traps to Avoid

Cellveyor renders reports with `rich` (`Console`, `Panel`, `Markdown`) and is invoked via `typer.testing.CliRunner`. A recurring flake is `task test` failing while `task test-parallel` passes (or the converse) on a `CliRunner` assertion:

- `rich.console.Console()` defaults to `stderr` and, when `isatty()` is true,
  emits ANSI escape codes and may use a different encoding. Under
  `pytest -n auto` (`task test`) each `xdist` worker is not a TTY (plain `utf-8` to `stdout`); under single-process `task test-not-xdist` it may be a TTY (ANSI to `stderr`). `CliRunner` captures `stdout`/`stderr` separately, so `assert "gkapfham" in result.stdout` can be empty or ANSI-wrapped while `result.output` holds the text.

Required process for every agent working in Python on this repo:

- In tests using `typer.testing.CliRunner`, strip ANSI before asserting (see `tests/test_main.py:_strip_ansi`) and assert against `result.output` or the stripped output with a substring check (`assert "gkapfham" in _strip_ansi(result.output)`) rather than an exact `result.stdout == "..."` check. Never assert a hard-coded ANSI string.
- If `rich` must be used in production code, prefer `Console()` defaults as `main.py` does, but keep tests ANSI-tolerant. If you need deterministic output in a test, construct `Console(file=sys.stdout, force_terminal=False, highlight=False)` explicitly.
- Always pass `encoding="utf-8"` to `Path.read_text`/`write_text` and to `open(..., encoding="utf-8", newline="")` for YAML/CSV so the suite behaves identically on Linux, macOS, and Windows.
- Verify both variants before completing:
  `uv run task test` and `uv run task test-not-xdist`. The canonical gate is `uv run task all`, but both must be green.
- When a fix touches CLI output, run `uv run task test-coverage` as well; a coverage drop from an untested `rich` branch is a signal, not just a lint failure.

## Making Changes

1. **Understand:** Thoroughly understand the request and the relevant
   codebase. Use available tools to explore files.
1. **Plan:** Formulate a clear plan before making changes. Consult `README.md` and `WORKFLOW.md` for architecture decisions.
1. **Implement:** Make small, incremental changes.
1. **Verify:** Run `uv run task all` to ensure correctness and style
   compliance.
1. **Commit:** The human developer commits the changes.
1. **Rules:** Follow all rules in this file, `README.md`, and `WORKFLOW.md`.
1. **Report, don't close the TODO:** When finished, summarize completed
   tasks, how you completed them, challenges faced, how you overcame them,
   and the rules you followed. Leave the TODO open — only the user closes it.
1. **Wait for confirmation:** After reporting completion, wait for the user to
   confirm before starting the next TODO.
