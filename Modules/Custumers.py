from DB.connection import get_connection

def create_client(codclie, nomclie, direc, telef, ciudad):
    """
    Purpose: Insert a new client into the database.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Clientes (codclie, nomclie, direc, telef, ciudad) VALUES (?, ?, ?, ?, ?)", 
                   (codclie, nomclie, direc, telef, ciudad))
    conn.commit()
    conn.close()
