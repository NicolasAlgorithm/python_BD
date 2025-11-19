"""Main menu that enables modules based on user privilege level."""

from __future__ import annotations

import tkinter as tk
from functools import partial

from GUI.Custumers_CRUD import open_clients_window
from GUI.Inventarios_CRUD import open_inventory_window
from GUI.Providers_CRUD import open_providers_window
from GUI.Sales_CRUD import open_sales_window
from GUI.Users_CRUD import open_users_window
from GUI.permissions import allowed_actions

try:
    from GUI.Products_CRUD import open_products_window
except ImportError:
    open_products_window = None  # will be available after module creation

try:
    from GUI.Reports import open_reports_window
except ImportError:
    open_reports_window = None


def open_main_menu(username: str, level: int) -> None:
    """Create the main menu window and display buttons the user can access."""

    root = tk.Tk()
    root.title("Menú principal")
    root.geometry("420x420")

    header = f"Usuario: {username} | Nivel: {level}"
    tk.Label(root, text=header, font=("Arial", 12)).pack(pady=10)
    tk.Label(root, text="Seleccione un módulo", font=("Arial", 14, "bold")).pack(pady=5)

    button_specs = [
        ("Usuarios", "users", open_users_window),
        ("Clientes", "clients", open_clients_window),
        ("Productos", "products", open_products_window),
        ("Proveedores", "providers", open_providers_window),
        ("Inventarios", "inventories", open_inventory_window),
        ("Ventas", "sales", open_sales_window),
        ("Reportes", "reports", open_reports_window),
    ]

    for label, module_key, handler in button_specs:
        if handler is None:
            continue
        actions = allowed_actions(module_key, level)
        if not actions:
            continue
        command = partial(handler, root, username, level)
        tk.Button(root, text=label, width=20, command=command).pack(pady=6)

    tk.Button(root, text="Cerrar sesión", width=20, command=root.destroy).pack(pady=20)

    root.mainloop()
