from tkinter import Tk, Frame, Label, Entry, Button, Listbox, END, messagebox
from Modules.Users import Users  # Assuming Users.py contains the necessary functions for user management

class UsersCRUD:
    def __init__(self, master):
        self.master = master
        self.master.title("Users CRUD")
        
        self.frame = Frame(self.master)
        self.frame.pack(padx=10, pady=10)

        self.label_id = Label(self.frame, text="User ID:")
        self.label_id.grid(row=0, column=0)
        self.entry_id = Entry(self.frame)
        self.entry_id.grid(row=0, column=1)

        self.label_name = Label(self.frame, text="Name:")
        self.label_name.grid(row=1, column=0)
        self.entry_name = Entry(self.frame)
        self.entry_name.grid(row=1, column=1)

        self.label_email = Label(self.frame, text="Email:")
        self.label_email.grid(row=2, column=0)
        self.entry_email = Entry(self.frame)
        self.entry_email.grid(row=2, column=1)

        self.button_create = Button(self.frame, text="Create", command=self.create_user)
        self.button_create.grid(row=3, column=0)

        self.button_read = Button(self.frame, text="Read", command=self.read_user)
        self.button_read.grid(row=3, column=1)

        self.button_update = Button(self.frame, text="Update", command=self.update_user)
        self.button_update.grid(row=4, column=0)

        self.button_delete = Button(self.frame, text="Delete", command=self.delete_user)
        self.button_delete.grid(row=4, column=1)

        self.listbox_users = Listbox(self.frame)
        self.listbox_users.grid(row=5, column=0, columnspan=2)

        self.load_users()

    def load_users(self):
        self.listbox_users.delete(0, END)
        users = Users.get_all_users()  # Assuming this function retrieves all users
        for user in users:
            self.listbox_users.insert(END, f"{user['id']} - {user['name']} - {user['email']}")

    def create_user(self):
        user_id = self.entry_id.get()
        name = self.entry_name.get()
        email = self.entry_email.get()
        if Users.create_user(user_id, name, email):  # Assuming this function creates a user
            messagebox.showinfo("Success", "User created successfully!")
            self.load_users()
        else:
            messagebox.showerror("Error", "Failed to create user.")

    def read_user(self):
        selected_user = self.listbox_users.curselection()
        if selected_user:
            user_info = self.listbox_users.get(selected_user)
            user_id = user_info.split(" - ")[0]
            user = Users.get_user(user_id)  # Assuming this function retrieves a user by ID
            if user:
                self.entry_id.delete(0, END)
                self.entry_id.insert(0, user['id'])
                self.entry_name.delete(0, END)
                self.entry_name.insert(0, user['name'])
                self.entry_email.delete(0, END)
                self.entry_email.insert(0, user['email'])

    def update_user(self):
        user_id = self.entry_id.get()
        name = self.entry_name.get()
        email = self.entry_email.get()
        if Users.update_user(user_id, name, email):  # Assuming this function updates a user
            messagebox.showinfo("Success", "User updated successfully!")
            self.load_users()
        else:
            messagebox.showerror("Error", "Failed to update user.")

    def delete_user(self):
        user_id = self.entry_id.get()
        if Users.delete_user(user_id):  # Assuming this function deletes a user
            messagebox.showinfo("Success", "User deleted successfully!")
            self.load_users()
        else:
            messagebox.showerror("Error", "Failed to delete user.")

if __name__ == "__main__":
    root = Tk()
    app = UsersCRUD(root)
    root.mainloop()