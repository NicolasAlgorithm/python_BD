"""
Initialize the SQLite schema used by the inventory and sales application.

The module creates all required base tables plus a reporting view that
joins sales with clients and products. Run it whenever you need to bootstrap
or refresh the database structure.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable

DB_PATH = Path(__file__).with_name("app.db")

TABLE_DEFINITIONS: dict[str, str] = {
    "usuarios": """
        CREATE TABLE IF NOT EXISTS usuarios (
            nomusu TEXT PRIMARY KEY,
            clave TEXT NOT NULL,
            salt TEXT NOT NULL,
            nivel INTEGER NOT NULL CHECK (nivel IN (1, 2, 3))
        );
    """,
    "clientes": """
        CREATE TABLE IF NOT EXISTS clientes (
            codclie TEXT PRIMARY KEY,
            nomclie TEXT NOT NULL,
            direc TEXT NOT NULL,
            telef TEXT NOT NULL,
            ciudad TEXT NOT NULL
        );
    """,
    "productos": """
        CREATE TABLE IF NOT EXISTS productos (
            codprod TEXT PRIMARY KEY,
            nomprod TEXT NOT NULL,
            descripcion TEXT NOT NULL,
            iva REAL NOT NULL DEFAULT 0,
            costovta REAL NOT NULL CHECK (costovta >= 0)
        );
    """,
    "proveedores": """
        CREATE TABLE IF NOT EXISTS proveedores (
            idprov TEXT PRIMARY KEY,
            codprod TEXT NOT NULL,
            descripcion TEXT NOT NULL,
            costo REAL NOT NULL CHECK (costo >= 0),
            direccion TEXT NOT NULL,
            telefono TEXT NOT NULL,
            FOREIGN KEY (codprod) REFERENCES productos (codprod)
                ON UPDATE CASCADE ON DELETE RESTRICT
        );
    """,
    "inventarios": """
        CREATE TABLE IF NOT EXISTS inventarios (
            codprod TEXT PRIMARY KEY,
            nomprod TEXT NOT NULL,
            cantidad INTEGER NOT NULL DEFAULT 0 CHECK (cantidad >= 0),
            stock_minimo INTEGER NOT NULL DEFAULT 0 CHECK (stock_minimo >= 0),
            iva REAL NOT NULL DEFAULT 0,
            costovta REAL NOT NULL DEFAULT 0 CHECK (costovta >= 0),
            FOREIGN KEY (codprod) REFERENCES productos (codprod)
                ON UPDATE CASCADE ON DELETE RESTRICT
        );
    """,
    "ventas": """
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            codclie TEXT NOT NULL,
            codprod TEXT NOT NULL,
            nomprod TEXT NOT NULL,
            costovta REAL NOT NULL CHECK (costovta >= 0),
            canti INTEGER NOT NULL CHECK (canti > 0),
            vriva REAL NOT NULL DEFAULT 0 CHECK (vriva >= 0),
            subtotal REAL NOT NULL CHECK (subtotal >= 0),
            vrtotal REAL NOT NULL CHECK (vrtotal >= 0),
            FOREIGN KEY (codclie) REFERENCES clientes (codclie)
                ON UPDATE CASCADE ON DELETE RESTRICT,
            FOREIGN KEY (codprod) REFERENCES productos (codprod)
                ON UPDATE CASCADE ON DELETE RESTRICT
        );
    """
}

VIEW_DEFINITIONS: dict[str, str] = {
    "vw_sales_with_clients": """
        CREATE VIEW IF NOT EXISTS vw_sales_with_clients AS
        SELECT v.id,
               v.fecha,
               v.codclie,
               c.nomclie,
               v.codprod,
               p.nomprod AS producto_catalogo,
               v.nomprod AS producto_vendido,
               v.canti,
               v.costovta,
               v.vriva,
               v.subtotal,
               v.vrtotal
        FROM ventas AS v
        JOIN clientes AS c ON c.codclie = v.codclie
        JOIN productos AS p ON p.codprod = v.codprod;
    """
}

INDEX_DEFINITIONS: dict[str, str] = {
    "idx_ventas_fecha": """
        CREATE INDEX IF NOT EXISTS idx_ventas_fecha
        ON ventas (fecha);
    """,
    "idx_ventas_codclie": """
        CREATE INDEX IF NOT EXISTS idx_ventas_codclie
        ON ventas (codclie);
    """,
    "idx_inventarios_stock": """
        CREATE INDEX IF NOT EXISTS idx_inventarios_stock
        ON inventarios (stock_minimo);
    """
}


def _execute_statements(cursor: sqlite3.Cursor, statements: Iterable[str]) -> None:
    """
    Purpose: Execute each SQL statement in order using the provided cursor.
    Args:
        cursor: Active SQLite cursor.
        statements: Iterable with raw SQL strings.
    """
    for statement in statements:
        cursor.execute(statement)


def _column_exists(cursor: sqlite3.Cursor, table: str, column: str) -> bool:
    cursor.execute(f"PRAGMA table_info({table})")
    return any(row[1] == column for row in cursor.fetchall())


def _apply_migrations(connection: sqlite3.Connection) -> None:
    cursor = connection.cursor()

    if _column_exists(cursor, "usuarios", "nomusu") and not _column_exists(cursor, "usuarios", "salt"):
        cursor.execute("ALTER TABLE usuarios ADD COLUMN salt TEXT")
        cursor.execute("UPDATE usuarios SET salt = '' WHERE salt IS NULL")

    if _column_exists(cursor, "inventarios", "codprod") and not _column_exists(cursor, "inventarios", "nomprod"):
        cursor.execute("ALTER TABLE inventarios ADD COLUMN nomprod TEXT")
        cursor.execute(
            """
            UPDATE inventarios
            SET nomprod = (
                SELECT nomprod FROM productos WHERE productos.codprod = inventarios.codprod
            )
            WHERE nomprod IS NULL
            """
        )


def initialize_database(db_path: Path = DB_PATH) -> None:
    """
    Purpose: Create all mandatory tables, indexes, and views for the project.
    Args:
        db_path: Optional override for the SQLite database path.
    """
    connection = sqlite3.connect(db_path)
    try:
        connection.execute("PRAGMA foreign_keys = ON;")
        cursor = connection.cursor()

        _execute_statements(cursor, TABLE_DEFINITIONS.values())
        _execute_statements(cursor, INDEX_DEFINITIONS.values())
        _execute_statements(cursor, VIEW_DEFINITIONS.values())
        _apply_migrations(connection)

        connection.commit()
    finally:
        connection.close()


def main() -> None:
    """
    Purpose: Provide a CLI entry point for initializing the database schema.
    """
    initialize_database()
    print(f"Database initialized at: {DB_PATH}")


if __name__ == "__main__":
    main()