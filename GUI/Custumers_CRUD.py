"""Tkinter window to manage clientes with level-aware permissions."""

from __future__ import annotations

import tkinter as tk
from tkinter import END, Frame, Label, Listbox, Toplevel, messagebox

from GUI.permissions import allowed_actions
from Modules.Custumers import (
    create_client,
    delete_client,
    get_client,
    list_clients,
    update_client,
)


class ClientsWindow:
    """CRUD window bound to the clientes table."""

    def __init__(self, master: Toplevel, actions: list[str]) -> None:
        self.master = master
        self.actions = actions
        self.master.title("Clientes")

        container = Frame(master)
        container.pack(padx=12, pady=12, fill="both", expand=True)

        Label(container, text="Código").grid(row=0, column=0, sticky="w")
        self.entry_code = tk.Entry(container)
        self.entry_code.grid(row=0, column=1, sticky="ew")

        Label(container, text="Nombre").grid(row=1, column=0, sticky="w")
        self.entry_name = tk.Entry(container)
        self.entry_name.grid(row=1, column=1, sticky="ew")

        Label(container, text="Dirección").grid(row=2, column=0, sticky="w")
        self.entry_address = tk.Entry(container)
        self.entry_address.grid(row=2, column=1, sticky="ew")

        Label(container, text="Teléfono").grid(row=3, column=0, sticky="w")
        self.entry_phone = tk.Entry(container)
        self.entry_phone.grid(row=3, column=1, sticky="ew")

        Label(container, text="Ciudad").grid(row=4, column=0, sticky="w")
        self.entry_city = tk.Entry(container)
        self.entry_city.grid(row=4, column=1, sticky="ew")

        buttons = Frame(container)
        buttons.grid(row=5, column=0, columnspan=2, pady=8)

        self.btn_create = tk.Button(buttons, text="Crear", command=self.create_client)
        self.btn_create.grid(row=0, column=0, padx=4)
        self.btn_update = tk.Button(buttons, text="Actualizar", command=self.update_client)
        self.btn_update.grid(row=0, column=1, padx=4)
        self.btn_delete = tk.Button(buttons, text="Eliminar", command=self.delete_client)
        self.btn_delete.grid(row=0, column=2, padx=4)
        tk.Button(buttons, text="Limpiar", command=self.clear_form).grid(row=0, column=3, padx=4)

        Label(container, text="Clientes").grid(row=6, column=0, columnspan=2, sticky="w", pady=(10, 0))
        self.listbox = Listbox(container, height=10, width=50)
        self.listbox.grid(row=7, column=0, columnspan=2, sticky="nsew")
        self.listbox.bind("<<ListboxSelect>>", self.load_selection)

        container.columnconfigure(1, weight=1)
        container.rowconfigure(7, weight=1)

        self._apply_permissions()
        self.refresh_list()

    def _apply_permissions(self) -> None:
        if "create" not in self.actions:
            self.btn_create.config(state=tk.DISABLED)
        if "update" not in self.actions:
            self.btn_update.config(state=tk.DISABLED)
        if "delete" not in self.actions:
            self.btn_delete.config(state=tk.DISABLED)
        if "read" not in self.actions:
            self.listbox.config(state=tk.DISABLED)

    def refresh_list(self) -> None:
        self.listbox.delete(0, END)
        for client in list_clients():
            row = f"{client['codclie']} - {client['nomclie']} ({client['ciudad']})"
            self.listbox.insert(END, row)

    def _get_form_data(self) -> tuple[str, str, str, str, str]:
        return (
            self.entry_code.get().strip(),
            self.entry_name.get().strip(),
            self.entry_address.get().strip(),
            self.entry_phone.get().strip(),
            self.entry_city.get().strip(),
        )

    def create_client(self) -> None:
        if "create" not in self.actions:
            return
        codclie, nomclie, direc, telef, ciudad = self._get_form_data()
        if not codclie or not nomclie:
            messagebox.showerror("Clientes", "Código y nombre son obligatorios.")
            return
        ok, msg = create_client(codclie, nomclie, direc, telef, ciudad)
        if ok:
            messagebox.showinfo("Clientes", msg)
            self.refresh_list()
        else:
            messagebox.showerror("Clientes", msg)

    def update_client(self) -> None:
        if "update" not in self.actions:
            return
        codclie, nomclie, direc, telef, ciudad = self._get_form_data()
        if not codclie:
            messagebox.showerror("Clientes", "Debe seleccionar un cliente.")
            return
        ok, msg = update_client(codclie, nomclie, direc, telef, ciudad)
        if ok:
            messagebox.showinfo("Clientes", msg)
            self.refresh_list()
        else:
            messagebox.showerror("Clientes", msg)

    def delete_client(self) -> None:
        if "delete" not in self.actions:
            return
        codclie = self.entry_code.get().strip()
        if not codclie:
            messagebox.showerror("Clientes", "Debe seleccionar un cliente.")
            return
        ok, msg = delete_client(codclie)
        if ok:
            messagebox.showinfo("Clientes", msg)
            self.clear_form()
            self.refresh_list()
        else:
            messagebox.showerror("Clientes", msg)

    def load_selection(self, event) -> None:
        if "read" not in self.actions:
            return
        selection = event.widget.curselection()
        if not selection:
            return
        codclie = event.widget.get(selection[0]).split(" ")[0]
        client = get_client(codclie)
        if not client:
            return
        self.entry_code.delete(0, END)
        self.entry_code.insert(0, client["codclie"])
        self.entry_name.delete(0, END)
        self.entry_name.insert(0, client["nomclie"])
        self.entry_address.delete(0, END)
        self.entry_address.insert(0, client["direc"])
        self.entry_phone.delete(0, END)
        self.entry_phone.insert(0, client["telef"])
        self.entry_city.delete(0, END)
        self.entry_city.insert(0, client["ciudad"])

    def clear_form(self) -> None:
        for entry in (
            self.entry_code,
            self.entry_name,
            self.entry_address,
            self.entry_phone,
            self.entry_city,
        ):
            entry.delete(0, END)


def open_clients_window(parent, username: str, level: int) -> None:
    actions = allowed_actions("clients", level)
    if not actions:
        messagebox.showwarning("Clientes", "No tiene permisos para este módulo.")
        return
    window = Toplevel(parent)
    ClientsWindow(window, actions)