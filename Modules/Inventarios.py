"""CRUD y validaciones para la tabla inventarios."""

from __future__ import annotations

from typing import Callable, Optional

from DB.connection import get_connection


class InventoriesCRUD:
    """Operaciones CRUD sobre la tabla inventarios con validación de stock mínimo."""

    def __init__(self, connection_factory: Callable = get_connection) -> None:
        self._connection_factory = connection_factory

    def create_inventory(
        self,
        codprod: str,
        cantidad: int,
        stock_minimo: int,
        iva: float,
        costovta: float,
    ) -> tuple[bool, str]:
        """Crear registro de inventario validando stock mínimo y existencia del producto."""
        conn = self._connection_factory()
        try:
            cursor = conn.cursor()

            if cantidad < 0 or stock_minimo < 0:
                return False, "Cantidad y stock mínimo deben ser valores no negativos."
            if costovta < 0:
                return False, "El precio de venta no puede ser negativo."
            if cantidad < stock_minimo:
                return False, "La cantidad disponible no puede ser menor que el stock mínimo."

            cursor.execute("SELECT 1 FROM inventarios WHERE codprod = ?", (codprod,))
            if cursor.fetchone():
                return False, "Ya existe un registro de inventario para ese producto."

            cursor.execute("SELECT 1 FROM productos WHERE codprod = ?", (codprod,))
            if not cursor.fetchone():
                return False, "El producto asociado no existe."

            cursor.execute(
                """
                INSERT INTO inventarios (codprod, cantidad, stock_minimo, iva, costovta)
                VALUES (?, ?, ?, ?, ?)
                """,
                (codprod, cantidad, stock_minimo, iva, costovta),
            )
            conn.commit()
            return True, "Inventario creado."
        finally:
            conn.close()

    def read_inventory(self, codprod: str) -> Optional[dict]:
        """Leer inventario por producto, devuelve dict o None."""
        conn = self._connection_factory()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT codprod, cantidad, stock_minimo, iva, costovta FROM inventarios WHERE codprod = ?",
                (codprod,),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
        finally:
            conn.close()

    def update_inventory(
        self,
        codprod: str,
        cantidad: int,
        stock_minimo: int,
        iva: float,
        costovta: float,
    ) -> tuple[bool, str]:
        """Actualizar inventario validando stock mínimo y existencia del registro/producto."""
        conn = self._connection_factory()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM inventarios WHERE codprod = ?", (codprod,))
            if not cursor.fetchone():
                return False, "Registro de inventario no existe."

            if cantidad < 0 or stock_minimo < 0:
                return False, "Cantidad y stock mínimo deben ser valores no negativos."
            if costovta < 0:
                return False, "El precio de venta no puede ser negativo."
            if cantidad < stock_minimo:
                return False, "La cantidad disponible no puede ser menor que el stock mínimo."

            cursor.execute("SELECT 1 FROM productos WHERE codprod = ?", (codprod,))
            if not cursor.fetchone():
                return False, "El producto asociado no existe."

            cursor.execute(
                """
                UPDATE inventarios
                SET cantidad = ?, stock_minimo = ?, iva = ?, costovta = ?
                WHERE codprod = ?
                """,
                (cantidad, stock_minimo, iva, costovta, codprod),
            )
            conn.commit()
            return True, "Inventario actualizado."
        finally:
            conn.close()

    def delete_inventory(self, codprod: str) -> tuple[bool, str]:
        """Eliminar registro de inventario si existe."""
        conn = self._connection_factory()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM inventarios WHERE codprod = ?", (codprod,))
            if not cursor.fetchone():
                return False, "Registro de inventario no existe."

            cursor.execute("DELETE FROM inventarios WHERE codprod = ?", (codprod,))
            conn.commit()
            return True, "Inventario eliminado."
        finally:
            conn.close()