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
from Modules.Users import create_user, delete_user
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

    @classmethod
    def tearDownClass(cls) -> None:
        os.environ.pop("PYTHON_BD_DB_PATH", None)
        cls._tmp_dir.cleanup()

    def tearDown(self) -> None:
        conn = get_connection()
        try:
            for table in (
                "ventas",
                "inventarios",
                "proveedores",
                "clientes",
                "productos",
                "users",
            ):
                try:
                    conn.execute(f"DELETE FROM {table};")
                except sqlite3.OperationalError:
                    continue
            conn.commit()
        finally:
            conn.close()

    def _insert_client(
        self,
        client_id: str,
        name: str = "Cliente Test",
        address: str = "Calle 123",
        phone: str = "3000000000",
        city: str = "Bogota",
    ) -> None:
        conn = get_connection()
        try:
            conn.execute(
                """
                INSERT OR REPLACE INTO clientes (codclie, nomclie, direc, telef, ciudad)
                VALUES (?, ?, ?, ?, ?)
                """,
                (client_id, name, address, phone, city),
            )
            conn.commit()
        finally:
            conn.close()

    def test_inventory_crud_flow(self) -> None:
        self.products.create_product(
            "INV-1", "UPS", "Respaldo de energia", 0.19, 450.0
        )

        created, message = self.inventories.create_inventory(
            "INV-1", cantidad=20, stock_minimo=5, iva=0.19, costovta=480.0
        )
        self.assertTrue(created, message)

        inventory = self.inventories.read_inventory("INV-1")
        self.assertIsNotNone(inventory)
        assert inventory is not None
        self.assertEqual(inventory["cantidad"], 20)

        updated, update_message = self.inventories.update_inventory(
            "INV-1", cantidad=15, stock_minimo=4, iva=0.19, costovta=490.0
        )
        self.assertTrue(updated, update_message)

        inventory = self.inventories.read_inventory("INV-1")
        self.assertIsNotNone(inventory)
        assert inventory is not None
        self.assertEqual(inventory["cantidad"], 15)

        deleted, delete_message = self.inventories.delete_inventory("INV-1")
        self.assertTrue(deleted, delete_message)
        self.assertIsNone(self.inventories.read_inventory("INV-1"))

    def test_inventory_requires_existing_product(self) -> None:
        created, message = self.inventories.create_inventory(
            "INV-404", cantidad=5, stock_minimo=1, iva=0.19, costovta=100.0
        )
        self.assertFalse(created)
        self.assertIn("no existe", message.lower())

    def test_prevent_duplicate_inventory(self) -> None:
        self.products.create_product(
            "INV-2", "Router", "Router de 4 antenas", 0.19, 210.0
        )
        first_created, first_message = self.inventories.create_inventory(
            "INV-2", cantidad=10, stock_minimo=2, iva=0.19, costovta=220.0
        )
        self.assertTrue(first_created, first_message)

        duplicated, duplicate_message = self.inventories.create_inventory(
            "INV-2", cantidad=12, stock_minimo=2, iva=0.19, costovta=220.0
        )
        self.assertFalse(duplicated)
        self.assertIn("ya existe", duplicate_message.lower())

    def test_inventory_quantity_cannot_be_below_stock(self) -> None:
        self.products.create_product(
            "INV-3", "Cable HDMI", "Cable 4k", 0.19, 30.0
        )
        created, message = self.inventories.create_inventory(
            "INV-3", cantidad=1, stock_minimo=5, iva=0.19, costovta=35.0
        )
        self.assertFalse(created)
        self.assertIn("no puede ser menor", message.lower())

    def test_sales_referential_integrity(self) -> None:
        created, _ = self.products.create_product(
            "S100", "ProdS", "Desc", 0.19, 20.0
        )
        self.assertTrue(created)

        ok, msg = self.sales.create_sale(
            "2025-11-18", "NOCL", "S100", "ProdS", 20.0, 1
        )
        self.assertFalse(ok)
        self.assertIn("cliente", (msg or "").lower())

        self._insert_client("C100")
        ok2, msg2 = self.sales.create_sale(
            "2025-11-18", "C100", "S100", "ProdS", 20.0, 2
        )
        self.assertTrue(ok2, msg2)

        self._insert_client("C101")
        ok3, msg3 = self.sales.create_sale(
            "2025-11-18", "C101", "NOPROD", "X", 5.0, 1
        )
        self.assertFalse(ok3)
        self.assertIn("producto", (msg3 or "").lower())

    def test_product_crud_flow(self) -> None:
        created, message = self.products.create_product(
            "P001", "Teclado", "Teclado mecanico", 0.19, 120.0
        )
        self.assertTrue(created, message)

        product = self.products.read_product("P001")
        self.assertIsNotNone(product)
        assert product is not None
        self.assertEqual(product["nomprod"], "Teclado")

        updated, update_message = self.products.update_product(
            "P001", "Teclado RGB", "Teclado con iluminacion", 0.19, 150.0
        )
        self.assertTrue(updated, update_message)

        product = self.products.read_product("P001")
        self.assertIsNotNone(product)
        assert product is not None
        self.assertEqual(product["nomprod"], "Teclado RGB")

        deleted, delete_message = self.products.delete_product("P001")
        self.assertTrue(deleted, delete_message)
        self.assertIsNone(self.products.read_product("P001"))

    def test_prevent_duplicate_product(self) -> None:
        created, _ = self.products.create_product(
            "P002", "Mouse", "Mouse inalambrico", 0.19, 60.0
        )
        self.assertTrue(created)

        duplicated, message = self.products.create_product(
            "P002", "Mouse", "Mouse inalambrico", 0.19, 60.0
        )
        self.assertFalse(duplicated)
        self.assertIn("ya existe", message.lower())

    def test_provider_crud_flow(self) -> None:
        self.products.create_product(
            "P100", "Monitor", "Monitor 24 pulgadas", 0.19, 800.0
        )

        created, message = self.providers.create_provider(
            "PRV-1",
            "P100",
            "Mayorista tecnologia",
            700.0,
            "Av. 123",
            "3001234567",
        )
        self.assertTrue(created, message)

        provider = self.providers.read_provider("PRV-1")
        self.assertIsNotNone(provider)
        assert provider is not None
        self.assertEqual(provider["codprod"], "P100")

        updated, update_message = self.providers.update_provider(
            "PRV-1",
            "P100",
            "Mayorista gamer",
            650.0,
            "Av. 321",
            "3009876543",
        )
        self.assertTrue(updated, update_message)

        provider = self.providers.read_provider("PRV-1")
        self.assertIsNotNone(provider)
        assert provider is not None
        self.assertEqual(provider["descripcion"], "Mayorista gamer")

        deleted, delete_message = self.providers.delete_provider("PRV-1")
        self.assertTrue(deleted, delete_message)
        self.assertIsNone(self.providers.read_provider("PRV-1"))

    def test_provider_requires_existing_product(self) -> None:
        created, message = self.providers.create_provider(
            "PRV-404",
            "P404",
            "Sin producto",
            10.0,
            "Av. 000",
            "3000000000",
        )
        self.assertFalse(created)
        self.assertIn("no existe", message.lower())


if __name__ == "__main__":
    unittest.main()
