"""Pytest fixtures for Cellveyor.

This module provides an autouse fixture that wraps and extracts console
output so that Rich-based diagnostics do not appear during test runs.
The output still appears when the program is run normally via
``uv run cellveyor ...``.
"""

import gc
import io
import subprocess
import sys
from typing import Any

import pytest

# disable garbage collector to avoid intermittent segfaults with hypothesis
gc.disable()


@pytest.fixture(autouse=True)
def wrap_console_output(monkeypatch: pytest.MonkeyPatch) -> None:
    """Wrap console output so tests remain quiet.

    This fixture captures all writes to ``sys.stdout`` and ``sys.stderr``
    into an in-memory buffer, preventing Rich ``Console`` output (which
    writes to those streams) from appearing during ``uv run task test-coverage``.
    The program's output is still extracted and can be inspected via
    ``result.output`` when using ``typer.testing.CliRunner``.

    It also quiets ``typer.echo`` and ``subprocess.run`` to avoid
    extraneous output, mirroring best practices from GatorGrade.
    """
    captured_buffer = io.StringIO()

    class QuietStream:
        """A stream that captures output silently."""

        def __init__(self, original: Any, buffer: io.StringIO) -> None:
            self.original = original
            self.buffer = buffer

        def write(self, text: str) -> int:
            self.buffer.write(text)
            return len(text)

        def flush(self) -> None:
            pass

        def isatty(self) -> bool:
            return False

        def __getattr__(self, name: str) -> Any:
            return getattr(self.original, name)

    monkeypatch.setattr(
        sys, "stdout", QuietStream(sys.stdout, captured_buffer)
    )
    monkeypatch.setattr(
        sys, "stderr", QuietStream(sys.stderr, captured_buffer)
    )

    import typer  # noqa: PLC0415

    def quiet_echo(_message: Any = None, **_kwargs: Any) -> None:
        pass

    monkeypatch.setattr(typer, "echo", quiet_echo)

    original_run = subprocess.run

    def quiet_run(*args: Any, **kwargs: Any) -> Any:
        if "stdout" not in kwargs:
            kwargs["stdout"] = subprocess.PIPE
        if "stderr" not in kwargs:
            kwargs["stderr"] = subprocess.PIPE
        return original_run(*args, **kwargs)

    monkeypatch.setattr(subprocess, "run", quiet_run)
