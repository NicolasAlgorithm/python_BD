"""CRUD helpers for clientes that enforce existence validations."""

from __future__ import annotations

from typing import List, Optional, Tuple

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


def get_client(codclie: str) -> Optional[dict]:
    """Fetch a single client as a dictionary."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT codclie, nomclie, direc, telef, ciudad FROM clientes WHERE codclie = ?",
            (codclie,),
        )
        row = cursor.fetchone()
        if row is None:
            return None
        columns = [desc[0] for desc in cursor.description]
        return dict(zip(columns, row))
    finally:
        conn.close()


def update_client(
    codclie: str,
    nomclie: str,
    direc: str,
    telef: str,
    ciudad: str,
) -> Tuple[bool, str]:
    """Update an existing client record."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM clientes WHERE codclie = ?", (codclie,))
        if not cursor.fetchone():
            return False, "El cliente no existe."

        cursor.execute(
            """
            UPDATE clientes
            SET nomclie = ?, direc = ?, telef = ?, ciudad = ?
            WHERE codclie = ?
            """,
            (nomclie, direc, telef, ciudad, codclie),
        )
        conn.commit()
        return True, "Cliente actualizado."
    finally:
        conn.close()


def list_clients() -> List[dict]:
    """Return all clients ordered by identifier."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT codclie, nomclie, direc, telef, ciudad FROM clientes ORDER BY codclie"
        )
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in rows]
    finally:
        conn.close()
