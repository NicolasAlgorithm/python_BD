"""Punto de entrada para iniciar la aplicación con datos precargados."""

from __future__ import annotations

from DB.connection import get_connection
from DB.init_db import initialize_database
from GUI.Login import login_window
from GUI.Main_Menu import open_main_menu
from Modules.Custumers import create_client, update_client
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
    """Insert demo rows for every table, ensuring a rich baseline dataset."""

    users = UsersCRUD()
    products = ProductsCRUD()
    providers = ProvidersCRUD()
    inventories = InventoriesCRUD()
    sales = SalesCRUD()

    def ensure_user(username: str, password: str, level: int) -> None:
        record = users.read_user(username)
        if record is None:
            users.create_user(username, password, level)
            return
        current_level = int(record.get("nivel", level))
        if current_level != level:
            users.update_user(username, None, level)

    def ensure_client(codclie: str, nomclie: str, direc: str, telef: str, ciudad: str) -> None:
        ok, _ = create_client(codclie, nomclie, direc, telef, ciudad)
        if not ok:
            update_client(codclie, nomclie, direc, telef, ciudad)

    def ensure_product(data: dict) -> None:
        ok, _ = products.create_product(
            data["codprod"],
            data["nomprod"],
            data["descripcion"],
            data["iva"],
            data["costovta"],
        )
        if not ok:
            products.update_product(
                data["codprod"],
                data["nomprod"],
                data["descripcion"],
                data["iva"],
                data["costovta"],
            )

    def ensure_provider(entry: tuple[str, str, str, float, str, str]) -> None:
        ok, _ = providers.create_provider(*entry)
        if not ok:
            providers.update_provider(*entry)

    def ensure_inventory(entry: tuple[str, int, int, float, float]) -> None:
        codprod, cantidad, stock_minimo, iva, costovta = entry
        ok, _ = inventories.create_inventory(
            codprod,
            cantidad=cantidad,
            stock_minimo=stock_minimo,
            iva=iva,
            costovta=costovta,
            username="manager",
        )
        if not ok:
            inventories.update_inventory(
                codprod,
                cantidad,
                stock_minimo,
                iva,
                costovta,
                username="manager",
            )

    def sale_exists(fecha: str, codclie: str, codprod: str, canti: int) -> bool:
        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT 1 FROM ventas WHERE fecha = ? AND codclie = ? AND codprod = ? AND canti = ?",
                (fecha, codclie, codprod, canti),
            )
            return cur.fetchone() is not None
        finally:
            conn.close()

    user_records = [
        ("admin", "Admin123", 1),
        ("manager", "Manager123", 2),
        ("viewer", "Viewer123", 3),
        ("supervisor", "Super123", 1),
        ("analyst", "Analyst123", 3),
        ("seller_north", "Seller123", 2),
        ("seller_south", "Seller234", 2),
        ("inventory_ops", "Inventory123", 2),
        ("logistics", "Logistic123", 3),
        ("support", "Support123", 3),
    ]
    for username, password, level in user_records:
        ensure_user(username, password, level)

    client_data = [
        ("C001", "Comercial Andina", "Cra 10 #10-10", "5551000", "Bogotá"),
        ("C002", "Servicios Delta", "Av 45 #20-15", "5552000", "Medellín"),
        ("C003", "Soluciones Orion", "Calle 12 #8-30", "5553001", "Cali"),
        ("C004", "Tecno Global", "Carrera 32 #45-12", "5553002", "Barranquilla"),
        ("C005", "Distribuciones Quasar", "Av 7 #33-21", "5553003", "Cartagena"),
        ("C006", "Alianza Nova", "Calle 5 #19-05", "5553004", "Manizales"),
        ("C007", "Electro Mundo", "Cra 40 #25-60", "5553005", "Pereira"),
        ("C008", "Red Comercial Sigma", "Calle 18 #4-20", "5553006", "Bucaramanga"),
        ("C009", "Mercantil Prisma", "Carrera 9 #70-15", "5553007", "Bogotá"),
        ("C010", "Grupo Horizonte", "Av 3N #45-50", "5553008", "Cali"),
    ]
    for codclie, nomclie, direc, telef, ciudad in client_data:
        ensure_client(codclie, nomclie, direc, telef, ciudad)

    product_data = [
        {"codprod": "P001", "nomprod": "Teclado Atlas", "descripcion": "Teclado mecánico 87 teclas", "iva": 0.19, "costovta": 120.0},
        {"codprod": "P002", "nomprod": "Mouse Nebula", "descripcion": "Mouse óptico gamer", "iva": 0.19, "costovta": 60.0},
        {"codprod": "P003", "nomprod": "Monitor Zenith 27", "descripcion": "Monitor LED 27 pulgadas", "iva": 0.19, "costovta": 520.0},
        {"codprod": "P004", "nomprod": "Impresora Flux", "descripcion": "Impresora multifuncional", "iva": 0.19, "costovta": 450.0},
        {"codprod": "P005", "nomprod": "Disco Externo Orion", "descripcion": "Disco duro portátil 2TB", "iva": 0.19, "costovta": 210.0},
        {"codprod": "P006", "nomprod": "Router AeroMesh", "descripcion": "Router WiFi 6 con malla", "iva": 0.19, "costovta": 180.0},
        {"codprod": "P007", "nomprod": "Parlante Pulse", "descripcion": "Parlante bluetooth 30W", "iva": 0.19, "costovta": 95.0},
        {"codprod": "P008", "nomprod": "Webcam Aurora", "descripcion": "Cámara 4K con micrófono", "iva": 0.19, "costovta": 150.0},
        {"codprod": "P009", "nomprod": "USB Hyper 128", "descripcion": "Memoria USB 128GB 3.2", "iva": 0.19, "costovta": 32.0},
        {"codprod": "P010", "nomprod": "Silla ErgoFlex", "descripcion": "Silla ergonómica de oficina", "iva": 0.19, "costovta": 380.0},
    ]
    for product in product_data:
        ensure_product(product)

    provider_data = [
        ("PR001", "P001", "Distribuidor oficial", 95.0, "Calle 50 #20-30", "5553000"),
        ("PR002", "P002", "Mayorista periféricos", 45.0, "Carrera 40 #15-25", "5554000"),
        ("PR003", "P003", "Importador displays", 430.0, "Av 30 #66-40", "5554100"),
        ("PR004", "P004", "Partner impresión", 365.0, "Calle 80 #24-11", "5554200"),
        ("PR005", "P005", "Mayorista almacenamiento", 170.0, "Cra 15 #76-20", "5554300"),
        ("PR006", "P006", "Redes avanzadas", 140.0, "Av 6 #45-18", "5554400"),
        ("PR007", "P007", "Audio premium", 70.0, "Calle 60 #30-45", "5554500"),
        ("PR008", "P008", "Video soluciones", 115.0, "Carrera 12 #90-12", "5554600"),
        ("PR009", "P009", "Componentes flash", 20.0, "Calle 45 #18-33", "5554700"),
        ("PR010", "P010", "Mobiliario corporativo", 298.0, "Av 68 #95-05", "5554800"),
    ]
    for provider in provider_data:
        ensure_provider(provider)

    inventory_data = [
        ("P001", 40, 10, 0.19, 120.0),
        ("P002", 60, 15, 0.19, 60.0),
        ("P003", 25, 8, 0.19, 520.0),
        ("P004", 18, 5, 0.19, 450.0),
        ("P005", 35, 10, 0.19, 210.0),
        ("P006", 45, 12, 0.19, 180.0),
        ("P007", 70, 20, 0.19, 95.0),
        ("P008", 30, 8, 0.19, 150.0),
        ("P009", 120, 30, 0.19, 32.0),
        ("P010", 22, 6, 0.19, 380.0),
    ]
    for inventory_entry in inventory_data:
        ensure_inventory(inventory_entry)

    product_lookup = {product["codprod"]: product for product in product_data}
    sales_entries = [
        {"fecha": "2025-01-05", "codclie": "C001", "codprod": "P001", "canti": 2},
        {"fecha": "2025-01-07", "codclie": "C002", "codprod": "P003", "canti": 1},
        {"fecha": "2025-01-12", "codclie": "C003", "codprod": "P002", "canti": 5},
        {"fecha": "2025-01-15", "codclie": "C004", "codprod": "P004", "canti": 1},
        {"fecha": "2025-02-02", "codclie": "C005", "codprod": "P005", "canti": 3},
        {"fecha": "2025-02-10", "codclie": "C006", "codprod": "P006", "canti": 4},
        {"fecha": "2025-02-18", "codclie": "C007", "codprod": "P007", "canti": 6},
        {"fecha": "2025-03-03", "codclie": "C008", "codprod": "P008", "canti": 2},
        {"fecha": "2025-03-10", "codclie": "C009", "codprod": "P009", "canti": 10},
        {"fecha": "2025-03-22", "codclie": "C010", "codprod": "P010", "canti": 2},
    ]
    for entry in sales_entries:
        product = product_lookup[entry["codprod"]]
        unit_price = product["costovta"]
        iva_rate = product["iva"]
        subtotal = round(unit_price * entry["canti"], 2)
        iva_value = round(subtotal * iva_rate, 2)
        total = round(subtotal + iva_value, 2)
        if sale_exists(entry["fecha"], entry["codclie"], entry["codprod"], entry["canti"]):
            continue
        sales.create_sale(
            fecha=entry["fecha"],
            codclie=entry["codclie"],
            codprod=entry["codprod"],
            nomprod=product["nomprod"],
            costovta=unit_price,
            canti=entry["canti"],
            vriva=iva_value,
            subtotal=subtotal,
            vrtotal=total,
            username="manager",
        )


def main() -> None:
    """Inicializa la base de datos, aplica datos de ejemplo y abre la ventana de login."""

    initialize_database()
    seed_demo_data()
    username, level = login_window()
    if username and level is not None:
        open_main_menu(username, level)


if __name__ == "__main__":
    main()
