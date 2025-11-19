"""CRUD y validaciones para la tabla ventas."""

from __future__ import annotations

from typing import Callable, Optional

from DB.connection import get_connection


class SalesCRUD:
    """CRUD para la tabla ventas con validaciones de integridad referencial."""

    def __init__(self, connection_factory: Callable = get_connection) -> None:
        self._connection_factory = connection_factory

    def create_sale(
        self,
        fecha: str,
        codclie: str,
        codprod: str,
        nomprod: str,
        costovta: float,
        canti: int,
        vriva: float = 0.0,
        subtotal: Optional[float] = None,
        vrtotal: Optional[float] = None,
    ) -> tuple[bool, str]:
        """
        Inserta una venta validando que exista el cliente y el producto.
        Además valida valores básicos (precio >= 0, cantidad > 0).
        """
        conn = self._connection_factory()
        try:
            cursor = conn.cursor()

            # Validaciones básicas de valores
            if costovta < 0:
                return False, "El precio de venta no puede ser negativo."
            if canti <= 0:
                return False, "La cantidad debe ser mayor que cero."

            # Validar existencia del cliente
            cursor.execute("SELECT 1 FROM clientes WHERE codclie = ?", (codclie,))
            if not cursor.fetchone():
                return False, "El cliente asociado no existe."

            # Validar existencia del producto
            cursor.execute("SELECT 1 FROM productos WHERE codprod = ?", (codprod,))
            if not cursor.fetchone():
                return False, "El producto asociado no existe."

            # Calcular subtotal / total si no se proporcionan
            if subtotal is None:
                subtotal = round(costovta * canti, 2)
            if vrtotal is None:
                vrtotal = round(subtotal + vriva, 2)

            cursor.execute(
                """
                INSERT INTO ventas (fecha, codclie, codprod, nomprod, costovta, canti, vriva, subtotal, vrtotal)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (fecha, codclie, codprod, nomprod, costovta, canti, vriva, subtotal, vrtotal),
            )
            conn.commit()
            return True, "Venta registrada correctamente."
        finally:
            conn.close()

    def read_sale(self, sale_id: int) -> Optional[dict]:
        """Leer venta por id, devolver dict o None."""
        conn = self._connection_factory()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, fecha, codclie, codprod, nomprod, costovta, canti, vriva, subtotal, vrtotal FROM ventas WHERE id = ?",
                (sale_id,),
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
        sale_id: int,
        fecha: str,
        codclie: str,
        codprod: str,
        nomprod: str,
        costovta: float,
        canti: int,
        vriva: float = 0.0,
        subtotal: Optional[float] = None,
        vrtotal: Optional[float] = None,
    ) -> tuple[bool, str]:
        """
        Actualiza una venta validando integridad referencial y valores.
        """
        conn = self._connection_factory()
        try:
            cursor = conn.cursor()

            # Comprobar que la venta exista
            cursor.execute("SELECT 1 FROM ventas WHERE id = ?", (sale_id,))
            if not cursor.fetchone():
                return False, "Registro de venta no existe."

            # Validaciones de valores
            if costovta < 0:
                return False, "El precio de venta no puede ser negativo."
            if canti <= 0:
                return False, "La cantidad debe ser mayor que cero."

            # Validar existencia del cliente
            cursor.execute("SELECT 1 FROM clientes WHERE codclie = ?", (codclie,))
            if not cursor.fetchone():
                return False, "El cliente asociado no existe."

            # Validar existencia del producto
            cursor.execute("SELECT 1 FROM productos WHERE codprod = ?", (codprod,))
            if not cursor.fetchone():
                return False, "El producto asociado no existe."

            # Calcular subtotal / total si no se proporcionan
            if subtotal is None:
                subtotal = round(costovta * canti, 2)
            if vrtotal is None:
                vrtotal = round(subtotal + vriva, 2)

            cursor.execute(
                """
                UPDATE ventas
                SET fecha = ?, codclie = ?, codprod = ?, nomprod = ?, costovta = ?, canti = ?, vriva = ?, subtotal = ?, vrtotal = ?
                WHERE id = ?
                """,
                (fecha, codclie, codprod, nomprod, costovta, canti, vriva, subtotal, vrtotal, sale_id),
            )
            conn.commit()
            return True, "Venta actualizada correctamente."
        finally:
            conn.close()

    def delete_sale(self, sale_id: int) -> tuple[bool, str]:
        """Eliminar una venta si existe."""
        conn = self._connection_factory()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM ventas WHERE id = ?", (sale_id,))
            if not cursor.fetchone():
                return False, "Registro de venta no existe."

            cursor.execute("DELETE FROM ventas WHERE id = ?", (sale_id,))
            conn.commit()
            return True, "Venta eliminada."
        finally:
            conn.close()