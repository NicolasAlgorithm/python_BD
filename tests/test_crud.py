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
from Modules.Users import create_user, delete_user
from Modules.Custumers import create_client, delete_client


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
            conn.execute("DELETE FROM usuarios;")
            conn.execute("DELETE FROM clientes;")
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

        missing, missing_message = self.products.delete_product("P999")
        self.assertFalse(missing)
        self.assertIn("no existe", missing_message.lower())

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

        missing, missing_message = self.providers.delete_provider("PRV-404")
        self.assertFalse(missing)
        self.assertIn("no existe", missing_message.lower())

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

        self.products.create_product(
            "P500", "Parlantes", "Parlantes bluetooth", 0.19, 200.0
        )
        created, message = self.providers.create_provider(
            "PRV-500",
            "P500",
            "Mayorista audio",
            150.0,
            "Av. 555",
            "3005555555",
        )
        self.assertTrue(created, message)

        duplicated, duplicate_message = self.providers.create_provider(
            "PRV-500",
            "P500",
            "Mayorista audio",
            150.0,
            "Av. 555",
            "3005555555",
        )
        self.assertFalse(duplicated)
        self.assertIn("ya existe", duplicate_message.lower())

    def test_user_create_and_delete_validations(self) -> None:
        created, message = create_user("admin", "clave", 1)
        self.assertTrue(created, message)

        duplicated, duplicate_message = create_user("admin", "otra", 2)
        self.assertFalse(duplicated)
        self.assertIn("ya existe", duplicate_message.lower())

        deleted, delete_message = delete_user("admin")
        self.assertTrue(deleted, delete_message)

        missing, missing_message = delete_user("admin")
        self.assertFalse(missing)
        self.assertIn("no existe", missing_message.lower())

    def test_client_create_and_delete_validations(self) -> None:
        created, message = create_client(
            "CL001", "Cliente Demo", "Calle 1", "3000000001", "Bogota"
        )
        self.assertTrue(created, message)

        duplicated, duplicate_message = create_client(
            "CL001", "Cliente Demo", "Calle 1", "3000000001", "Bogota"
        )
        self.assertFalse(duplicated)
        self.assertIn("ya existe", duplicate_message.lower())

        deleted, delete_message = delete_client("CL001")
        self.assertTrue(deleted, delete_message)

        missing, missing_message = delete_client("CL001")
        self.assertFalse(missing)
        self.assertIn("no existe", missing_message.lower())


if __name__ == "__main__":
    unittest.main()
