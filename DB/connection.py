"""Helpers to open SQLite connections used across the project."""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path

DEFAULT_DB_PATH = Path(__file__).with_name("app.db")
ENV_VAR_NAME = "PYTHON_BD_DB_PATH"


def _resolve_db_path() -> str:
    """Return the database path or URI while honoring test overrides."""
    override = os.getenv(ENV_VAR_NAME)
    if override:
        if override == ":memory:":
            return override
        override_path = Path(override)
        if not override_path.is_absolute():
            override_path = DEFAULT_DB_PATH.parent / override_path
        override_path.parent.mkdir(parents=True, exist_ok=True)
        return str(override_path)

    DEFAULT_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return str(DEFAULT_DB_PATH)


def get_connection() -> sqlite3.Connection:
    """
    Purpose: Establish and return a connection to the SQLite database.
    Returns:
        sqlite3.Connection object
    """
    connection = sqlite3.connect(_resolve_db_path())
    connection.execute("PRAGMA foreign_keys = ON;")
    return connection
