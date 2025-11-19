"""CRUD para la tabla ventas con comprobaciones de integridad referencial y controles de acceso."""

from __future__ import annotations

from typing import Any, Callable, List, Optional

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
        # In the application a lower numeric `nivel` means more privileges
        # (1 = admin, 2 = power user, 3 = viewer). `min_level` is the
        # maximum numeric level allowed to perform the action. Allow the
        # operation when the user's level is less than or equal to that
        # threshold.
        if level > min_level:
            if min_level == 1:
                return False, "Acceso denegado: solo administradores (nivel 1) pueden realizar esta operación."
            return False, f"Acceso denegado: se requiere nivel {min_level} para esta operación."
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
        # Allow read access to all levels (1..3)
        ok, msg = self._authorize(username, 3)
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
        # Only users with level 1 or 2 can delete sales (3 = viewer)
        ok, msg = self._authorize(username, 2)
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
        # Listing should be permitted for all levels
        ok, msg = self._authorize(username, 3)
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

    def list_sales_by_date_range(
        self,
        start_date: str,
        end_date: str,
        username: Optional[str] = None,
    ) -> List[dict[str, Any]]:
        # Permit filtering by date for all levels
        ok, msg = self._authorize(username, 3)
        if not ok:
            return []
        conn = self._connection_factory()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT id, fecha, codclie, codprod, nomprod, costovta, canti, vriva, subtotal, vrtotal
                FROM ventas
                WHERE date(fecha) BETWEEN date(?) AND date(?)
                ORDER BY fecha, id
                """,
                (start_date, end_date),
            )
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
            return [dict(zip(columns, row)) for row in rows]
        finally:
            conn.close()

    def summarize_sales(
        self,
        period: str,
        username: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[dict[str, Any]]:
        # Summaries/reports are allowed for all levels (reports may be
        # restricted at the GUI level by `GUI/permissions.py`)
        ok, msg = self._authorize(username, 3)
        if not ok:
            return []
        period = period.lower()
        period_map = {
            "day": "%Y-%m-%d",
            "week": "%Y-%W",
            "month": "%Y-%m",
            "year": "%Y",
        }
        if period not in period_map:
            return []
        bucket_format = period_map[period]
        where_clauses = []
        params: List[Any] = []
        if start_date:
            where_clauses.append("date(fecha) >= date(?)")
            params.append(start_date)
        if end_date:
            where_clauses.append("date(fecha) <= date(?)")
            params.append(end_date)
        where_sql = ""
        if where_clauses:
            where_sql = "WHERE " + " AND ".join(where_clauses)
        query = f"""
            SELECT
                strftime('{bucket_format}', fecha) AS periodo,
                COUNT(*) AS transacciones,
                ROUND(SUM(vrtotal), 2) AS total_ventas,
                ROUND(SUM(vriva), 2) AS total_iva,
                COUNT(DISTINCT codclie) AS clientes_unicos,
                CASE
                    WHEN COUNT(DISTINCT codclie) = 0 THEN 0
                    ELSE ROUND(SUM(vrtotal) / COUNT(DISTINCT codclie), 2)
                END AS promedio_por_cliente
            FROM ventas
            {where_sql}
            GROUP BY periodo
            ORDER BY periodo
        """
        conn = self._connection_factory()
        try:
            cur = conn.cursor()
            cur.execute(query, params)
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
