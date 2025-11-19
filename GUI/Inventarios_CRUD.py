from tkinter import Tk, Frame, Label, Entry, Button, Listbox, END, messagebox
from Modules.Inventarios import Inventarios  # Assuming this module contains the necessary functions

class InventariosCRUD:
    def __init__(self, master):
        self.master = master
        self.master.title("Inventarios CRUD")
        
        self.frame = Frame(self.master)
        self.frame.pack(padx=10, pady=10)

        self.label_id = Label(self.frame, text="ID:")
        self.label_id.grid(row=0, column=0)
        self.entry_id = Entry(self.frame)
        self.entry_id.grid(row=0, column=1)

        self.label_name = Label(self.frame, text="Name:")
        self.label_name.grid(row=1, column=0)
        self.entry_name = Entry(self.frame)
        self.entry_name.grid(row=1, column=1)

        self.label_quantity = Label(self.frame, text="Quantity:")
        self.label_quantity.grid(row=2, column=0)
        self.entry_quantity = Entry(self.frame)
        self.entry_quantity.grid(row=2, column=1)

        self.listbox = Listbox(self.frame)
        self.listbox.grid(row=3, column=0, columnspan=2)

        self.button_create = Button(self.frame, text="Create", command=self.create)
        self.button_create.grid(row=4, column=0)

        self.button_read = Button(self.frame, text="Read", command=self.read)
        self.button_read.grid(row=4, column=1)

        self.button_update = Button(self.frame, text="Update", command=self.update)
        self.button_update.grid(row=5, column=0)

        self.button_delete = Button(self.frame, text="Delete", command=self.delete)
        self.button_delete.grid(row=5, column=1)

        self.load_data()

    def load_data(self):
        self.listbox.delete(0, END)
        for item in Inventarios.get_all():  # Assuming this method retrieves all inventory items
            self.listbox.insert(END, item)

    def create(self):
        name = self.entry_name.get()
        quantity = self.entry_quantity.get()
        if Inventarios.create(name, quantity):  # Assuming this method creates a new inventory item
            messagebox.showinfo("Success", "Item created successfully!")
            self.load_data()
        else:
            messagebox.showerror("Error", "Failed to create item.")

    def read(self):
        selected_item = self.listbox.curselection()
        if selected_item:
            item = self.listbox.get(selected_item)
            self.entry_id.delete(0, END)
            self.entry_id.insert(0, item.id)  # Assuming item has an id attribute
            self.entry_name.delete(0, END)
            self.entry_name.insert(0, item.name)  # Assuming item has a name attribute
            self.entry_quantity.delete(0, END)
            self.entry_quantity.insert(0, item.quantity)  # Assuming item has a quantity attribute

    def update(self):
        id = self.entry_id.get()
        name = self.entry_name.get()
        quantity = self.entry_quantity.get()
        if Inventarios.update(id, name, quantity):  # Assuming this method updates an inventory item
            messagebox.showinfo("Success", "Item updated successfully!")
            self.load_data()
        else:
            messagebox.showerror("Error", "Failed to update item.")

    def delete(self):
        selected_item = self.listbox.curselection()
        if selected_item:
            item = self.listbox.get(selected_item)
            if Inventarios.delete(item.id):  # Assuming this method deletes an inventory item by id
                messagebox.showinfo("Success", "Item deleted successfully!")
                self.load_data()
            else:
                messagebox.showerror("Error", "Failed to delete item.")

if __name__ == "__main__":
    root = Tk()
    app = InventariosCRUD(root)
    root.mainloop()