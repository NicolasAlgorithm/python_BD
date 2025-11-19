from tkinter import *
from tkinter import messagebox
from Modules.Providers import Provider  # Assuming Provider is a class in Providers.py

class ProvidersCRUD:
    def __init__(self, master):
        self.master = master
        self.master.title("Providers CRUD")
        
        self.label_id = Label(master, text="Provider ID:")
        self.label_id.grid(row=0, column=0)
        self.entry_id = Entry(master)
        self.entry_id.grid(row=0, column=1)

        self.label_name = Label(master, text="Provider Name:")
        self.label_name.grid(row=1, column=0)
        self.entry_name = Entry(master)
        self.entry_name.grid(row=1, column=1)

        self.button_create = Button(master, text="Create", command=self.create_provider)
        self.button_create.grid(row=2, column=0)

        self.button_read = Button(master, text="Read", command=self.read_provider)
        self.button_read.grid(row=2, column=1)

        self.button_update = Button(master, text="Update", command=self.update_provider)
        self.button_update.grid(row=2, column=2)

        self.button_delete = Button(master, text="Delete", command=self.delete_provider)
        self.button_delete.grid(row=2, column=3)

    def create_provider(self):
        provider_name = self.entry_name.get()
        if provider_name:
            # Logic to create a provider
            messagebox.showinfo("Success", f"Provider '{provider_name}' created.")
        else:
            messagebox.showwarning("Input Error", "Please enter a provider name.")

    def read_provider(self):
        provider_id = self.entry_id.get()
        if provider_id:
            # Logic to read a provider
            messagebox.showinfo("Provider Info", f"Details for provider ID: {provider_id}")
        else:
            messagebox.showwarning("Input Error", "Please enter a provider ID.")

    def update_provider(self):
        provider_id = self.entry_id.get()
        provider_name = self.entry_name.get()
        if provider_id and provider_name:
            # Logic to update a provider
            messagebox.showinfo("Success", f"Provider ID '{provider_id}' updated to '{provider_name}'.")
        else:
            messagebox.showwarning("Input Error", "Please enter both provider ID and name.")

    def delete_provider(self):
        provider_id = self.entry_id.get()
        if provider_id:
            # Logic to delete a provider
            messagebox.showinfo("Success", f"Provider ID '{provider_id}' deleted.")
        else:
            messagebox.showwarning("Input Error", "Please enter a provider ID.")

if __name__ == "__main__":
    root = Tk()
    providers_crud = ProvidersCRUD(root)
    root.mainloop()