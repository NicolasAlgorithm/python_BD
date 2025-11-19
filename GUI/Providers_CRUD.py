"""Providers window bound to Providers CRUD with security levels."""

from __future__ import annotations

import tkinter as tk
from tkinter import END, Frame, Label, Listbox, Toplevel, messagebox

from GUI.permissions import allowed_actions
from Modules.Providers import ProvidersCRUD


class ProvidersWindow:
    """CRUD interface for proveedores table respecting permissions."""

    def __init__(self, master: Toplevel, actions: list[str]) -> None:
        self.master = master
        self.actions = actions
        self.service = ProvidersCRUD()

        self.master.title("Proveedores")

        container = Frame(master)
        container.pack(padx=12, pady=12, fill="both", expand=True)

        Label(container, text="ID proveedor").grid(row=0, column=0, sticky="w")
        self.entry_id = tk.Entry(container)
        self.entry_id.grid(row=0, column=1, sticky="ew")

        Label(container, text="Producto asociado").grid(row=1, column=0, sticky="w")
        self.entry_product = tk.Entry(container)
        self.entry_product.grid(row=1, column=1, sticky="ew")

        Label(container, text="Descripción").grid(row=2, column=0, sticky="w")
        self.entry_description = tk.Entry(container)
        self.entry_description.grid(row=2, column=1, sticky="ew")

        Label(container, text="Costo").grid(row=3, column=0, sticky="w")
        self.entry_cost = tk.Entry(container)
        self.entry_cost.grid(row=3, column=1, sticky="ew")

        Label(container, text="Dirección").grid(row=4, column=0, sticky="w")
        self.entry_address = tk.Entry(container)
        self.entry_address.grid(row=4, column=1, sticky="ew")

        Label(container, text="Teléfono").grid(row=5, column=0, sticky="w")
        self.entry_phone = tk.Entry(container)
        self.entry_phone.grid(row=5, column=1, sticky="ew")

        buttons = Frame(container)
        buttons.grid(row=6, column=0, columnspan=2, pady=8)

        self.btn_create = tk.Button(buttons, text="Crear", command=self.create_provider)
        self.btn_create.grid(row=0, column=0, padx=4)
        self.btn_update = tk.Button(buttons, text="Actualizar", command=self.update_provider)
        self.btn_update.grid(row=0, column=1, padx=4)
        self.btn_delete = tk.Button(buttons, text="Eliminar", command=self.delete_provider)
        self.btn_delete.grid(row=0, column=2, padx=4)
        tk.Button(buttons, text="Limpiar", command=self.clear_form).grid(row=0, column=3, padx=4)

        Label(container, text="Proveedores").grid(row=7, column=0, columnspan=2, sticky="w", pady=(10, 0))
        self.listbox = Listbox(container, height=10, width=50)
        self.listbox.grid(row=8, column=0, columnspan=2, sticky="nsew")
        self.listbox.bind("<<ListboxSelect>>", self.load_selection)

        container.columnconfigure(1, weight=1)
        container.rowconfigure(8, weight=1)

        self._apply_permissions()
        self.refresh_list()

    def _apply_permissions(self) -> None:
        if "create" not in self.actions:
            self.btn_create.config(state=tk.DISABLED)
        if "update" not in self.actions:
            self.btn_update.config(state=tk.DISABLED)
        if "delete" not in self.actions:
            self.btn_delete.config(state=tk.DISABLED)

    def refresh_list(self) -> None:
        self.listbox.delete(0, END)
        for provider in self.service.list_providers():
            row = f"{provider['idprov']} - {provider['descripcion']} (Prod: {provider['codprod']})"
            self.listbox.insert(END, row)

    def _get_form(self):
        return (
            self.entry_id.get().strip(),
            self.entry_product.get().strip(),
            self.entry_description.get().strip(),
            self.entry_cost.get().strip(),
            self.entry_address.get().strip(),
            self.entry_phone.get().strip(),
        )

    def create_provider(self) -> None:
        if "create" not in self.actions:
            return
        idprov, codprod, descripcion, costo, direccion, telefono = self._get_form()
        if not idprov or not codprod:
            messagebox.showerror("Proveedores", "ID y producto son obligatorios.")
            return
        try:
            costo_value = float(costo or 0)
        except ValueError:
            messagebox.showerror("Proveedores", "Costo inválido.")
            return
        ok, msg = self.service.create_provider(idprov, codprod, descripcion, costo_value, direccion, telefono)
        if ok:
            messagebox.showinfo("Proveedores", msg)
            self.refresh_list()
        else:
            messagebox.showerror("Proveedores", msg)

    def update_provider(self) -> None:
        if "update" not in self.actions:
            messagebox.showerror("Proveedores", "No tiene permiso para actualizar (nivel insuficiente).")
            return
        idprov, codprod, descripcion, costo, direccion, telefono = self._get_form()
        if not idprov:
            messagebox.showerror("Proveedores", "Seleccione un proveedor.")
            return
        try:
            costo_value = float(costo or 0)
        except ValueError:
            messagebox.showerror("Proveedores", "Costo inválido.")
            return
        ok, msg = self.service.update_provider(idprov, codprod, descripcion, costo_value, direccion, telefono)
        if ok:
            messagebox.showinfo("Proveedores", msg)
            self.refresh_list()
        else:
            messagebox.showerror("Proveedores", msg)

    def delete_provider(self) -> None:
        if "delete" not in self.actions:
            messagebox.showerror("Proveedores", "No tiene permiso para eliminar (nivel insuficiente).")
            return
        idprov = self.entry_id.get().strip()
        if not idprov:
            messagebox.showerror("Proveedores", "Seleccione un proveedor.")
            return
        ok, msg = self.service.delete_provider(idprov)
        if ok:
            messagebox.showinfo("Proveedores", msg)
            self.clear_form()
            self.refresh_list()
        else:
            messagebox.showerror("Proveedores", msg)

    def load_selection(self, event) -> None:
        selection = event.widget.curselection()
        if not selection:
            return
        idprov = event.widget.get(selection[0]).split(" ")[0]
        provider = self.service.read_provider(idprov)
        if not provider:
            return
        self.entry_id.delete(0, END)
        self.entry_id.insert(0, provider["idprov"])
        self.entry_product.delete(0, END)
        self.entry_product.insert(0, provider["codprod"])
        self.entry_description.delete(0, END)
        self.entry_description.insert(0, provider["descripcion"])
        self.entry_cost.delete(0, END)
        self.entry_cost.insert(0, provider["costo"])
        self.entry_address.delete(0, END)
        self.entry_address.insert(0, provider["direccion"])
        self.entry_phone.delete(0, END)
        self.entry_phone.insert(0, provider["telefono"])

    def clear_form(self) -> None:
        for entry in (
            self.entry_id,
            self.entry_product,
            self.entry_description,
            self.entry_cost,
            self.entry_address,
            self.entry_phone,
        ):
            entry.delete(0, END)


def open_providers_window(parent, username: str, level: int) -> None:
    actions = allowed_actions("providers", level)
    if not actions:
        messagebox.showwarning("Proveedores", "No tiene permisos para este módulo.")
        return
    window = Toplevel(parent)
    ProvidersWindow(window, actions)