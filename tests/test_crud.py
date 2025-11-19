"""Unit tests for Modules/Inventarios.py validating stock minimum rules and referential checks."""

from __future__ import annotations

import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from DB.connection import get_connection
from DB.init_db import initialize_database
from Modules.Products import ProductsCRUD
from Modules.Inventarios import InventoriesCRUD
from Modules.Users import UsersCRUD
from Modules.Sales import SalesCRUD


class TestInventoriesCrud(unittest.TestCase):
    """Tests for InventoriesCRUD focusing on stock minimum validation and referential integrity."""

    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp_dir = TemporaryDirectory()
        cls._db_path = Path(cls._tmp_dir.name) / "test_inventarios.db"
        os.environ["PYTHON_BD_DB_PATH"] = str(cls._db_path)
        initialize_database(cls._db_path)
        cls.products = ProductsCRUD()
        cls.inventories = InventoriesCRUD()

    @classmethod
    def tearDownClass(cls) -> None:
        os.environ.pop("PYTHON_BD_DB_PATH", None)
        cls._tmp_dir.cleanup()

    def tearDown(self) -> None:
        conn = get_connection()
        try:
            # Clear inventories first to keep FK constraints happy, then products.
            conn.execute("DELETE FROM inventarios;")
            conn.execute("DELETE FROM productos;")
            conn.commit()
        finally:
            conn.close()

    def test_create_inventory_success(self) -> None:
        created, msg = self.products.create_product(
            "IP001", "Producto A", "Desc A", 0.19, 50.0
        )
        self.assertTrue(created, msg)
        ok, message = self.inventories.create_inventory(
            "IP001", cantidad=100, stock_minimo=20, iva=0.19, costovta=50.0
        )
        self.assertTrue(ok, message)
        inv = self.inventories.read_inventory("IP001")
        self.assertIsNotNone(inv)
        assert inv is not None
        self.assertEqual(inv["cantidad"], 100)
        self.assertEqual(inv["stock_minimo"], 20)

    def test_inventory_prevent_negative_values(self) -> None:
        created, _ = self.products.create_product(
            "IP002", "Producto B", "Desc B", 0.19, 30.0
        )
        self.assertTrue(created)
        ok, msg = self.inventories.create_inventory(
            "IP002", cantidad=-5, stock_minimo=0, iva=0.19, costovta=30.0
        )
        self.assertFalse(ok)
        self.assertIn("no negativos", msg.lower() or "")

        ok2, msg2 = self.inventories.create_inventory(
            "IP002", cantidad=10, stock_minimo=-1, iva=0.19, costovta=30.0
        )
        self.assertFalse(ok2)
        self.assertIn("no negativos", msg2.lower() or "")

        ok3, msg3 = self.inventories.create_inventory(
            "IP002", cantidad=10, stock_minimo=5, iva=0.19, costovta=-10.0
        )
        self.assertFalse(ok3)
        self.assertIn("no puede ser negativo", msg3.lower() or "")

    def test_inventory_quantity_less_than_stock_minimum_fails(self) -> None:
        created, _ = self.products.create_product(
            "IP003", "Producto C", "Desc C", 0.19, 40.0
        )
        self.assertTrue(created)
        ok, msg = self.inventories.create_inventory(
            "IP003", cantidad=3, stock_minimo=5, iva=0.19, costovta=40.0
        )
        self.assertFalse(ok)
        # message should indicate quantity less than stock minimum
        self.assertTrue(
            "menor" in msg.lower() or "stock" in msg.lower(),
            f"Unexpected message for stock-min check: {msg}",
        )

    def test_prevent_duplicate_inventory(self) -> None:
        created, _ = self.products.create_product(
            "IP004", "Producto D", "Desc D", 0.19, 25.0
        )
        self.assertTrue(created)
        ok, _ = self.inventories.create_inventory(
            "IP004", cantidad=20, stock_minimo=5, iva=0.19, costovta=25.0
        )
        self.assertTrue(ok)
        ok2, msg2 = self.inventories.create_inventory(
            "IP004", cantidad=30, stock_minimo=5, iva=0.19, costovta=25.0
        )
        self.assertFalse(ok2)
        self.assertIn("ya existe", msg2.lower() or "")

    def test_requires_existing_product(self) -> None:
        ok, msg = self.inventories.create_inventory(
            "NO-PROD", cantidad=10, stock_minimo=1, iva=0.19, costovta=10.0
        )
        self.assertFalse(ok)
        self.assertIn("no existe", msg.lower() or "")

    def test_update_inventory_checks_stock_minimum(self) -> None:
        created, _ = self.products.create_product(
            "IP005", "Producto E", "Desc E", 0.19, 60.0
        )
        self.assertTrue(created)
        ok, _ = self.inventories.create_inventory(
            "IP005", cantidad=50, stock_minimo=10, iva=0.19, costovta=60.0
        )
        self.assertTrue(ok)

        # Attempt update with cantidad < stock_minimo -> should fail
        up_ok, up_msg = self.inventories.update_inventory(
            "IP005", cantidad=5, stock_minimo=10, iva=0.19, costovta=60.0
        )
        self.assertFalse(up_ok)
        self.assertTrue("menor" in up_msg.lower() or "stock" in up_msg.lower())

        # Valid update
        up_ok2, up_msg2 = self.inventories.update_inventory(
            "IP005", cantidad=30, stock_minimo=10, iva=0.19, costovta=60.0
        )
        self.assertTrue(up_ok2, up_msg2)
        inv = self.inventories.read_inventory("IP005")
        self.assertIsNotNone(inv)
        assert inv is not None
        self.assertEqual(inv["cantidad"], 30)

    def test_delete_inventory(self) -> None:
        created, _ = self.products.create_product(
            "IP006", "Producto F", "Desc F", 0.19, 15.0
        )
        self.assertTrue(created)
        ok, _ = self.inventories.create_inventory(
            "IP006", cantidad=15, stock_minimo=5, iva=0.19, costovta=15.0
        )
        self.assertTrue(ok)
        deleted, msg = self.inventories.delete_inventory("IP006")
        self.assertTrue(deleted, msg)
        self.assertIsNone(self.inventories.read_inventory("IP006"))

    # Additional tests focused on stock validation edge cases

    def test_create_inventory_quantity_equals_stock_minimum_succeeds(self) -> None:
        created, _ = self.products.create_product(
            "IP007", "Producto G", "Desc G", 0.19, 20.0
        )
        self.assertTrue(created)
        ok, msg = self.inventories.create_inventory(
            "IP007", cantidad=5, stock_minimo=5, iva=0.19, costovta=20.0
        )
        self.assertTrue(ok, msg)
        inv = self.inventories.read_inventory("IP007")
        self.assertIsNotNone(inv)
        assert inv is not None
        self.assertEqual(inv["cantidad"], 5)
        self.assertEqual(inv["stock_minimo"], 5)

    def test_create_inventory_zero_quantity_and_zero_stock_minimum_succeeds(self) -> None:
        created, _ = self.products.create_product(
            "IP008", "Producto H", "Desc H", 0.19, 10.0
        )
        self.assertTrue(created)
        ok, msg = self.inventories.create_inventory(
            "IP008", cantidad=0, stock_minimo=0, iva=0.19, costovta=10.0
        )
        self.assertTrue(ok, msg)
        inv = self.inventories.read_inventory("IP008")
        self.assertIsNotNone(inv)
        assert inv is not None
        self.assertEqual(inv["cantidad"], 0)
        self.assertEqual(inv["stock_minimo"], 0)

    def test_update_inventory_set_quantity_equal_to_stock_minimum(self) -> None:
        created, _ = self.products.create_product(
            "IP009", "Producto I", "Desc I", 0.19, 45.0
        )
        self.assertTrue(created)
        ok, _ = self.inventories.create_inventory(
            "IP009", cantidad=10, stock_minimo=2, iva=0.19, costovta=45.0
        )
        self.assertTrue(ok)
        up_ok, up_msg = self.inventories.update_inventory(
            "IP009", cantidad=2, stock_minimo=2, iva=0.19, costovta=45.0
        )
        self.assertTrue(up_ok, up_msg)
        inv = self.inventories.read_inventory("IP009")
        self.assertIsNotNone(inv)
        assert inv is not None
        self.assertEqual(inv["cantidad"], 2)
        self.assertEqual(inv["stock_minimo"], 2)

    def test_update_inventory_cannot_set_stock_minimum_greater_than_quantity(self) -> None:
        created, _ = self.products.create_product(
            "IP010", "Producto J", "Desc J", 0.19, 12.0
        )
        self.assertTrue(created)
        ok, _ = self.inventories.create_inventory(
            "IP010", cantidad=8, stock_minimo=3, iva=0.19, costovta=12.0
        )
        self.assertTrue(ok)
        up_ok, up_msg = self.inventories.update_inventory(
            "IP010", cantidad=6, stock_minimo=7, iva=0.19, costovta=12.0
        )
        self.assertFalse(up_ok)
        self.assertTrue("menor" in up_msg.lower() or "stock" in up_msg.lower())


