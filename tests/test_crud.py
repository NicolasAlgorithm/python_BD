"""Unit tests covering the core CRUD flows tied to the SQLite database."""

from __future__ import annotations

import os
import sqlite3
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from DB.connection import get_connection
from DB.init_db import initialize_database
from Modules.Inventarios import InventoriesCRUD
from Modules.Products import ProductsCRUD
from Modules.Providers import ProvidersCRUD
from Modules.Sales import SalesCRUD
from Modules.Users import UsersCRUD
from Modules.Custumers import create_client, delete_client


class MinimalCrudTests(unittest.TestCase):
    """Verify that CRUD modules enforce validation and basic flows."""

    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp_dir = TemporaryDirectory()
        cls._db_path = Path(cls._tmp_dir.name) / "test_db.sqlite"
        os.environ["PYTHON_BD_DB_PATH"] = str(cls._db_path)
        initialize_database(str(cls._db_path))
        cls.products = ProductsCRUD()
        cls.providers = ProvidersCRUD()
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
            for table in ("ventas", "inventarios", "productos", "clientes", "users"):
                try:
                    conn.execute(f"DELETE FROM {table};")
                except sqlite3.OperationalError:
                    continue
            conn.commit()
        finally:
            conn.close()

    def test_user_level_restrictions_inventory(self) -> None:
        # crear usuarios con niveles distintos
        ok, _ = self.users.create_user("u1", "pass", level=1)
        self.assertTrue(ok)
        ok, _ = self.users.create_user("u2", "pass", level=2)
        self.assertTrue(ok)
        ok, _ = self.users.create_user("u3", "pass", level=3)
        self.assertTrue(ok)

        # crear producto para inventario
        created, _ = self.products.create_product("P900", "Prod", "Desc", 0.19, 10.0)
        self.assertTrue(created)

        # nivel 1 no puede crear
        ok, msg = self.inventories.create_inventory("P900", 10, 1, 0.19, 10.0, username="u1")
        self.assertFalse(ok)
        self.assertIn("acceso", (msg or "").lower())

        # nivel 2 puede crear y actualizar pero no eliminar
        ok2, _ = self.inventories.create_inventory("P900", 10, 1, 0.19, 10.0, username="u2")
        self.assertTrue(ok2)
        up_ok, _ = self.inventories.update_inventory("P900", 15, 1, 0.19, 10.0, username="u2")
        self.assertTrue(up_ok)
        del_ok, del_msg = self.inventories.delete_inventory("P900", username="u2")
        self.assertFalse(del_ok)
        self.assertIn("acceso", (del_msg or "").lower())

        # nivel 3 puede eliminar
        del_ok2, _ = self.inventories.delete_inventory("P900", username="u3")
        self.assertTrue(del_ok2)

    def test_user_level_restrictions_sales(self) -> None:
        # crear usuarios niveles
        ok, _ = self.users.create_user("su1", "pass", level=1)
        self.assertTrue(ok)
        ok, _ = self.users.create_user("su2", "pass", level=2)
        self.assertTrue(ok)

        # producto y cliente
        created, _ = self.products.create_product("S900", "ProdS", "Desc", 0.19, 20.0)
        self.assertTrue(created)
        # insertar cliente mínima
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT OR REPLACE INTO clientes (codclie, nomclie, direc, telef, ciudad)
                VALUES (?, ?, ?, ?, ?)
                """,
                ("C900", "Cliente", "Calle 123", "5550000", "Ciudad"),
            )
            conn.commit()
        finally:
            conn.close()

        # nivel1 no puede crear venta
        ok, msg = self.sales.create_sale("2025-11-18", "C900", "S900", "ProdS", 20.0, 1, username="su1")
        self.assertFalse(ok)
        self.assertIn("acceso", (msg or "").lower())

        # nivel2 puede crear
        ok2, _ = self.sales.create_sale("2025-11-18", "C900", "S900", "ProdS", 20.0, 1, username="su2")
        self.assertTrue(ok2)


if __name__ == "__main__":
    unittest.main()
