import tkinter as tk
from tkinter import END, Frame, Label, Listbox, Spinbox, Toplevel, messagebox

from GUI.permissions import allowed_actions
from Modules.Users import UsersCRUD


class UsersWindow:
    """Ventana CRUD para administrar usuarios respetando privilegios."""

    def __init__(self, master: Toplevel, actions: list[str]) -> None:
        self._service = UsersCRUD()
        self.master = master
        self.actions = actions
        self.master.title("Administrar usuarios")

        container = Frame(self.master)
        container.pack(padx=12, pady=12, fill="both", expand=True)

        Label(container, text="Usuario").grid(row=0, column=0, sticky="w")
        self.entry_username = tk.Entry(container)
        self.entry_username.grid(row=0, column=1, sticky="ew")

        Label(container, text="Contraseña").grid(row=1, column=0, sticky="w")
        self.entry_password = tk.Entry(container, show="*")
        self.entry_password.grid(row=1, column=1, sticky="ew")

        Label(container, text="Nivel (1-3)").grid(row=2, column=0, sticky="w")
        self.spin_level = Spinbox(container, from_=1, to=3, width=5)
        self.spin_level.grid(row=2, column=1, sticky="w")

        buttons = Frame(container)
        buttons.grid(row=3, column=0, columnspan=2, pady=8)

        self.btn_create = tk.Button(buttons, text="Crear", command=self.create_user)
        self.btn_create.grid(row=0, column=0, padx=4)
        self.btn_update = tk.Button(buttons, text="Actualizar", command=self.update_user)
        self.btn_update.grid(row=0, column=1, padx=4)
        self.btn_delete = tk.Button(buttons, text="Eliminar", command=self.delete_user)
        self.btn_delete.grid(row=0, column=2, padx=4)

        Label(container, text="Usuarios registrados").grid(row=4, column=0, columnspan=2, sticky="w", pady=(10, 0))
        self.listbox_users = Listbox(container, width=40, height=8)
        self.listbox_users.grid(row=5, column=0, columnspan=2, sticky="nsew")
        self.listbox_users.bind("<<ListboxSelect>>", self.load_selection)

        container.columnconfigure(1, weight=1)
        container.rowconfigure(5, weight=1)

        self._apply_permissions()
        self.refresh_users()

    def _apply_permissions(self) -> None:
        if "create" not in self.actions:
            self.btn_create.config(state=tk.DISABLED)
        if "update" not in self.actions:
            self.btn_update.config(state=tk.DISABLED)
        if "delete" not in self.actions:
            self.btn_delete.config(state=tk.DISABLED)

    def refresh_users(self) -> None:
        self.listbox_users.delete(0, END)
        for user in self._service.list_users():
            self.listbox_users.insert(END, f"{user['nomusu']} (Nivel {user['nivel']})")

    def _get_form_data(self) -> tuple[str, str, int]:
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()
        level = int(self.spin_level.get())
        return username, password, level

    def create_user(self) -> None:
        if "create" not in self.actions:
            return
        username, password, level = self._get_form_data()
        if not username or not password:
            messagebox.showerror("Usuarios", "Usuario y contraseña son obligatorios.")
            return
        ok, msg = self._service.create_user(username, password, level)
        if ok:
            messagebox.showinfo("Usuarios", msg)
            self.entry_password.delete(0, END)
            self.refresh_users()
        else:
            messagebox.showerror("Usuarios", msg)

    def update_user(self) -> None:
        if "update" not in self.actions:
            messagebox.showerror("Usuarios", "No tiene permiso para actualizar (nivel insuficiente).")
            return
        username, password, level = self._get_form_data()
        if not username:
            messagebox.showerror("Usuarios", "Debe seleccionar o ingresar un usuario.")
            return
        password_arg = password or None
        ok, msg = self._service.update_user(username, password_arg, level)
        if ok:
            messagebox.showinfo("Usuarios", msg)
            self.entry_password.delete(0, END)
            self.refresh_users()
        else:
            messagebox.showerror("Usuarios", msg)

    def delete_user(self) -> None:
        if "delete" not in self.actions:
            messagebox.showerror("Usuarios", "No tiene permiso para eliminar (nivel insuficiente).")
            return
        username = self.entry_username.get().strip()
        if not username:
            messagebox.showerror("Usuarios", "Debe elegir un usuario para eliminar.")
            return
        ok, msg = self._service.delete_user(username)
        if ok:
            messagebox.showinfo("Usuarios", msg)
            self.entry_username.delete(0, END)
            self.entry_password.delete(0, END)
            self.refresh_users()
        else:
            messagebox.showerror("Usuarios", msg)

    def load_selection(self, event) -> None:
        selection = event.widget.curselection()
        if not selection:
            return
        value = event.widget.get(selection[0])
        username = value.split(" ")[0]
        user = self._service.read_user(username)
        if not user:
            return
        self.entry_username.delete(0, END)
        self.entry_username.insert(0, user["nomusu"])
        self.spin_level.delete(0, END)
        self.spin_level.insert(0, user["nivel"])
        self.entry_password.delete(0, END)


def open_users_window(parent, username: str, level: int) -> None:
    actions = allowed_actions("users", level)
    if not actions:
        messagebox.showwarning("Usuarios", "No tiene permisos para usar este módulo.")
        return
    window = Toplevel(parent)
    UsersWindow(window, actions)