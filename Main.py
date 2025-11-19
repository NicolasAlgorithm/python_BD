"""Punto de entrada para iniciar la aplicación con datos precargados."""

from __future__ import annotations

from datetime import date

from DB.connection import get_connection
from DB.init_db import initialize_database
from GUI.Login import login_window
from Modules.Custumers import create_client
from Modules.Inventarios import InventoriesCRUD
from Modules.Products import ProductsCRUD
from Modules.Providers import ProvidersCRUD
from Modules.Sales import SalesCRUD
from Modules.Users import UsersCRUD


def _table_has_rows(table: str) -> bool:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(f"SELECT COUNT(1) FROM {table}")
        count = cur.fetchone()[0]
        return count > 0
    finally:
        conn.close()


def seed_demo_data() -> None:
    """Insert demo rows for every table when the database is empty."""

    if _table_has_rows("usuarios"):
        return

    users = UsersCRUD()
    products = ProductsCRUD()
    providers = ProvidersCRUD()
    inventories = InventoriesCRUD()
    sales = SalesCRUD()

    users.create_user("admin", "Admin123", level=1)
    users.create_user("manager", "Manager123", level=2)
    users.create_user("viewer", "Viewer123", level=3)

    create_client("C001", "Comercial Andina", "Cra 10 #10-10", "5551000", "Bogotá")
    create_client("C002", "Servicios Delta", "Av 45 #20-15", "5552000", "Medellín")

    products.create_product("P001", "Teclado Atlas", "Teclado mecánico 87 teclas", 0.19, 120.0)
    products.create_product("P002", "Mouse Nebula", "Mouse óptico gamer", 0.19, 60.0)

    providers.create_provider("PR001", "P001", "Distribuidor oficial", 95.0, "Calle 50 #20-30", "5553000")
    providers.create_provider("PR002", "P002", "Mayorista periféricos", 45.0, "Carrera 40 #15-25", "5554000")

    inventories.create_inventory("P001", cantidad=40, stock_minimo=10, iva=0.19, costovta=120.0, username="manager")
    inventories.create_inventory("P002", cantidad=60, stock_minimo=15, iva=0.19, costovta=60.0, username="manager")

    sale_cost = 120.0
    sale_qty = 2
    sale_subtotal = round(sale_cost * sale_qty, 2)
    sale_tax = round(sale_subtotal * 0.19, 2)
    sales.create_sale(
        fecha=date.today().isoformat(),
        codclie="C001",
        codprod="P001",
        nomprod="Teclado Atlas",
        costovta=sale_cost,
        canti=sale_qty,
        vriva=sale_tax,
        subtotal=sale_subtotal,
        vrtotal=round(sale_subtotal + sale_tax, 2),
        username="manager",
    )


def main() -> None:
    """Inicializa la base de datos, aplica datos de ejemplo y abre la ventana de login."""

    initialize_database()
    seed_demo_data()
    login_window()


if __name__ == "__main__":
    main()
