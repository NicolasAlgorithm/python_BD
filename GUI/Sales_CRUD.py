"""Sales window bound to the Sales CRUD service with permissions."""

from __future__ import annotations

import tkinter as tk
from tkinter import END, Frame, Label, Listbox, Scrollbar, Toplevel, messagebox

from GUI.permissions import allowed_actions
from Modules.Sales import SalesCRUD


class SalesWindow:
    """CRUD window for ventas table, aware of user capabilities."""

    def __init__(self, master: Toplevel, username: str, level: int, actions: list[str]) -> None:
        self.master = master
        self.username = username
        self.level = level
        self.actions = actions
        self.service = SalesCRUD()

        self.master.title("Ventas")

        frame = Frame(master)
        frame.pack(padx=12, pady=12, fill="both", expand=True)

        Label(frame, text="ID venta").grid(row=0, column=0, sticky="w")
        self.entry_id = tk.Entry(frame)
        self.entry_id.grid(row=0, column=1, sticky="ew")

        Label(frame, text="Fecha (YYYY-MM-DD)").grid(row=1, column=0, sticky="w")
        self.entry_date = tk.Entry(frame)
        self.entry_date.grid(row=1, column=1, sticky="ew")

        Label(frame, text="Cliente").grid(row=2, column=0, sticky="w")
        self.entry_client = tk.Entry(frame)
        self.entry_client.grid(row=2, column=1, sticky="ew")

        Label(frame, text="Producto").grid(row=3, column=0, sticky="w")
        self.entry_product = tk.Entry(frame)
        self.entry_product.grid(row=3, column=1, sticky="ew")

        Label(frame, text="Nombre producto").grid(row=4, column=0, sticky="w")
        self.entry_name = tk.Entry(frame)
        self.entry_name.grid(row=4, column=1, sticky="ew")

        Label(frame, text="Precio").grid(row=5, column=0, sticky="w")
        self.entry_price = tk.Entry(frame)
        self.entry_price.grid(row=5, column=1, sticky="ew")

        Label(frame, text="Cantidad").grid(row=6, column=0, sticky="w")
        self.entry_quantity = tk.Entry(frame)
        self.entry_quantity.grid(row=6, column=1, sticky="ew")

        Label(frame, text="IVA").grid(row=7, column=0, sticky="w")
        self.entry_iva = tk.Entry(frame)
        self.entry_iva.grid(row=7, column=1, sticky="ew")

        buttons = Frame(frame)
        buttons.grid(row=8, column=0, columnspan=2, pady=8)

        self.btn_create = tk.Button(buttons, text="Crear", command=self.create_sale)
        self.btn_create.grid(row=0, column=0, padx=4)
        self.btn_update = tk.Button(buttons, text="Actualizar", command=self.update_sale)
        self.btn_update.grid(row=0, column=1, padx=4)
        self.btn_delete = tk.Button(buttons, text="Eliminar", command=self.delete_sale)
        self.btn_delete.grid(row=0, column=2, padx=4)
        tk.Button(buttons, text="Limpiar", command=self.clear_form).grid(row=0, column=3, padx=4)

        Label(frame, text="Ventas registradas").grid(row=9, column=0, columnspan=2, sticky="w", pady=(10, 0))
        list_frame = Frame(frame)
        list_frame.grid(row=10, column=0, columnspan=2, sticky="nsew")

        self.listbox = Listbox(list_frame, width=70, height=10)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.listbox.bind("<<ListboxSelect>>", self.load_selection)

        scrollbar = Scrollbar(list_frame, orient=tk.VERTICAL, command=self.listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=scrollbar.set)

        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(10, weight=1)

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
        for sale in self.service.list_sales(self.username):
            row = (
                f"{sale['id']} | {sale['fecha']} | Cliente: {sale['codclie']} | "
                f"Prod: {sale['codprod']} | Cant: {sale['canti']} | Total: {sale['vrtotal']}"
            )
            self.listbox.insert(END, row)

    def _parse_float(self, value: str) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    def _parse_int(self, value: str) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return 0

    def _get_form(self):
        return {
            "sale_id": self.entry_id.get().strip(),
            "fecha": self.entry_date.get().strip(),
            "codclie": self.entry_client.get().strip(),
            "codprod": self.entry_product.get().strip(),
            "nomprod": self.entry_name.get().strip(),
            "costovta": self._parse_float(self.entry_price.get()),
            "canti": self._parse_int(self.entry_quantity.get()),
            "vriva": self._parse_float(self.entry_iva.get()),
        }

    def create_sale(self) -> None:
        if "create" not in self.actions:
            return
        data = self._get_form()
        required = [data["fecha"], data["codclie"], data["codprod"], data["nomprod"]]
        if not all(required):
            messagebox.showerror("Ventas", "Complete fecha, cliente, producto y nombre.")
            return
        ok, msg = self.service.create_sale(
            data["fecha"],
            data["codclie"],
            data["codprod"],
            data["nomprod"],
            data["costovta"],
            data["canti"],
            vriva=data["vriva"],
            username=self.username,
        )
        if ok:
            messagebox.showinfo("Ventas", msg)
            self.refresh_list()
        else:
            messagebox.showerror("Ventas", msg)

    def update_sale(self) -> None:
        if "update" not in self.actions:
            return
        data = self._get_form()
        if not data["sale_id"]:
            messagebox.showerror("Ventas", "Seleccione una venta.")
            return
        ok, msg = self.service.update_sale(
            int(data["sale_id"]),
            data["fecha"],
            data["codclie"],
            data["codprod"],
            data["nomprod"],
            data["costovta"],
            data["canti"],
            vriva=data["vriva"],
            username=self.username,
        )
        if ok:
            messagebox.showinfo("Ventas", msg)
            self.refresh_list()
        else:
            messagebox.showerror("Ventas", msg)

    def delete_sale(self) -> None:
        if "delete" not in self.actions:
            return
        sale_id = self.entry_id.get().strip()
        if not sale_id:
            messagebox.showerror("Ventas", "Seleccione una venta.")
            return
        ok, msg = self.service.delete_sale(int(sale_id), username=self.username)
        if ok:
            messagebox.showinfo("Ventas", msg)
            self.clear_form()
            self.refresh_list()
        else:
            messagebox.showerror("Ventas", msg)

    def load_selection(self, event) -> None:
        selection = event.widget.curselection()
        if not selection:
            return
        sale_id = event.widget.get(selection[0]).split(" |")[0]
        sale = self.service.read_sale(int(sale_id), username=self.username)
        if not sale:
            return
        self.entry_id.delete(0, END)
        self.entry_id.insert(0, sale["id"])
        self.entry_date.delete(0, END)
        self.entry_date.insert(0, sale["fecha"])
        self.entry_client.delete(0, END)
        self.entry_client.insert(0, sale["codclie"])
        self.entry_product.delete(0, END)
        self.entry_product.insert(0, sale["codprod"])
        self.entry_name.delete(0, END)
        self.entry_name.insert(0, sale["nomprod"])
        self.entry_price.delete(0, END)
        self.entry_price.insert(0, sale["costovta"])
        self.entry_quantity.delete(0, END)
        self.entry_quantity.insert(0, sale["canti"])
        self.entry_iva.delete(0, END)
        self.entry_iva.insert(0, sale["vriva"])

    def clear_form(self) -> None:
        for entry in (
            self.entry_id,
            self.entry_date,
            self.entry_client,
            self.entry_product,
            self.entry_name,
            self.entry_price,
            self.entry_quantity,
            self.entry_iva,
        ):
            entry.delete(0, END)


def open_sales_window(parent, username: str, level: int) -> None:
    actions = allowed_actions("sales", level)
    if not actions:
        messagebox.showwarning("Ventas", "No tiene permisos para este módulo.")
        return
    window = Toplevel(parent)
    SalesWindow(window, username, level, actions)