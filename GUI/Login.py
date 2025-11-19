import tkinter as tk
from tkinter import messagebox
from modules.users import get_users

def login_window():
    """
    Purpose: Display login window and validate user credentials.
    """
    root = tk.Tk()
    root.title("Login")
    root.geometry("300x200")

    tk.Label(root, text="Username").pack(pady=5)
    username_entry = tk.Entry(root)
    username_entry.pack()

    tk.Label(root, text="Password").pack(pady=5)
    password_entry = tk.Entry(root, show="*")
    password_entry.pack()

    def validate_login():
        users = get_users()
        for u in users:
            if u[0] == username_entry.get() and u[1] == password_entry.get():
                messagebox.showinfo("Login", f"Welcome {u[0]} (Level {u[2]})")
                root.destroy()
                return
        messagebox.showerror("Login Failed", "Invalid credentials")

    tk.Button(root, text="Login", command=validate_login).pack(pady=20)

    root.mainloop()

