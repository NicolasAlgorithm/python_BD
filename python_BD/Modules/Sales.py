class Sale:
    def __init__(self, sale_id, product_id, customer_id, quantity, total_price):
        self.sale_id = sale_id
        self.product_id = product_id
        self.customer_id = customer_id
        self.quantity = quantity
        self.total_price = total_price

class SalesManager:
    def __init__(self):
        self.sales = []

    def create_sale(self, sale):
        self.sales.append(sale)

    def read_sales(self):
        return self.sales

    def update_sale(self, sale_id, updated_sale):
        for index, sale in enumerate(self.sales):
            if sale.sale_id == sale_id:
                self.sales[index] = updated_sale
                return True
        return False

    def delete_sale(self, sale_id):
        for index, sale in enumerate(self.sales):
            if sale.sale_id == sale_id:
                del self.sales[index]
                return True
        return False