"""CRUD helpers for clientes that enforce existence validations."""

from __future__ import annotations

from typing import Tuple

from DB.connection import get_connection


def create_client(
    codclie: str,
    nomclie: str,
    direc: str,
    telef: str,
    ciudad: str,
) -> Tuple[bool, str]:
    """Insert a client while checking for duplicated primary keys."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM clientes WHERE codclie = ?", (codclie,))
        if cursor.fetchone():
            return False, "El cliente ya existe."

        cursor.execute(
            """
            INSERT INTO clientes (codclie, nomclie, direc, telef, ciudad)
            VALUES (?, ?, ?, ?, ?)
            """,
            (codclie, nomclie, direc, telef, ciudad),
        )
        conn.commit()
        return True, "Cliente creado."
    finally:
        conn.close()


def delete_client(codclie: str) -> Tuple[bool, str]:
    """Delete a client only if it exists."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM clientes WHERE codclie = ?", (codclie,))
        if not cursor.fetchone():
            return False, "El cliente no existe."

        cursor.execute("DELETE FROM clientes WHERE codclie = ?", (codclie,))
        conn.commit()
        return True, "Cliente eliminado."
    finally:
        conn.close()
