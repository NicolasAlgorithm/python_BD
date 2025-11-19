import tkinter as tk
from tkinter import messagebox

from Modules.Users import UsersCRUD


def login_window():
    """Display the login window and return (username, level) when successful."""

    root = tk.Tk()
    root.title("Login")
    root.geometry("320x200")

    result = {"username": None, "level": None}

    tk.Label(root, text="Usuario").pack(pady=5)
    username_entry = tk.Entry(root)
    username_entry.pack()

    tk.Label(root, text="Contraseña").pack(pady=5)
    password_entry = tk.Entry(root, show="*")
    password_entry.pack()

    def validate_login():
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        if not username or not password:
            messagebox.showerror("Login", "Debe ingresar usuario y contraseña.")
            return

        users = UsersCRUD()
        ok, msg = users.verify_user(username, password)
        if ok:
            level = users.get_user_level(username)
            result["username"] = username
            result["level"] = level
            root.destroy()
        else:
            messagebox.showerror("Login", msg)

    tk.Button(root, text="Ingresar", command=validate_login).pack(pady=20)

    root.mainloop()

    return result["username"], result["level"]

