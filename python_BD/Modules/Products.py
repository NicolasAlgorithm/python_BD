class Product:
    def __init__(self, product_id, name, description, price, quantity):
        self.product_id = product_id
        self.name = name
        self.description = description
        self.price = price
        self.quantity = quantity

class ProductManager:
    def __init__(self):
        self.products = []

    def create_product(self, product_id, name, description, price, quantity):
        new_product = Product(product_id, name, description, price, quantity)
        self.products.append(new_product)

    def read_product(self, product_id):
        for product in self.products:
            if product.product_id == product_id:
                return vars(product)
        return None

    def update_product(self, product_id, name=None, description=None, price=None, quantity=None):
        for product in self.products:
            if product.product_id == product_id:
                if name is not None:
                    product.name = name
                if description is not None:
                    product.description = description
                if price is not None:
                    product.price = price
                if quantity is not None:
                    product.quantity = quantity
                return True
        return False

    def delete_product(self, product_id):
        for product in self.products:
            if product.product_id == product_id:
                self.products.remove(product)
                return True
        return False

    def list_products(self):
        return [vars(product) for product in self.products]