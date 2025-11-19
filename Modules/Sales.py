"""CRUD para la tabla ventas con comprobaciones de integridad referencial (producto y cliente)."""

from __future__ import annotations

from typing import Callable, Optional
from DB.connection import get_connection


class SalesCRUD:
    """CRUD para ventas validando que exista el cliente y el producto antes de insertar/actualizar."""

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
        conn = self._connection_factory()
        try:
            cur = conn.cursor()

            if costovta < 0:
                return False, "El precio de venta no puede ser negativo."
            if canti <= 0:
                return False, "La cantidad debe ser mayor que cero."

            # Verificar cliente existente
            cur.execute("SELECT 1 FROM clientes WHERE codclie = ?", (codclie,))
            if not cur.fetchone():
                return False, "El cliente asociado no existe."

            # Verificar producto existente
            cur.execute("SELECT 1 FROM productos WHERE codprod = ?", (codprod,))
            if not cur.fetchone():
                return False, "El producto asociado no existe."

            if subtotal is None:
                subtotal = round(costovta * canti, 2)
            if vrtotal is None:
                vrtotal = round(subtotal + vriva, 2)

            cur.execute(
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
        conn = self._connection_factory()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT id, fecha, codclie, codprod, nomprod, costovta, canti, vriva, subtotal, vrtotal FROM ventas WHERE id = ?",
                (sale_id,),
            )
            row = cur.fetchone()
            if row is None:
                return None
            cols = [d[0] for d in cur.description]
            return dict(zip(cols, row))
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
        conn = self._connection_factory()
        try:
            cur = conn.cursor()

            cur.execute("SELECT 1 FROM ventas WHERE id = ?", (sale_id,))
            if not cur.fetchone():
                return False, "Registro de venta no existe."

            if costovta < 0:
                return False, "El precio de venta no puede ser negativo."
            if canti <= 0:
                return False, "La cantidad debe ser mayor que cero."

            cur.execute("SELECT 1 FROM clientes WHERE codclie = ?", (codclie,))
            if not cur.fetchone():
                return False, "El cliente asociado no existe."

            cur.execute("SELECT 1 FROM productos WHERE codprod = ?", (codprod,))
            if not cur.fetchone():
                return False, "El producto asociado no existe."

            if subtotal is None:
                subtotal = round(costovta * canti, 2)
            if vrtotal is None:
                vrtotal = round(subtotal + vriva, 2)

            cur.execute(
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
        conn = self._connection_factory()
        try:
            cur = conn.cursor()
            cur.execute("SELECT 1 FROM ventas WHERE id = ?", (sale_id,))
            if not cur.fetchone():
                return False, "Registro de venta no existe."
            cur.execute("DELETE FROM ventas WHERE id = ?", (sale_id,))
            conn.commit()
            return True, "Venta eliminada."
        finally:
            conn.close()