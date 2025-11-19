"""Menú principal: lista módulos disponibles y controla acceso por nivel de usuario."""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from Modules.Users import UsersCRUD
from DB.connection import get_connection


class MainMenu:
    """
    Provee funciones para obtener módulos visibles para un usuario y abrir módulos
    verificando el nivel mínimo requerido.
    """

    # mapa módulo -> nivel mínimo para acceder (1=read,2=write,3=admin)
    MODULE_MAP: Dict[str, int] = {
        "Products": 1,
        "Inventarios": 1,
        "Sales": 1,
        "Users": 3,  # administración de usuarios requiere nivel 3
    }

    def __init__(self, connection_factory: Callable = get_connection) -> None:
        self._connection_factory = connection_factory
        self._users = UsersCRUD(self._connection_factory)

    def get_user_level(self, username: Optional[str]) -> Optional[int]:
        if not username:
            return None
        return self._users.get_user_level(username)

    def get_available_modules(self, username: Optional[str]) -> Tuple[bool, List[str] | str]:
        """
        Devuelve (True, [módulos]) si usuario existe o si username None devuelve mensaje de error.
        """
        if not username:
            return False, "Usuario no proporcionado."
        level = self.get_user_level(username)
        if level is None:
            return False, "Usuario no encontrado."
        available = [m for m, min_lvl in self.MODULE_MAP.items() if level >= min_lvl]
        return True, available

    def open_module(self, module_name: str, username: Optional[str]) -> Tuple[bool, str]:
        """
        Intento de navegar a módulo. Devuelve (True, msg) si el usuario tiene permiso.
        """
        if module_name not in self.MODULE_MAP:
            return False, "Módulo no existe."
        if not username:
            return False, "Usuario no proporcionado."
        level = self.get_user_level(username)
        if level is None:
            return False, "Usuario no encontrado."
        min_lvl = self.MODULE_MAP[module_name]
        if level < min_lvl:
            return False, "Acceso denegado: nivel insuficiente."
        return True, f"Acceso concedido a {module_name}."