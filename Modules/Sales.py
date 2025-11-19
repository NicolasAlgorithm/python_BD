"""CRUD para la tabla ventas con comprobaciones de integridad referencial y controles de acceso."""

from __future__ import annotations

from typing import Any, Callable, Optional

from DB.connection import get_connection
import sqlite3


class SalesCRUD:
    """Gestiona las operaciones CRUD sobre la tabla ventas aplicando validaciones y niveles de acceso."""

    def __init__(self, connection_factory: Callable = get_connection) -> None:
        self._connection_factory = connection_factory

    def _authorize(self, username: Optional[str], min_level: int) -> tuple[bool, str]:
        if not username:
            return False, "Usuario no proporcionado."
        from Modules.Users import UsersCRUD  # import diferido para evitar ciclos

        users = UsersCRUD(self._connection_factory)
        level = users.get_user_level(username)
        if level is None:
            return False, "Usuario no encontrado."
        if level < min_level:
            return False, "Acceso denegado: nivel insuficiente."
        return True, ""

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
        username: Optional[str] = None,
    ) -> tuple[bool, str]:
        ok, msg = self._authorize(username, 2)
        if not ok:
            return False, msg

        conn = self._connection_factory()
        try:
            cur = conn.cursor()
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
                INSERT INTO ventas (fecha, codclie, codprod, nomprod, costovta, canti, vriva, subtotal, vrtotal)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (fecha, codclie, codprod, nomprod, costovta, canti, vriva, subtotal, vrtotal),
            )
            conn.commit()
            return True, "Venta registrada correctamente."
        finally:
            conn.close()

    def read_sale(self, sale_id: int, username: Optional[str] = None) -> Optional[dict[str, Any]]:
        ok, msg = self._authorize(username, 1)
        if not ok:
            return None
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
            columns = [desc[0] for desc in cur.description]
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
        username: Optional[str] = None,
    ) -> tuple[bool, str]:
        ok, msg = self._authorize(username, 2)
        if not ok:
            return False, msg
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

    def delete_sale(self, sale_id: int, username: Optional[str] = None) -> tuple[bool, str]:
        ok, msg = self._authorize(username, 3)
        if not ok:
            return False, msg
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

    def list_sales(self, username: Optional[str] = None) -> list[dict[str, Any]]:
        ok, msg = self._authorize(username, 1)
        if not ok:
            return []
        conn = self._connection_factory()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT id, fecha, codclie, codprod, nomprod, costovta, canti, vriva, subtotal, vrtotal FROM ventas ORDER BY id"
            )
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
            return [dict(zip(columns, row)) for row in rows]
        finally:
            conn.close()


def get_sales_with_customers_products(db_path="db/app.db"):
    """
    Devuelve las ventas junto con los datos del cliente y los productos vendidos.
    Retorna una lista de diccionarios con campos: sale_id, sale_date, sale_total,
    customer_id, customer_name, product_id, product_name, quantity, unit_price.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = """
    SELECT
        s.id AS sale_id,
        s.date AS sale_date,
        s.total AS sale_total,
        c.id AS customer_id,
        COALESCE(c.name, c.nomcli, '') AS customer_name,
        p.id AS product_id,
        COALESCE(p.name, p.nombre, '') AS product_name,
        sd.quantity AS quantity,
        sd.price AS unit_price
    FROM Sales s
    LEFT JOIN Custumers c ON s.customer_id = c.id OR s.customer_id = c.nomcli
    LEFT JOIN SalesDetails sd ON sd.sale_id = s.id
    LEFT JOIN Products p ON sd.product_id = p.id
    ORDER BY s.date DESC, s.id
    """

    try:
        rows = cursor.execute(sql).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()