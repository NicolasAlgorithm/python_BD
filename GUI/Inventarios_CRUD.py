"""Inventory window linked to Inventarios CRUD with privilege handling."""

from __future__ import annotations

import tkinter as tk
from tkinter import END, Frame, Label, Listbox, Toplevel, messagebox

from GUI.permissions import allowed_actions
from Modules.Inventarios import InventoriesCRUD


class InventoryWindow:
    """Render inventories with create/update/delete governed by user level."""

    def __init__(self, master: Toplevel, username: str, level: int, actions: list[str]) -> None:
        self.master = master
        self.username = username
        self.level = level
        self.actions = actions
        self.service = InventoriesCRUD()

        self.master.title("Inventarios")

        container = Frame(master)
        container.pack(padx=12, pady=12, fill="both", expand=True)

        Label(container, text="Código producto").grid(row=0, column=0, sticky="w")
        self.entry_code = tk.Entry(container)
        self.entry_code.grid(row=0, column=1, sticky="ew")

        Label(container, text="Cantidad").grid(row=1, column=0, sticky="w")
        self.entry_amount = tk.Entry(container)
        self.entry_amount.grid(row=1, column=1, sticky="ew")

        Label(container, text="Stock mínimo").grid(row=2, column=0, sticky="w")
        self.entry_min = tk.Entry(container)
        self.entry_min.grid(row=2, column=1, sticky="ew")

        Label(container, text="IVA").grid(row=3, column=0, sticky="w")
        self.entry_iva = tk.Entry(container)
        self.entry_iva.grid(row=3, column=1, sticky="ew")

        Label(container, text="Costo venta").grid(row=4, column=0, sticky="w")
        self.entry_cost = tk.Entry(container)
        self.entry_cost.grid(row=4, column=1, sticky="ew")

        buttons = Frame(container)
        buttons.grid(row=5, column=0, columnspan=2, pady=8)

        self.btn_create = tk.Button(buttons, text="Crear", command=self.create_inventory)
        self.btn_create.grid(row=0, column=0, padx=4)
        self.btn_update = tk.Button(buttons, text="Actualizar", command=self.update_inventory)
        self.btn_update.grid(row=0, column=1, padx=4)
        self.btn_delete = tk.Button(buttons, text="Eliminar", command=self.delete_inventory)
        self.btn_delete.grid(row=0, column=2, padx=4)
        tk.Button(buttons, text="Limpiar", command=self.clear_form).grid(row=0, column=3, padx=4)

        Label(container, text="Inventario actual").grid(row=6, column=0, columnspan=2, sticky="w", pady=(10, 0))
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
        for item in self.service.list_inventories(self.username):
            row = (
                f"{item['codprod']} - {item['nomprod']} | Cant: {item['cantidad']} | "
                f"Stock min: {item['stock_minimo']}"
            )
            self.listbox.insert(END, row)

    def _parse_numeric(self, value: str, cast, default=0):
        try:
            return cast(value)
        except (TypeError, ValueError):
            return default

    def _get_form(self):
        codprod = self.entry_code.get().strip()
        cantidad = self._parse_numeric(self.entry_amount.get(), int)
        stock_minimo = self._parse_numeric(self.entry_min.get(), int)
        iva = self._parse_numeric(self.entry_iva.get(), float)
        costovta = self._parse_numeric(self.entry_cost.get(), float)
        return codprod, cantidad, stock_minimo, iva, costovta

    def create_inventory(self) -> None:
        if "create" not in self.actions:
            return
        codprod, cantidad, stock_minimo, iva, costovta = self._get_form()
        if not codprod:
            messagebox.showerror("Inventarios", "Debe indicar código de producto.")
            return
        ok, msg = self.service.create_inventory(
            codprod,
            cantidad,
            stock_minimo,
            iva,
            costovta,
            username=self.username,
        )
        if ok:
            messagebox.showinfo("Inventarios", msg)
            self.refresh_list()
        else:
            messagebox.showerror("Inventarios", msg)

    def update_inventory(self) -> None:
        if "update" not in self.actions:
            return
        codprod, cantidad, stock_minimo, iva, costovta = self._get_form()
        if not codprod:
            messagebox.showerror("Inventarios", "Seleccione un registro a actualizar.")
            return
        ok, msg = self.service.update_inventory(
            codprod,
            cantidad,
            stock_minimo,
            iva,
            costovta,
            username=self.username,
        )
        if ok:
            messagebox.showinfo("Inventarios", msg)
            self.refresh_list()
        else:
            messagebox.showerror("Inventarios", msg)

    def delete_inventory(self) -> None:
        if "delete" not in self.actions:
            return
        codprod = self.entry_code.get().strip()
        if not codprod:
            messagebox.showerror("Inventarios", "Seleccione un registro a eliminar.")
            return
        ok, msg = self.service.delete_inventory(codprod, username=self.username)
        if ok:
            messagebox.showinfo("Inventarios", msg)
            self.clear_form()
            self.refresh_list()
        else:
            messagebox.showerror("Inventarios", msg)

    def load_selection(self, event) -> None:
        selection = event.widget.curselection()
        if not selection:
            return
        codprod = event.widget.get(selection[0]).split(" ")[0]
        data = self.service.read_inventory(codprod, username=self.username)
        if not data:
            return
        self.entry_code.delete(0, END)
        self.entry_code.insert(0, data["codprod"])
        self.entry_amount.delete(0, END)
        self.entry_amount.insert(0, data["cantidad"])
        self.entry_min.delete(0, END)
        self.entry_min.insert(0, data["stock_minimo"])
        self.entry_iva.delete(0, END)
        self.entry_iva.insert(0, data["iva"])
        self.entry_cost.delete(0, END)
        self.entry_cost.insert(0, data["costovta"])

    def clear_form(self) -> None:
        for entry in (
            self.entry_code,
            self.entry_amount,
            self.entry_min,
            self.entry_iva,
            self.entry_cost,
        ):
            entry.delete(0, END)


def open_inventory_window(parent, username: str, level: int) -> None:
    actions = allowed_actions("inventories", level)
    if not actions:
        messagebox.showwarning("Inventarios", "No tiene permisos para este módulo.")
        return
    window = Toplevel(parent)
    InventoryWindow(window, username, level, actions)