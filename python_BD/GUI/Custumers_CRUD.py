from tkinter import *
from tkinter import messagebox
from Modules.Custumers import CustumerManager  # Assuming CustumerManager handles CRUD operations

class CustumersCRUD:
    def __init__(self, master):
        self.master = master
        self.master.title("Customers CRUD")
        
        self.label_id = Label(master, text="Customer ID:")
        self.label_id.grid(row=0, column=0)
        self.entry_id = Entry(master)
        self.entry_id.grid(row=0, column=1)

        self.label_name = Label(master, text="Customer Name:")
        self.label_name.grid(row=1, column=0)
        self.entry_name = Entry(master)
        self.entry_name.grid(row=1, column=1)

        self.label_email = Label(master, text="Customer Email:")
        self.label_email.grid(row=2, column=0)
        self.entry_email = Entry(master)
        self.entry_email.grid(row=2, column=1)

        self.button_create = Button(master, text="Create", command=self.create_customer)
        self.button_create.grid(row=3, column=0)

        self.button_read = Button(master, text="Read", command=self.read_customer)
        self.button_read.grid(row=3, column=1)

        self.button_update = Button(master, text="Update", command=self.update_customer)
        self.button_update.grid(row=3, column=2)

        self.button_delete = Button(master, text="Delete", command=self.delete_customer)
        self.button_delete.grid(row=3, column=3)

    def create_customer(self):
        name = self.entry_name.get()
        email = self.entry_email.get()
        if CustumerManager.create(name, email):
            messagebox.showinfo("Success", "Customer created successfully!")
        else:
            messagebox.showerror("Error", "Failed to create customer.")

    def read_customer(self):
        customer_id = self.entry_id.get()
        customer = CustumerManager.read(customer_id)
        if customer:
            self.entry_name.delete(0, END)
            self.entry_name.insert(0, customer['name'])
            self.entry_email.delete(0, END)
            self.entry_email.insert(0, customer['email'])
        else:
            messagebox.showerror("Error", "Customer not found.")

    def update_customer(self):
        customer_id = self.entry_id.get()
        name = self.entry_name.get()
        email = self.entry_email.get()
        if CustumerManager.update(customer_id, name, email):
            messagebox.showinfo("Success", "Customer updated successfully!")
        else:
            messagebox.showerror("Error", "Failed to update customer.")

    def delete_customer(self):
        customer_id = self.entry_id.get()
        if CustumerManager.delete(customer_id):
            messagebox.showinfo("Success", "Customer deleted successfully!")
        else:
            messagebox.showerror("Error", "Failed to delete customer.")

if __name__ == "__main__":
    root = Tk()
    app = CustumersCRUD(root)
    root.mainloop()