class TestUsersCrud(unittest.TestCase):
    """Pruebas para el módulo Users: hashing y verificación de contraseñas."""

    @classmethod
    def setUpClass(cls) -> None:
        # Crear base de datos de prueba aislada
        cls._tmp_dir = TemporaryDirectory()
        cls._db_path = Path(cls._tmp_dir.name) / "test_users.db"
        os.environ["PYTHON_BD_DB_PATH"] = str(cls._db_path)
        initialize_database(cls._db_path)
        cls.users = UsersCRUD()

    @classmethod
    def tearDownClass(cls) -> None:
        os.environ.pop("PYTHON_BD_DB_PATH", None)
        cls._tmp_dir.cleanup()

    def tearDown(self) -> None:
        conn = get_connection()
        try:
            conn.execute("DELETE FROM users;")
            conn.commit()
        finally:
            conn.close()

    def test_create_user_stores_hashed_password(self) -> None:
        ok, msg = self.users.create_user("testuser1", "Secreta123")
        self.assertTrue(ok, msg)
        info = self.users.read_user("testuser1")
        self.assertIsNotNone(info)
        assert info is not None
        self.assertIn("password_hash", info)
        self.assertIn("salt", info)
        # El hash no debe ser la contraseña en claro
        self.assertNotEqual(info["password_hash"], "Secreta123")
        # El hash debe tener longitud de SHA256 en hex (64 chars)
        self.assertEqual(len(info["password_hash"]), 64)
        self.assertGreater(len(info["salt"]), 0)

    def test_verify_user_success_and_failure(self) -> None:
        ok, msg = self.users.create_user("testuser2", "MiPass")
        self.assertTrue(ok, msg)
        okv, msgv = self.users.verify_user("testuser2", "MiPass")
        self.assertTrue(okv, msgv)
        okv2, msgv2 = self.users.verify_user("testuser2", "WrongPass")
        self.assertFalse(okv2)
        self.assertIn("incorrecta", msgv2.lower() or "")

    def test_duplicate_user_fails(self) -> None:
        ok, _ = self.users.create_user("testuser3", "Pwd1")
        self.assertTrue(ok)
        ok2, msg2 = self.users.create_user("testuser3", "Pwd1")
        self.assertFalse(ok2)
        self.assertIn("ya existe", msg2.lower() or "")


