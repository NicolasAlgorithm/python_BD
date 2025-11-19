"""Pruebas mínimas para Inventarios, Sales (referencial) y Users (hashing)."""

from __future__ import annotations

import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from DB.connection import get_connection
from DB.init_db import initialize_database
from Modules.Products import ProductsCRUD
from Modules.Inventarios import InventoriesCRUD
from Modules.Sales import SalesCRUD
from Modules.Users import UsersCRUD


class MinimalCrudTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp_dir = TemporaryDirectory()
        cls._db_path = Path(cls._tmp_dir.name) / "test_db.sqlite"
        os.environ["PYTHON_BD_DB_PATH"] = str(cls._db_path)
        initialize_database(str(cls._db_path))
        cls.products = ProductsCRUD()
        cls.inventories = InventoriesCRUD()
        cls.sales = SalesCRUD()
        cls.users = UsersCRUD()

    @classmethod
    def tearDownClass(cls) -> None:
        os.environ.pop("PYTHON_BD_DB_PATH", None)
        cls._tmp_dir.cleanup()

    def tearDown(self) -> None:
        conn = get_connection()
        try:
            # limpiar tablas usadas en las pruebas
            for t in ("ventas", "inventarios", "productos", "clientes", "users"):
                try:
                    conn.execute(f"DELETE FROM {t};")
                except Exception:
                    pass
            conn.commit()
        finally:
            conn.close()

    def _insert_client(self, codclie: str, nombre: str = "Cliente Test") -> None:
        """Inserta un cliente rellenando todas las columnas detectadas para satisfacer NOT NULL."""
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("PRAGMA table_info(clientes)")
            cols_info = cur.fetchall()
            if not cols_info:
                # crear una tabla mínima si no existe
                cur.execute("CREATE TABLE IF NOT EXISTS clientes (codclie TEXT PRIMARY KEY, nomclie TEXT NOT NULL)")
                conn.commit()
                cur.execute("PRAGMA table_info(clientes)")
                cols_info = cur.fetchall()

            cols = [c[1] for c in cols_info]
            vals = []
            insert_cols = []

            for info in cols_info:
                name = info[1]
                typ = (info[2] or "").upper()
                notnull = bool(info[3])
                dflt = info[4]

                # elegir valor para cada columna
                if name == "codclie":
                    val = codclie
                elif name.lower() in ("nomclie", "nombre", "razonsocial", "name"):
                    val = nombre
                elif dflt is not None:
                    val = dflt
                elif "INT" in typ:
                    val = 0
                elif "CHAR" in typ or "TEXT" in typ or "CLOB" in typ:
                    val = nombre if notnull else "N/A"
                elif "REAL" in typ or "FLOA" in typ or "DOUB" in typ:
                    val = 0.0
                else:
                    val = nombre if isinstance(nombre, str) else "N/A"

                insert_cols.append(name)
                vals.append(val)

            cols_sql = ", ".join(insert_cols)
            placeholders = ", ".join(["?"] * len(vals))
            sql = f"INSERT OR REPLACE INTO clientes ({cols_sql}) VALUES ({placeholders})"
            cur.execute(sql, tuple(vals))
            conn.commit()
        finally:
            conn.close()

    # Inventario: validación stock mínimo
    def test_inventory_stock_validation(self) -> None:
        created, _ = self.products.create_product("P100", "Prod", "Desc", 0.19, 10.0)
        self.assertTrue(created)
        ok, msg = self.inventories.create_inventory("P100", cantidad=5, stock_minimo=10, iva=0.19, costovta=10.0)
        self.assertFalse(ok)
        self.assertIn("menor", (msg or "").lower())

        ok2, msg2 = self.inventories.create_inventory("P100", cantidad=10, stock_minimo=10, iva=0.19, costovta=10.0)
        self.assertTrue(ok2, msg2)

    # Ventas: integridad referencial (cliente y producto)
    def test_sales_referential_integrity(self) -> None:
        # crear producto
        created, _ = self.products.create_product("S100", "ProdS", "Desc", 0.19, 20.0)
        self.assertTrue(created)

        # intentar crear venta sin cliente -> debe fallar
        ok, msg = self.sales.create_sale("2025-11-18", "NOCL", "S100", "ProdS", 20.0, 1)
        self.assertFalse(ok)
        self.assertIn("cliente", (msg or "").lower())

        # insertar cliente y crear venta -> debe funcionar
        self._insert_client("C100")
        ok2, msg2 = self.sales.create_sale("2025-11-18", "C100", "S100", "ProdS", 20.0, 2)
        self.assertTrue(ok2, msg2)

        # intentar crear venta con producto inexistente -> debe fallar
        self._insert_client("C101")
        ok3, msg3 = self.sales.create_sale("2025-11-18", "C101", "NOPROD", "X", 5.0, 1)
        self.assertFalse(ok3)
        self.assertIn("producto", (msg3 or "").lower())

    # Usuarios: hashing de contraseñas
    def test_users_password_hashing(self) -> None:
        ok, msg = self.users.create_user("testuser", "Secreta123")
        self.assertTrue(ok, msg)
        info = self.users.read_user("testuser")
        self.assertIsNotNone(info)
        assert info is not None
        self.assertIn("password_hash", info)
        self.assertIn("salt", info)
        self.assertEqual(len(info["password_hash"]), 64)
        okv, _ = self.users.verify_user("testuser", "Secreta123")
        self.assertTrue(okv)


if __name__ == "__main__":
    unittest.main()
