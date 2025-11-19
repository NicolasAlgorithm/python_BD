"""Products window connected to Products CRUD with role-based permissions."""

from __future__ import annotations

import tkinter as tk
from tkinter import END, Frame, Label, Listbox, Toplevel, messagebox

from GUI.permissions import allowed_actions
from Modules.Products import ProductsCRUD


class ProductsWindow:
    """Allow users to manage productos table respecting their privileges."""

    def __init__(self, master: Toplevel, actions: list[str]) -> None:
        self.master = master
        self.actions = actions
        self.service = ProductsCRUD()

        self.master.title("Productos")

        container = Frame(master)
        container.pack(padx=12, pady=12, fill="both", expand=True)

        Label(container, text="Código").grid(row=0, column=0, sticky="w")
        self.entry_code = tk.Entry(container)
        self.entry_code.grid(row=0, column=1, sticky="ew")

        Label(container, text="Nombre").grid(row=1, column=0, sticky="w")
        self.entry_name = tk.Entry(container)
        self.entry_name.grid(row=1, column=1, sticky="ew")

        Label(container, text="Descripción").grid(row=2, column=0, sticky="w")
        self.entry_description = tk.Entry(container)
        self.entry_description.grid(row=2, column=1, sticky="ew")

        Label(container, text="IVA").grid(row=3, column=0, sticky="w")
        self.entry_iva = tk.Entry(container)
        self.entry_iva.grid(row=3, column=1, sticky="ew")

        Label(container, text="Costo venta").grid(row=4, column=0, sticky="w")
        self.entry_cost = tk.Entry(container)
        self.entry_cost.grid(row=4, column=1, sticky="ew")

        buttons = Frame(container)
        buttons.grid(row=5, column=0, columnspan=2, pady=8)

        self.btn_create = tk.Button(buttons, text="Crear", command=self.create_product)
        self.btn_create.grid(row=0, column=0, padx=4)
        self.btn_update = tk.Button(buttons, text="Actualizar", command=self.update_product)
        self.btn_update.grid(row=0, column=1, padx=4)
        self.btn_delete = tk.Button(buttons, text="Eliminar", command=self.delete_product)
        self.btn_delete.grid(row=0, column=2, padx=4)
        tk.Button(buttons, text="Limpiar", command=self.clear_form).grid(row=0, column=3, padx=4)

        Label(container, text="Productos").grid(row=6, column=0, columnspan=2, sticky="w", pady=(10, 0))
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

    def refresh_list(self) -> None:
        self.listbox.delete(0, END)
        for product in self.service.list_products():
            row = f"{product['codprod']} - {product['nomprod']} (${product['costovta']})"
            self.listbox.insert(END, row)

    def _get_form(self):
        return (
            self.entry_code.get().strip(),
            self.entry_name.get().strip(),
            self.entry_description.get().strip(),
            self.entry_iva.get().strip(),
            self.entry_cost.get().strip(),
        )

    def create_product(self) -> None:
        if "create" not in self.actions:
            return
        codprod, nomprod, descripcion, iva, costovta = self._get_form()
        if not codprod or not nomprod:
            messagebox.showerror("Productos", "Código y nombre son obligatorios.")
            return
        try:
            iva_value = float(iva or 0)
            cost_value = float(costovta or 0)
        except ValueError:
            messagebox.showerror("Productos", "IVA y costo deben ser numéricos.")
            return
        ok, msg = self.service.create_product(codprod, nomprod, descripcion, iva_value, cost_value)
        if ok:
            messagebox.showinfo("Productos", msg)
            self.refresh_list()
        else:
            messagebox.showerror("Productos", msg)

    def update_product(self) -> None:
        if "update" not in self.actions:
            messagebox.showerror("Productos", "No tiene permiso para actualizar (nivel insuficiente).")
            return
        codprod, nomprod, descripcion, iva, costovta = self._get_form()
        if not codprod:
            messagebox.showerror("Productos", "Seleccione un producto.")
            return
        try:
            iva_value = float(iva or 0)
            cost_value = float(costovta or 0)
        except ValueError:
            messagebox.showerror("Productos", "IVA y costo deben ser numéricos.")
            return
        ok, msg = self.service.update_product(codprod, nomprod, descripcion, iva_value, cost_value)
        if ok:
            messagebox.showinfo("Productos", msg)
            self.refresh_list()
        else:
            messagebox.showerror("Productos", msg)

    def delete_product(self) -> None:
        if "delete" not in self.actions:
            messagebox.showerror("Productos", "No tiene permiso para eliminar (nivel insuficiente).")
            return
        codprod = self.entry_code.get().strip()
        if not codprod:
            messagebox.showerror("Productos", "Seleccione un producto.")
            return
        ok, msg = self.service.delete_product(codprod)
        if ok:
            messagebox.showinfo("Productos", msg)
            self.clear_form()
            self.refresh_list()
        else:
            messagebox.showerror("Productos", msg)

    def load_selection(self, event) -> None:
        selection = event.widget.curselection()
        if not selection:
            return
        codprod = event.widget.get(selection[0]).split(" ")[0]
        product = self.service.read_product(codprod)
        if not product:
            return
        self.entry_code.delete(0, END)
        self.entry_code.insert(0, product["codprod"])
        self.entry_name.delete(0, END)
        self.entry_name.insert(0, product["nomprod"])
        self.entry_description.delete(0, END)
        self.entry_description.insert(0, product["descripcion"])
        self.entry_iva.delete(0, END)
        self.entry_iva.insert(0, product["iva"])
        self.entry_cost.delete(0, END)
        self.entry_cost.insert(0, product["costovta"])

    def clear_form(self) -> None:
        for entry in (
            self.entry_code,
            self.entry_name,
            self.entry_description,
            self.entry_iva,
            self.entry_cost,
        ):
            entry.delete(0, END)


def open_products_window(parent, username: str, level: int) -> None:
    actions = allowed_actions("products", level)
    if not actions:
        messagebox.showwarning("Productos", "No tiene permisos para este módulo.")
        return
    window = Toplevel(parent)
    ProductsWindow(window, actions)
