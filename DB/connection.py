import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "app.db")

def get_connection():
    """
    Purpose: Establish and return a connection to the SQLite database.
    Returns:
        sqlite3.Connection object
    """
    return sqlite3.connect(DB_PATH)
