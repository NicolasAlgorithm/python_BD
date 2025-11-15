import sqlite3

def init_db():
    conn = sqlite3.connect("db/app.db")
    cursor = conn.cursor()

    # Tabla de usuarios como ejemplo inicial
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Usuarios (
        nomusu TEXT PRIMARY KEY,
        clave TEXT NOT NULL,
        nivel INTEGER NOT NULL
    )
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully")
