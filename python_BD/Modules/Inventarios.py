class Inventory:
    def __init__(self, id, name, quantity, price):
        self.id = id
        self.name = name
        self.quantity = quantity
        self.price = price

class InventoryManager:
    def __init__(self):
        self.inventories = []

    def create_inventory(self, id, name, quantity, price):
        new_inventory = Inventory(id, name, quantity, price)
        self.inventories.append(new_inventory)

    def read_inventory(self, id):
        for inventory in self.inventories:
            if inventory.id == id:
                return vars(inventory)
        return None

    def update_inventory(self, id, name=None, quantity=None, price=None):
        for inventory in self.inventories:
            if inventory.id == id:
                if name is not None:
                    inventory.name = name
                if quantity is not None:
                    inventory.quantity = quantity
                if price is not None:
                    inventory.price = price
                return True
        return False

    def delete_inventory(self, id):
        for inventory in self.inventories:
            if inventory.id == id:
                self.inventories.remove(inventory)
                return True
        return False

    def list_inventories(self):
        return [vars(inventory) for inventory in self.inventories]