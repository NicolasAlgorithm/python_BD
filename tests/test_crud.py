"""Unit tests covering the core CRUD flows tied to the SQLite database."""

from __future__ import annotations

import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from DB.connection import get_connection
from DB.init_db import initialize_database
from Modules.Products import ProductsCRUD
from Modules.Providers import ProvidersCRUD


class TestDatabaseCrud(unittest.TestCase):
    """Verify that Products and Providers CRUD flows behave as expected."""

    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp_dir = TemporaryDirectory()
        cls._db_path = Path(cls._tmp_dir.name) / "test_app.db"
        os.environ["PYTHON_BD_DB_PATH"] = str(cls._db_path)
        initialize_database(cls._db_path)
        cls.products = ProductsCRUD()
        cls.providers = ProvidersCRUD()

    @classmethod
    def tearDownClass(cls) -> None:
        os.environ.pop("PYTHON_BD_DB_PATH", None)
        cls._tmp_dir.cleanup()

    def tearDown(self) -> None:
        conn = get_connection()
        try:
            # Keep FK checks happy by clearing child tables first.
            conn.execute("DELETE FROM proveedores;")
            conn.execute("DELETE FROM productos;")
            conn.commit()
        finally:
            conn.close()

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
