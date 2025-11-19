from tkinter import Tk, Frame, Label, Entry, Button, Listbox, END, Scrollbar, messagebox
from Modules.Sales import Sales  # Assuming Sales.py contains the necessary functions for CRUD operations

class SalesCRUD:
    def __init__(self, master):
        self.master = master
        self.master.title("Sales Management")
        self.frame = Frame(self.master)
        self.frame.pack(padx=10, pady=10)

        self.label_id = Label(self.frame, text="Sale ID:")
        self.label_id.grid(row=0, column=0)
        self.entry_id = Entry(self.frame)
        self.entry_id.grid(row=0, column=1)

        self.label_product = Label(self.frame, text="Product:")
        self.label_product.grid(row=1, column=0)
        self.entry_product = Entry(self.frame)
        self.entry_product.grid(row=1, column=1)

        self.label_quantity = Label(self.frame, text="Quantity:")
        self.label_quantity.grid(row=2, column=0)
        self.entry_quantity = Entry(self.frame)
        self.entry_quantity.grid(row=2, column=1)

        self.label_price = Label(self.frame, text="Price:")
        self.label_price.grid(row=3, column=0)
        self.entry_price = Entry(self.frame)
        self.entry_price.grid(row=3, column=1)

        self.button_create = Button(self.frame, text="Create", command=self.create_sale)
        self.button_create.grid(row=4, column=0, pady=5)

        self.button_read = Button(self.frame, text="Read", command=self.read_sales)
        self.button_read.grid(row=4, column=1, pady=5)

        self.button_update = Button(self.frame, text="Update", command=self.update_sale)
        self.button_update.grid(row=5, column=0, pady=5)

        self.button_delete = Button(self.frame, text="Delete", command=self.delete_sale)
        self.button_delete.grid(row=5, column=1, pady=5)

        self.listbox = Listbox(self.frame, width=50)
        self.listbox.grid(row=6, column=0, columnspan=2)

        self.scrollbar = Scrollbar(self.frame)
        self.scrollbar.grid(row=6, column=2, sticky='ns')
        self.listbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.listbox.yview)

        self.load_sales()

    def create_sale(self):
        sale_id = self.entry_id.get()
        product = self.entry_product.get()
        quantity = self.entry_quantity.get()
        price = self.entry_price.get()
        if Sales.create_sale(sale_id, product, quantity, price):
            messagebox.showinfo("Success", "Sale created successfully!")
            self.load_sales()
        else:
            messagebox.showerror("Error", "Failed to create sale.")

    def read_sales(self):
        self.load_sales()

    def update_sale(self):
        selected_sale = self.listbox.curselection()
        if selected_sale:
            sale_id = self.entry_id.get()
            product = self.entry_product.get()
            quantity = self.entry_quantity.get()
            price = self.entry_price.get()
            if Sales.update_sale(sale_id, product, quantity, price):
                messagebox.showinfo("Success", "Sale updated successfully!")
                self.load_sales()
            else:
                messagebox.showerror("Error", "Failed to update sale.")
        else:
            messagebox.showwarning("Warning", "Select a sale to update.")

    def delete_sale(self):
        selected_sale = self.listbox.curselection()
        if selected_sale:
            sale_id = self.listbox.get(selected_sale).split()[0]  # Assuming the first part is the sale ID
            if Sales.delete_sale(sale_id):
                messagebox.showinfo("Success", "Sale deleted successfully!")
                self.load_sales()
            else:
                messagebox.showerror("Error", "Failed to delete sale.")
        else:
            messagebox.showwarning("Warning", "Select a sale to delete.")

    def load_sales(self):
        self.listbox.delete(0, END)
        sales_list = Sales.get_all_sales()
        for sale in sales_list:
            self.listbox.insert(END, f"{sale['id']} - {sale['product']} - {sale['quantity']} - {sale['price']}")

if __name__ == "__main__":
    root = Tk()
    sales_crud = SalesCRUD(root)
    root.mainloop()