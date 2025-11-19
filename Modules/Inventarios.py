"""CRUD y validaciones para la tabla inventarios."""

from __future__ import annotations

from typing import Callable, Optional, Tuple

from DB.connection import get_connection
import sqlite3


class InventoriesCRUD:
    """Operaciones CRUD sobre la tabla inventarios con validación de stock mínimo y control de acceso por nivel."""

    def __init__(self, connection_factory: Callable = get_connection) -> None:
        self._connection_factory = connection_factory

    def _validate_values(self, cantidad: int, stock_minimo: int, costovta: float) -> Tuple[bool, str]:
        if cantidad < 0 or stock_minimo < 0:
            return False, "Cantidad y stock mínimo deben ser valores no negativos."
        if costovta < 0:
            return False, "El precio de venta no puede ser negativo."
        if cantidad < stock_minimo:
            return False, "La cantidad disponible no puede ser menor que el stock mínimo."
        return True, ""

    def _authorize(self, username: Optional[str], min_level: int) -> Tuple[bool, str]:
        if not username:
            return False, "Usuario no proporcionado."
        # import aquí para evitar ciclos al cargar módulos
        from Modules.Users import UsersCRUD

        users = UsersCRUD(self._connection_factory)
        level = users.get_user_level(username)
        if level is None:
            return False, "Usuario no encontrado."
        if level < min_level:
            return False, "Acceso denegado: nivel insuficiente."
        return True, ""

    def create_inventory(
        self,
        codprod: str,
        cantidad: int,
        stock_minimo: int,
        iva: float,
        costovta: float,
        username: Optional[str] = None,
    ) -> tuple[bool, str]:
        # crear/update requieren nivel >=2
        ok, msg = self._authorize(username, 2)
        if not ok:
            return False, msg

        conn = self._connection_factory()
        try:
            cursor = conn.cursor()
            ok, msg = self._validate_values(cantidad, stock_minimo, costovta)
            if not ok:
                return False, msg
            cursor.execute("SELECT 1 FROM inventarios WHERE codprod = ?", (codprod,))
            if cursor.fetchone():
                return False, "Ya existe un registro de inventario para ese producto."
            cursor.execute("SELECT nomprod FROM productos WHERE codprod = ?", (codprod,))
            product_row = cursor.fetchone()
            if not product_row:
                return False, "El producto asociado no existe."
            nomprod = product_row[0]
            cursor.execute(
                """
                INSERT INTO inventarios (codprod, nomprod, cantidad, stock_minimo, iva, costovta)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (codprod, nomprod, cantidad, stock_minimo, iva, costovta),
            )
            conn.commit()
            return True, "Inventario creado."
        finally:
            conn.close()

    def read_inventory(self, codprod: str, username: Optional[str] = None) -> Optional[dict]:
        ok, msg = self._authorize(username, 1)
        if not ok:
            return None
        conn = self._connection_factory()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT codprod, nomprod, cantidad, stock_minimo, iva, costovta FROM inventarios WHERE codprod = ?",
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
        username: Optional[str] = None,
    ) -> tuple[bool, str]:
        ok, msg = self._authorize(username, 2)
        if not ok:
            return False, msg

        conn = self._connection_factory()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM inventarios WHERE codprod = ?", (codprod,))
            if not cursor.fetchone():
                return False, "Registro de inventario no existe."
            ok, msg = self._validate_values(cantidad, stock_minimo, costovta)
            if not ok:
                return False, msg
            cursor.execute("SELECT nomprod FROM productos WHERE codprod = ?", (codprod,))
            product_row = cursor.fetchone()
            if not product_row:
                return False, "El producto asociado no existe."
            nomprod = product_row[0]
            cursor.execute(
                """
                UPDATE inventarios
                SET nomprod = ?, cantidad = ?, stock_minimo = ?, iva = ?, costovta = ?
                WHERE codprod = ?
                """,
                (nomprod, cantidad, stock_minimo, iva, costovta, codprod),
            )
            conn.commit()
            return True, "Inventario actualizado."
        finally:
            conn.close()

    def delete_inventory(self, codprod: str, username: Optional[str] = None) -> tuple[bool, str]:
        ok, msg = self._authorize(username, 3)
        if not ok:
            return False, msg
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


def get_inventory_with_products_providers(db_path="db/app.db"):
    """
    Devuelve registros de inventario junto con información del producto y su proveedor.
    Campos devueltos: inventory_id, stock, product_id, product_name, provider_id, provider_name
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = """
    SELECT
        i.id AS inventory_id,
        i.stock AS stock,
        p.id AS product_id,
        COALESCE(p.name, p.nombre, '') AS product_name,
        prov.id AS provider_id,
        COALESCE(prov.name, prov.razon_social, '') AS provider_name
    FROM Inventarios i
    LEFT JOIN Products p ON i.product_id = p.id
    LEFT JOIN Providers prov ON p.provider_id = prov.id
    ORDER BY p.id
    """

    try:
        rows = cursor.execute(sql).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()