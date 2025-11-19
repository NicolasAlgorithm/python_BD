"""CRUD helpers for the usuarios table with basic validations."""

from __future__ import annotations

from typing import Tuple

from DB.connection import get_connection


def create_user(nomusu: str, clave: str, nivel: int) -> Tuple[bool, str]:
    """Create a user only when the identifier is not already present."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM usuarios WHERE nomusu = ?", (nomusu,))
        if cursor.fetchone():
            return False, "El usuario ya existe."

        cursor.execute(
            "INSERT INTO usuarios (nomusu, clave, nivel) VALUES (?, ?, ?)",
            (nomusu, clave, nivel),
        )
        conn.commit()
        return True, "Usuario creado."
    finally:
        conn.close()


def delete_user(nomusu: str) -> Tuple[bool, str]:
    """Remove a user, ensuring it exists beforehand."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM usuarios WHERE nomusu = ?", (nomusu,))
        if not cursor.fetchone():
            return False, "El usuario no existe."

        cursor.execute("DELETE FROM usuarios WHERE nomusu = ?", (nomusu,))
        conn.commit()
        return True, "Usuario eliminado."
    finally:
        conn.close()


def get_users():
    """Retrieve all users stored in the database."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT nomusu, clave, nivel FROM usuarios")
        return cursor.fetchall()
    finally:
        conn.close()
