"""CRUD simple para usuarios con encriptación de contraseñas usando hashlib.sha256."""

from __future__ import annotations

import hashlib
import hmac
import os
from typing import Callable, Optional

from DB.connection import get_connection


class UsersCRUD:
    """Operaciones CRUD básicas para usuarios con hashing de contraseñas."""

    def __init__(self, connection_factory: Callable = get_connection) -> None:
        self._connection_factory = connection_factory

    def _ensure_table(self, cursor) -> None:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL
            )
            """
        )

    def _hash_password(self, password: str, salt: str) -> str:
        """Hash de contraseña usando SHA256 sobre salt + password."""
        return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()

    def create_user(self, username: str, password: str) -> tuple[bool, str]:
        """Crear usuario guardando salt y hash. Mensajes en español para tests."""
        if not username or not password:
            return False, "Nombre de usuario y contraseña requeridos."
        conn = self._connection_factory()
        try:
            cur = conn.cursor()
            self._ensure_table(cur)
            cur.execute("SELECT 1 FROM users WHERE username = ?", (username,))
            if cur.fetchone():
                return False, "Usuario ya existe."
            salt = os.urandom(16).hex()
            pw_hash = self._hash_password(password, salt)
            cur.execute(
                "INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)",
                (username, pw_hash, salt),
            )
            conn.commit()
            return True, "Usuario creado."
        finally:
            conn.close()

    def read_user(self, username: str) -> Optional[dict]:
        """Leer usuario (incluye hash y salt)."""
        conn = self._connection_factory()
        try:
            cur = conn.cursor()
            self._ensure_table(cur)
            cur.execute(
                "SELECT username, password_hash, salt FROM users WHERE username = ?",
                (username,),
            )
            row = cur.fetchone()
            if row is None:
                return None
            cols = [d[0] for d in cur.description]
            return dict(zip(cols, row))
        finally:
            conn.close()

    def verify_user(self, username: str, password: str) -> tuple[bool, str]:
        """Verificar contraseña: devuelve (True, msg) o (False, msg)."""
        conn = self._connection_factory()
        try:
            cur = conn.cursor()
            self._ensure_table(cur)
            cur.execute(
                "SELECT password_hash, salt FROM users WHERE username = ?", (username,)
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
