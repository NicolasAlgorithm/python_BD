from __future__ import annotations

from typing import Callable, List, Optional, Dict, Any

from DB.connection import get_connection


class SalesCRUD:
    """CRUD para la tabla ventas, adaptado a la conexión de DB/init_db.py."""

    def __init__(self, connection_factory: Callable = get_connection) -> None:
        self._connection_factory = connection_factory

    def create_sale(
        self,
        idventa: str,
        codprod: str,
        cantidad: float,
        precio: float,
    ) -> tuple[bool, str]:
        """Crear una venta validando unicidad y existencia del producto asociado."""
        conn = self._connection_factory()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM ventas WHERE idventa = ?", (idventa,))
            if cursor.fetchone():
                return False, "La venta ya existe."

            cursor.execute("SELECT 1 FROM productos WHERE codprod = ?", (codprod,))
            if not cursor.fetchone():
                return False, "El producto asociado no existe."

            cursor.execute(
                """
                INSERT INTO ventas(idventa, codprod, cantidad, precio)
                VALUES (?, ?, ?, ?)
                """,
                (idventa, codprod, cantidad, precio),
            )
            conn.commit()
            return True, "Venta creada."
        finally:
            conn.close()

    def read_sale(self, idventa: str) -> Optional[Dict[str, Any]]:
        """Leer una venta y devolverla como dict si existe."""
        conn = self._connection_factory()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT idventa, codprod, cantidad, precio
                FROM ventas
                WHERE idventa = ?
                """,
                (idventa,),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
        finally:
            conn.close()

    def update_sale(
        self,
        idventa: str,
        codprod: str,
        cantidad: float,
        precio: float,
    ) -> tuple[bool, str]:
        """Actualizar una venta existente validando su presencia y FK."""
        conn = self._connection_factory()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM ventas WHERE idventa = ?", (idventa,))
            if not cursor.fetchone():
                return False, "Venta no existe."

            cursor.execute("SELECT 1 FROM productos WHERE codprod = ?", (codprod,))
            if not cursor.fetchone():
                return False, "El producto asociado no existe."

            cursor.execute(
                """
                UPDATE ventas
                SET codprod = ?, cantidad = ?, precio = ?
                WHERE idventa = ?
                """,
                (codprod, cantidad, precio, idventa),
            )
            conn.commit()
            return True, "Venta actualizada."
        finally:
            conn.close()

    def delete_sale(self, idventa: str) -> tuple[bool, str]:
        """Eliminar una venta si existe."""
        conn = self._connection_factory()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM ventas WHERE idventa = ?", (idventa,))
            if not cursor.fetchone():
                return False, "Venta no existe."

            cursor.execute("DELETE FROM ventas WHERE idventa = ?", (idventa,))
            conn.commit()
            return True, "Venta eliminada."
        finally:
            conn.close()

    def list_sales(self) -> List[Dict[str, Any]]:
        """Listar todas las ventas como lista de diccionarios."""
        conn = self._connection_factory()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT idventa, codprod, cantidad, precio FROM ventas")
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
        finally:
            conn.close()