"""Tests para Modules/MainMenu.py validando visibilidad y acceso por nivel de usuario."""

from __future__ import annotations

import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from DB.connection import get_connection
from DB.init_db import initialize_database
from Modules.Users import UsersCRUD
from Modules.MainMenu import MainMenu


class TestMainMenu(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp_dir = TemporaryDirectory()
        cls._db_path = Path(cls._tmp_dir.name) / "test_menu.db"
        os.environ["PYTHON_BD_DB_PATH"] = str(cls._db_path)
        initialize_database(str(cls._db_path))
        cls.users = UsersCRUD()
        cls.menu = MainMenu()

    @classmethod
    def tearDownClass(cls) -> None:
        os.environ.pop("PYTHON_BD_DB_PATH", None)
        cls._tmp_dir.cleanup()

    def tearDown(self) -> None:
        conn = get_connection()
        try:
            for t in ("users", "ventas", "inventarios", "productos", "clientes"):
                try:
                    conn.execute(f"DELETE FROM {t};")
                except Exception:
                    pass
            conn.commit()
        finally:
            conn.close()

    def test_menu_visibility_by_level(self) -> None:
        ok, _ = self.users.create_user("lvl1", "p", level=1)
        self.assertTrue(ok)
        ok, _ = self.users.create_user("lvl2", "p", level=2)
        self.assertTrue(ok)
        ok, _ = self.users.create_user("lvl3", "p", level=3)
        self.assertTrue(ok)

        ok, mods1 = self.menu.get_available_modules("lvl1")
        self.assertTrue(ok)
        assert isinstance(mods1, list)
        self.assertIn("Products", mods1)
        self.assertNotIn("Users", mods1)

        ok2, mods3 = self.menu.get_available_modules("lvl3")
        self.assertTrue(ok2)
        assert isinstance(mods3, list)
        self.assertIn("Users", mods3)

    def test_open_module_permission_checks(self) -> None:
        ok, _ = self.users.create_user("u_read", "p", level=1)
        self.assertTrue(ok)
        ok, _ = self.users.create_user("u_admin", "p", level=3)
        self.assertTrue(ok)

        # nivel 1 no puede abrir Users
        allowed, msg = self.menu.open_module("Users", "u_read")
        self.assertFalse(allowed)
        self.assertIn("denegado", msg.lower())

        # admin puede abrir Users
        allowed2, msg2 = self.menu.open_module("Users", "u_admin")
        self.assertTrue(allowed2)
        self.assertIn("concedido", msg2.lower())

        # módulo inexistente
        allowed3, msg3 = self.menu.open_module("NoExiste", "u_admin")
        self.assertFalse(allowed3)
        self.assertIn("no existe", msg3.lower())


if __name__ == "__main__":
    unittest.main()
