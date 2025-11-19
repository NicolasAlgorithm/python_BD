"""CRUD para la tabla ventas con comprobaciones de integridad referencial y controles de acceso."""

from __future__ import annotations

from typing import Any, Callable, Optional

from DB.connection import get_connection


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

    def list_sales_by_date_range(self, start_date: str, end_date: str, username: Optional[str] = None) -> list[dict[str, Any]]:
        """Return sales between start_date and end_date inclusive. Dates in 'YYYY-MM-DD' format."""
        ok, msg = self._authorize(username, 1)
        if not ok:
            return []
        conn = self._connection_factory()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT id, fecha, codclie, codprod, nomprod, costovta, canti, vriva, subtotal, vrtotal
                FROM ventas
                WHERE fecha BETWEEN ? AND ?
                ORDER BY fecha, id
                """,
                (start_date, end_date),
            )
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
            return [dict(zip(columns, row)) for row in rows]
        finally:
            conn.close()

    def list_sales_by_week(self, year: int, week: int, username: Optional[str] = None) -> list[dict[str, Any]]:
        """
        Return sales for a given year and week number.
        week: ISO-like week number expected as integer (0-53). Uses SQLite strftime('%W') semantics.
        """
        ok, msg = self._authorize(username, 1)
        if not ok:
            return []
        y = str(year)
        wk = f"{week:02d}"
        conn = self._connection_factory()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT id, fecha, codclie, codprod, nomprod, costovta, canti, vriva, subtotal, vrtotal
                FROM ventas
                WHERE strftime('%Y', fecha) = ? AND strftime('%W', fecha) = ?
                ORDER BY fecha, id
                """,
                (y, wk),
            )
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
            return [dict(zip(columns, row)) for row in rows]
        finally:
            conn.close()

    def list_sales_by_month(self, year: int, month: int, username: Optional[str] = None) -> list[dict[str, Any]]:
        """Return sales for a specific year and month (month: 1-12)."""
        ok, msg = self._authorize(username, 1)
        if not ok:
            return []
        y = str(year)
        m = f"{month:02d}"
        conn = self._connection_factory()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT id, fecha, codclie, codprod, nomprod, costovta, canti, vriva, subtotal, vrtotal
                FROM ventas
                WHERE strftime('%Y', fecha) = ? AND strftime('%m', fecha) = ?
                ORDER BY fecha, id
                """,
                (y, m),
            )
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
            return [dict(zip(columns, row)) for row in rows]
        finally:
            conn.close()

    def list_sales_by_year(self, year: int, username: Optional[str] = None) -> list[dict[str, Any]]:
        """Return sales for a specific year."""
        ok, msg = self._authorize(username, 1)
        if not ok:
            return []
        y = str(year)
        conn = self._connection_factory()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT id, fecha, codclie, codprod, nomprod, costovta, canti, vriva, subtotal, vrtotal
                FROM ventas
                WHERE strftime('%Y', fecha) = ?
                ORDER BY fecha, id
                """,
                (y,),
            )
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
            return [dict(zip(columns, row)) for row in rows]
        finally:
            conn.close()