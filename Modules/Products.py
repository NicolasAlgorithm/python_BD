from database.connection import get_connection

class ProductsCRUD:

    #/***************************************************************************
    #*Nombre de función o método: create_product
    #*Propósito: Crear un nuevo producto en la tabla inventarios
    #****************************************************************************/
    def create_product(self, codprod, nomprod, cantidad, stock, costovta):
        conn = get_connection()
        cursor = conn.cursor()

        # Validación de existencia
        cursor.execute("SELECT codprod FROM inventarios WHERE codprod = ?", (codprod,))
        if cursor.fetchone():
            conn.close()
            return False, "El producto ya existe."

        cursor.execute("""
            INSERT INTO inventarios(codprod, nomprod, cantidad, stock, costovta)
            VALUES (?, ?, ?, ?, ?)
        """, (codprod, nomprod, cantidad, stock, costovta))

        conn.commit()
        conn.close()
        return True, "Producto creado exitosamente."

    #/***************************************************************************
    #*Nombre de función o método: read_product
    #*Propósito: Consultar un producto por su código
    #****************************************************************************/
    def read_product(self, codprod):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM inventarios WHERE codprod = ?", (codprod,))
        data = cursor.fetchone()

        conn.close()
        return data

    #/***************************************************************************
    #*Nombre de función o método: update_product
    #*Propósito: Actualizar un producto existente
    #****************************************************************************/
    def update_product(self, codprod, nomprod, cantidad, stock, costovta):
        conn = get_connection()
        cursor = conn.cursor()

        # Verificar que exista
        cursor.execute("SELECT codprod FROM inventarios WHERE codprod = ?", (codprod,))
        if not cursor.fetchone():
            conn.close()
            return False, "El producto no existe."

        cursor.execute("""
            UPDATE inventarios
            SET nomprod=?, cantidad=?, stock=?, costovta=?
            WHERE codprod=?
        """, (nomprod, cantidad, stock, costovta, codprod))

        conn.commit()
        conn.close()
        return True, "Producto actualizado correctamente."

    #//****************************************************************************
    #//Nombre de función o método: delete_product
    #Propósito: Eliminar un producto existente
    #*/***************************************************************************/
    def delete_product(self, codprod):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT codprod FROM inventarios WHERE codprod = ?", (codprod,))
        if not cursor.fetchone():
            conn.close()
            return False, "El producto no existe."

        cursor.execute("DELETE FROM inventarios WHERE codprod = ?", (codprod,))
        conn.commit()
        conn.close()
        return True, "Producto eliminado."
