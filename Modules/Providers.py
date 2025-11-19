"""CRUD helpers for proveedores linked to productos."""

from __future__ import annotations

from typing import Callable, List, Optional

from DB.connection import get_connection


class ProvidersCRUD:
    """Administra operaciones CRUD de la tabla proveedores."""

    def __init__(self, connection_factory: Callable = get_connection) -> None:
        self._connection_factory = connection_factory

    def create_provider(
        self,
        idprov: str,
        codprod: str,
        descripcion: str,
        costo: float,
        direccion: str,
        telefono: str,
    ) -> tuple[bool, str]:
        """Create a provider ensuring both uniqueness and FK integrity."""
        conn = self._connection_factory()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM proveedores WHERE idprov = ?", (idprov,))
            if cursor.fetchone():
                return False, "El proveedor ya existe."

            cursor.execute("SELECT 1 FROM productos WHERE codprod = ?", (codprod,))
            if not cursor.fetchone():
                return False, "El producto asociado no existe."

            cursor.execute(
                """
                INSERT INTO proveedores(idprov, codprod, descripcion, costo, direccion, telefono)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (idprov, codprod, descripcion, costo, direccion, telefono),
            )
            conn.commit()
            return True, "Proveedor creado."
        finally:
            conn.close()

    def read_provider(self, idprov: str) -> Optional[dict]:
        """Return provider data as a dict when available."""
        conn = self._connection_factory()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT idprov, codprod, descripcion, costo, direccion, telefono
                FROM proveedores
                WHERE idprov = ?
                """,
                (idprov,),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
        finally:
            conn.close()

    def update_provider(
        self,
        idprov: str,
        codprod: str,
        descripcion: str,
        costo: float,
        direccion: str,
        telefono: str,
    ) -> tuple[bool, str]:
        """Update provider data, validating its presence first."""
        conn = self._connection_factory()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM proveedores WHERE idprov = ?", (idprov,))
            if not cursor.fetchone():
                return False, "Proveedor no existe."

            cursor.execute("SELECT 1 FROM productos WHERE codprod = ?", (codprod,))
            if not cursor.fetchone():
                return False, "El producto asociado no existe."

            cursor.execute(
                """
                UPDATE proveedores
                SET codprod = ?, descripcion = ?, costo = ?, direccion = ?, telefono = ?
                WHERE idprov = ?
                """,
                (codprod, descripcion, costo, direccion, telefono, idprov),
            )
            conn.commit()
            return True, "Proveedor actualizado."
        finally:
            conn.close()

    def delete_provider(self, idprov: str) -> tuple[bool, str]:
        """Remove provider rows safely."""
        conn = self._connection_factory()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM proveedores WHERE idprov = ?", (idprov,))
            if not cursor.fetchone():
                return False, "Proveedor no existe."

            cursor.execute("DELETE FROM proveedores WHERE idprov = ?", (idprov,))
            conn.commit()
            return True, "Proveedor eliminado."
        finally:
            conn.close()

    def list_providers(self) -> List[dict]:
        """Return all providers ordered by identifier."""
        conn = self._connection_factory()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT idprov, codprod, descripcion, costo, direccion, telefono FROM proveedores ORDER BY idprov"
            )
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
        finally:
            conn.close()