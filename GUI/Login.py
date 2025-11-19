import tkinter as tk
from tkinter import messagebox

from Modules.Users import UsersCRUD

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
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        if not username or not password:
            messagebox.showerror("Login Failed", "Debe ingresar usuario y contraseña.")
            return

        users = UsersCRUD()
        ok, msg = users.verify_user(username, password)
        if ok:
            level = users.get_user_level(username)
            messagebox.showinfo(
                "Login",
                f"Bienvenido {username} (Nivel {level})",
            )
            root.destroy()
        else:
            messagebox.showerror("Login Failed", msg)

    tk.Button(root, text="Login", command=validate_login).pack(pady=20)

    root.mainloop()