class TestSalesCrud(unittest.TestCase):
    """Pruebas para SalesCRUD: verificar integridad referencial (cliente y producto)."""

    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp_dir = TemporaryDirectory()
        cls._db_path = Path(cls._tmp_dir.name) / "test_sales.db"
        os.environ["PYTHON_BD_DB_PATH"] = str(cls._db_path)
        initialize_database(cls._db_path)
        cls.products = ProductsCRUD()
        cls.sales = SalesCRUD()

    @classmethod
    def tearDownClass(cls) -> None:
        os.environ.pop("PYTHON_BD_DB_PATH", None)
        cls._tmp_dir.cleanup()

    def tearDown(self) -> None:
        conn = get_connection()
        try:
            conn.execute("DELETE FROM ventas;")
            conn.execute("DELETE FROM productos;")
            conn.execute("DELETE FROM clientes;")
            conn.commit()
        finally:
            conn.close()

    def _insert_client(self, codclie: str, nombre: str = "Cliente Test") -> None:
        conn = get_connection()
        try:
            cur = conn.cursor()
            # Obtener columnas reales de la tabla 'clientes'
            cur.execute("PRAGMA table_info(clientes)")
            cols_info = cur.fetchall()
            cols = [c[1] for c in cols_info]

            # Si la tabla no existe o no tiene columnas previsibles, crear una mínima
            if not cols:
                cur.execute("CREATE TABLE IF NOT EXISTS clientes (codclie TEXT PRIMARY KEY)")
                cols = ["codclie"]

            # Insertar de forma segura según columnas disponibles
            if "codclie" in cols and "nombre" in cols:
                cur.execute(
                    "INSERT OR REPLACE INTO clientes (codclie, nombre) VALUES (?, ?)",
                    (codclie, nombre),
                )
            elif "codclie" in cols:
                cur.execute(
                    "INSERT OR REPLACE INTO clientes (codclie) VALUES (?)",
                    (codclie,),
                )
            else:
                # Fallback: insertar en la primera columna que exista (intenta evitar crash)
                first_col = cols[0]
                cur.execute(
                    f"INSERT OR REPLACE INTO clientes ({first_col}) VALUES (?)",
                    (codclie,),
                )
            conn.commit()
        finally:
            conn.close()

    def test_create_sale_success(self) -> None:
        # Crear producto y cliente
        created, _ = self.products.create_product("S001", "Prod S1", "Desc", 0.19, 100.0)
        self.assertTrue(created)
        self._insert_client("C001")
        ok, msg = self.sales.create_sale(
            fecha="2025-11-18",
            codclie="C001",
            codprod="S001",
            nomprod="Prod S1",
            costovta=100.0,
            canti=2,
            vriva=19.0,
        )
        self.assertTrue(ok, msg)
        # Leer la venta recién creada
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id FROM ventas ORDER BY id DESC LIMIT 1")
            row = cur.fetchone()
            self.assertIsNotNone(row)
            sale_id = row[0]
        finally:
            conn.close()
        sale = self.sales.read_sale(sale_id)
        self.assertIsNotNone(sale)
        assert sale is not None
        self.assertEqual(sale["codclie"], "C001")
        self.assertEqual(sale["codprod"], "S001")
        self.assertEqual(sale["canti"], 2)

    def test_prevent_sale_without_product(self) -> None:
        self._insert_client("C002")
        ok, msg = self.sales.create_sale("2025-11-18", "C002", "NO-PROD", "NoProd", 10.0, 1)
        self.assertFalse(ok)
        self.assertIn("producto", msg.lower())

    def test_prevent_sale_without_client(self) -> None:
        created, _ = self.products.create_product("S002", "Prod S2", "Desc", 0.19, 50.0)
        self.assertTrue(created)
        ok, msg = self.sales.create_sale("2025-11-18", "NO-CLIE", "S002", "Prod S2", 50.0, 1)
        self.assertFalse(ok)
        self.assertIn("cliente", msg.lower())

    def test_update_sale_checks_referential(self) -> None:
        created, _ = self.products.create_product("S003", "Prod S3", "Desc", 0.19, 20.0)
        self.assertTrue(created)
        self._insert_client("C003")
        ok, msg = self.sales.create_sale("2025-11-18", "C003", "S003", "Prod S3", 20.0, 1)
        self.assertTrue(ok, msg)

        # obtener id
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id FROM ventas ORDER BY id DESC LIMIT 1")
            sale_id = cur.fetchone()[0]
        finally:
            conn.close()

        # intentar actualizar a producto inexistente
        up_ok, up_msg = self.sales.update_sale(sale_id, "2025-11-19", "C003", "NO-PROD", "X", 20.0, 1)
        self.assertFalse(up_ok)
        self.assertIn("producto", up_msg.lower())

        # intentar actualizar a cliente inexistente
        up_ok2, up_msg2 = self.sales.update_sale(sale_id, "2025-11-19", "NO-CLIE", "S003", "Prod S3", 20.0, 1)
        self.assertFalse(up_ok2)
        self.assertIn("cliente", up_msg2.lower())

        # actualización válida
        self._insert_client("C004")
        up_ok3, up_msg3 = self.sales.update_sale(sale_id, "2025-11-20", "C004", "S003", "Prod S3", 20.0, 2)
        self.assertTrue(up_ok3, up_msg3)
        sale = self.sales.read_sale(sale_id)
        self.assertIsNotNone(sale)
        assert sale is not None
        self.assertEqual(sale["codclie"], "C004")
        self.assertEqual(sale["canti"], 2)

    def test_delete_sale(self) -> None:
        created, _ = self.products.create_product("S004", "Prod S4", "Desc", 0.19, 5.0)
        self.assertTrue(created)
        self._insert_client("C005")
        ok, _ = self.sales.create_sale("2025-11-18", "C005", "S004", "Prod S4", 5.0, 1)
        self.assertTrue(ok)
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT id FROM ventas ORDER BY id DESC LIMIT 1")
            sale_id = cur.fetchone()[0]
        finally:
            conn.close()
        deleted, msg = self.sales.delete_sale(sale_id)
        self.assertTrue(deleted, msg)
        self.assertIsNone(self.sales.read_sale(sale_id))


if __name__ == "__main__":
    unittest.main()
