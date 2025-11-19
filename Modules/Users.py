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
            CREATE TABLE IF NOT EXISTS usuarios (
                nomusu TEXT PRIMARY KEY,
                clave TEXT NOT NULL,
                salt TEXT NOT NULL,
                nivel INTEGER NOT NULL CHECK(nivel IN (1, 2, 3))
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
            cur.execute("SELECT 1 FROM usuarios WHERE nomusu = ?", (username,))
            if cur.fetchone():
                return False, "Usuario ya existe."

            salt = os.urandom(16).hex()
            password_hash = self._hash_password(password, salt)
            cur.execute(
                "INSERT INTO usuarios (nomusu, clave, salt, nivel) VALUES (?, ?, ?, ?)",
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
                "SELECT nomusu, clave, salt, nivel FROM usuarios WHERE nomusu = ?",
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
                "SELECT clave, salt FROM usuarios WHERE nomusu = ?",
                (username,),
            )
            row = cur.fetchone()
            if row is None:
                return False, "Usuario no encontrado."
            stored_hash, salt = row
            salt = salt or ""
            candidate = self._hash_password(password, salt)
            if hmac.compare_digest(candidate, stored_hash):
                return True, "Contraseña verificada."
            if not salt and hmac.compare_digest(password, stored_hash):
                return True, "Contraseña verificada."
            return False, "Contraseña incorrecta."
        finally:
            conn.close()

    def delete_user(self, username: str) -> Tuple[bool, str]:
        conn = self._connection_factory()
        try:
            cur = conn.cursor()
            self._ensure_table(cur)
            cur.execute("SELECT 1 FROM usuarios WHERE nomusu = ?", (username,))
            if not cur.fetchone():
                return False, "Usuario no encontrado."
            cur.execute("DELETE FROM usuarios WHERE nomusu = ?", (username,))
            conn.commit()
            return True, "Usuario eliminado."
        finally:
            conn.close()

    def get_user_level(self, username: str) -> Optional[int]:
        user = self.read_user(username)
        if user is None:
            return None
        return int(user.get("nivel", 1))

    def update_user(self, username: str, password: Optional[str], level: Optional[int]) -> Tuple[bool, str]:
        if level is not None and level not in (1, 2, 3):
            return False, "Nivel de usuario inválido."

        conn = self._connection_factory()
        try:
            cur = conn.cursor()
            self._ensure_table(cur)
            cur.execute("SELECT clave, salt, nivel FROM usuarios WHERE nomusu = ?", (username,))
            row = cur.fetchone()
            if row is None:
                return False, "Usuario no encontrado."
            current_hash, current_salt, current_level = row

            if password:
                salt = os.urandom(16).hex()
                password_hash = self._hash_password(password, salt)
            else:
                salt = current_salt
                password_hash = current_hash

            new_level = int(level) if level is not None else int(current_level)
            cur.execute(
                "UPDATE usuarios SET clave = ?, salt = ?, nivel = ? WHERE nomusu = ?",
                (password_hash, salt, new_level, username),
            )
            conn.commit()
            return True, "Usuario actualizado."
        finally:
            conn.close()

    def list_users(self) -> list[dict]:
        conn = self._connection_factory()
        try:
            cur = conn.cursor()
            self._ensure_table(cur)
            cur.execute("SELECT nomusu, nivel FROM usuarios ORDER BY nomusu")
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
            return [dict(zip(columns, row)) for row in rows]
        finally:
            conn.close()


def create_user(nomusu: str, clave: str, nivel: int) -> Tuple[bool, str]:
    """Compatibility helper to create a user via UsersCRUD."""
    users = UsersCRUD()
    return users.create_user(nomusu, clave, nivel)


def delete_user(nomusu: str) -> Tuple[bool, str]:
    """Compatibility helper to delete a user via UsersCRUD."""
    users = UsersCRUD()
    return users.delete_user(nomusu)
