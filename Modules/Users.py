"""CRUD helpers for users with hashed passwords and access level checks."""

from __future__ import annotations

import hashlib
import hmac
import os
from typing import Callable, Optional, Tuple

from DB.connection import get_connection


class UsersCRUD:
    """Provide CRUD operations for application users backed by the users table."""

    def __init__(self, connection_factory: Callable = get_connection) -> None:
        self._connection_factory = connection_factory

    def _ensure_table(self, cursor) -> None:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                level INTEGER NOT NULL CHECK(level IN (1, 2, 3))
            )
            """
        )

    def _hash_password(self, password: str, salt: str) -> str:
        return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()

    def create_user(self, username: str, password: str, level: int = 1) -> Tuple[bool, str]:
        if not username or not password:
            return False, "Nombre de usuario y contraseña requeridos."
        if level not in (1, 2, 3):
            return False, "Nivel de usuario inválido."

        conn = self._connection_factory()
        try:
            cur = conn.cursor()
            self._ensure_table(cur)
            cur.execute("SELECT 1 FROM users WHERE username = ?", (username,))
            if cur.fetchone():
                return False, "Usuario ya existe."

            salt = os.urandom(16).hex()
            password_hash = self._hash_password(password, salt)
            cur.execute(
                "INSERT INTO users (username, password_hash, salt, level) VALUES (?, ?, ?, ?)",
                (username, password_hash, salt, level),
            )
            conn.commit()
            return True, "Usuario creado."
        finally:
            conn.close()

    def read_user(self, username: str) -> Optional[dict]:
        conn = self._connection_factory()
        try:
            cur = conn.cursor()
            self._ensure_table(cur)
            cur.execute(
                "SELECT username, password_hash, salt, level FROM users WHERE username = ?",
                (username,),
            )
            row = cur.fetchone()
            if row is None:
                return None
            columns = [desc[0] for desc in cur.description]
            return dict(zip(columns, row))
        finally:
            conn.close()

    def verify_user(self, username: str, password: str) -> Tuple[bool, str]:
        conn = self._connection_factory()
        try:
            cur = conn.cursor()
            self._ensure_table(cur)
            cur.execute(
                "SELECT password_hash, salt FROM users WHERE username = ?",
                (username,),
            )
            row = cur.fetchone()
            if row is None:
                return False, "Usuario no encontrado."
            stored_hash, salt = row
            candidate = self._hash_password(password, salt)
            if hmac.compare_digest(candidate, stored_hash):
                return True, "Contraseña verificada."
            return False, "Contraseña incorrecta."
        finally:
            conn.close()

    def delete_user(self, username: str) -> Tuple[bool, str]:
        conn = self._connection_factory()
        try:
            cur = conn.cursor()
            self._ensure_table(cur)
            cur.execute("SELECT 1 FROM users WHERE username = ?", (username,))
            if not cur.fetchone():
                return False, "Usuario no encontrado."
            cur.execute("DELETE FROM users WHERE username = ?", (username,))
            conn.commit()
            return True, "Usuario eliminado."
        finally:
            conn.close()

    def get_user_level(self, username: str) -> Optional[int]:
        user = self.read_user(username)
        if user is None:
            return None
        return int(user.get("level", 1))


def create_user(nomusu: str, clave: str, nivel: int) -> Tuple[bool, str]:
    """Compatibility helper to create a user via UsersCRUD."""
    users = UsersCRUD()
    return users.create_user(nomusu, clave, nivel)


def delete_user(nomusu: str) -> Tuple[bool, str]:
    """Compatibility helper to delete a user via UsersCRUD."""
    users = UsersCRUD()
    return users.delete_user(nomusu)
