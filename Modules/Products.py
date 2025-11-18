"""CRUD helpers for the productos table."""

from __future__ import annotations

from typing import Callable, Optional

from DB.connection import get_connection


class ProductsCRUD:
    """Encapsula las operaciones CRUD sobre la tabla productos."""

    def __init__(self, connection_factory: Callable = get_connection) -> None:
        self._connection_factory = connection_factory

    def create_product(
        self,
        codprod: str,
        nomprod: str,
        descripcion: str,
        iva: float,
        costovta: float,
    ) -> tuple[bool, str]:
        """Insert a product only if the identifier is still unused."""
        conn = self._connection_factory()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM productos WHERE codprod = ?", (codprod,))
            if cursor.fetchone():
                return False, "El producto ya existe."

            cursor.execute(
                """
                INSERT INTO productos (codprod, nomprod, descripcion, iva, costovta)
                VALUES (?, ?, ?, ?, ?)
                """,
                (codprod, nomprod, descripcion, iva, costovta),
            )
            conn.commit()
            return True, "Producto creado exitosamente."
        finally:
            conn.close()

    def read_product(self, codprod: str) -> Optional[dict]:
        """Fetch a product by id returning a dict or None."""
        conn = self._connection_factory()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT codprod, nomprod, descripcion, iva, costovta FROM productos WHERE codprod = ?",
                (codprod,),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
        finally:
            conn.close()

    def update_product(
        self,
        codprod: str,
        nomprod: str,
        descripcion: str,
        iva: float,
        costovta: float,
    ) -> tuple[bool, str]:
        """Update a product ensuring it exists beforehand."""
        conn = self._connection_factory()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM productos WHERE codprod = ?", (codprod,))
            if not cursor.fetchone():
                return False, "El producto no existe."

            cursor.execute(
                """
                UPDATE productos
                SET nomprod = ?, descripcion = ?, iva = ?, costovta = ?
                WHERE codprod = ?
                """,
                (nomprod, descripcion, iva, costovta, codprod),
            )
            conn.commit()
            return True, "Producto actualizado correctamente."
        finally:
            conn.close()

    def delete_product(self, codprod: str) -> tuple[bool, str]:
        """Remove a product when present."""
        conn = self._connection_factory()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM productos WHERE codprod = ?", (codprod,))
            if not cursor.fetchone():
                return False, "El producto no existe."

            cursor.execute("DELETE FROM productos WHERE codprod = ?", (codprod,))
            conn.commit()
            return True, "Producto eliminado."
        finally:
            conn.close()
