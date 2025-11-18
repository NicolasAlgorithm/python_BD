from database.connection import get_connection

class ProvidersCRUD:

    #Nombre: create_provider
    #Propósito: Crear un proveedor con su producto y costo
    def create_provider(self, idprov, codprod, costo):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT idprov FROM proveedores WHERE idprov = ?", (idprov,))
        if cursor.fetchone():
            conn.close()
            return False, "El proveedor ya existe."

        cursor.execute("""
            INSERT INTO proveedores(idprov, codprod, costo)
            VALUES (?, ?, ?)
        """, (idprov, codprod, costo))

        conn.commit()
        conn.close()
        return True, "Proveedor creado."

    #Nombre: read_provider
    #Propósito: Leer proveedor por ID
    def read_provider(self, idprov):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM proveedores WHERE idprov = ?", (idprov,))
        data = cursor.fetchone()

        conn.close()
        return data

    #Nombre: update_provider
    #Propósito: Actualizar proveedor existente
    def update_provider(self, idprov, codprod, costo):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT idprov FROM proveedores WHERE idprov = ?", (idprov,))
        if not cursor.fetchone():
            conn.close()
            return False, "Proveedor no existe."

        cursor.execute("""
            UPDATE proveedores
            SET codprod=?, costo=?
            WHERE idprov=?
        """, (codprod, costo, idprov))

        conn.commit()
        conn.close()
        return True, "Proveedor actualizado."

    #Nombre: delete_provider
    #Propósito: Eliminar proveedor
    def delete_provider(self, idprov):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT idprov FROM proveedores WHERE idprov = ?", (idprov,))
        if not cursor.fetchone():
            conn.close()
            return False, "Proveedor no existe."

        cursor.execute("DELETE FROM proveedores WHERE idprov = ?", (idprov,))
        conn.commit()
        conn.close()
        return True, "Proveedor eliminado."