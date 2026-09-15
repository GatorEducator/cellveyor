"""Single source of truth for the cellveyor version number.

This module exists so that both cellveyor.main and other modules can import
the version without creating a circular dependency. The value must always
match the version in pyproject.toml.
"""

CELLVEYOR_VERSION = "0.1.0"
