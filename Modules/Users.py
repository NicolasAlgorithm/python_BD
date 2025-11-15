from db.connection import get_connection

def create_user(nomusu, clave, nivel):
    """
    Purpose: Insert a new user into the database.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Usuarios (nomusu, clave, nivel) VALUES (?, ?, ?)", 
                   (nomusu, clave, nivel))
    conn.commit()
    conn.close()

def get_users():
    """
    Purpose: Retrieve all users from the database.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Usuarios")
    rows = cursor.fetchall()
    conn.close()
    return rows
