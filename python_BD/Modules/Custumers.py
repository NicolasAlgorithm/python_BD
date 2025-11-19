class Customer:
    def __init__(self, customer_id, name, email, phone):
        self.customer_id = customer_id
        self.name = name
        self.email = email
        self.phone = phone

class CustomerManager:
    def __init__(self):
        self.customers = {}

    def create_customer(self, customer_id, name, email, phone):
        if customer_id in self.customers:
            raise ValueError("Customer ID already exists.")
        self.customers[customer_id] = Customer(customer_id, name, email, phone)

    def read_customer(self, customer_id):
        return self.customers.get(customer_id, None)

    def update_customer(self, customer_id, name=None, email=None, phone=None):
        customer = self.read_customer(customer_id)
        if not customer:
            raise ValueError("Customer not found.")
        if name:
            customer.name = name
        if email:
            customer.email = email
        if phone:
            customer.phone = phone

    def delete_customer(self, customer_id):
        if customer_id not in self.customers:
            raise ValueError("Customer not found.")
        del self.customers[customer_id]