"""Reporting window that exposes sales filters and summary metrics."""

from __future__ import annotations

import tkinter as tk
from tkinter import Toplevel, messagebox

from GUI.permissions import allowed_actions
from Modules.Sales import SalesCRUD


class ReportsWindow:
    """Provide sales reports such as date filters and aggregated indicators."""

    PERIOD_OPTIONS = [
        ("Día", "day"),
        ("Semana", "week"),
        ("Mes", "month"),
        ("Año", "year"),
    ]

    def __init__(self, master: Toplevel, username: str, level: int, actions: list[str]) -> None:
        self.master = master
        self.username = username
        self.level = level
        self.actions = actions
        self.service = SalesCRUD()

        self.master.title("Reportes de ventas")
        self.master.geometry("520x480")

        container = tk.Frame(master)
        container.pack(padx=12, pady=12, fill="both", expand=True)

        tk.Label(container, text="Fecha inicio (YYYY-MM-DD)").grid(row=0, column=0, sticky="w")
        self.entry_start = tk.Entry(container)
        self.entry_start.grid(row=0, column=1, sticky="ew")

        tk.Label(container, text="Fecha fin (YYYY-MM-DD)").grid(row=1, column=0, sticky="w")
        self.entry_end = tk.Entry(container)
        self.entry_end.grid(row=1, column=1, sticky="ew")

        tk.Button(container, text="Filtrar ventas", command=self.show_sales).grid(row=2, column=0, pady=6)

        self.period_var = tk.StringVar(value=self.PERIOD_OPTIONS[0][1])
        period_menu = tk.OptionMenu(
            container,
            self.period_var,
            *[opt[1] for opt in self.PERIOD_OPTIONS],
        )
        period_menu.grid(row=2, column=1, sticky="ew", padx=4)
        tk.Button(container, text="Ver indicadores", command=self.show_summary).grid(row=2, column=2, padx=4)

        self.text_output = tk.Text(container, height=18)
        self.text_output.grid(row=3, column=0, columnspan=3, sticky="nsew", pady=(10, 0))

        container.columnconfigure(1, weight=1)
        container.rowconfigure(3, weight=1)

    def _get_dates(self) -> tuple[str, str]:
        return self.entry_start.get().strip(), self.entry_end.get().strip()

    def show_sales(self) -> None:
        if "report" not in self.actions:
            messagebox.showwarning("Reportes", "No cuenta con permisos de reporte.")
            return
        start, end = self._get_dates()
        records = self.service.list_sales_by_date_range(start or "0001-01-01", end or "9999-12-31", username=self.username)
        self.text_output.delete("1.0", tk.END)
        if not records:
            self.text_output.insert(tk.END, "Sin registros para el rango indicado.\n")
            return
        for sale in records:
            line = (
                f"ID {sale['id']} | Fecha {sale['fecha']} | Cliente {sale['codclie']} | "
                f"Prod {sale['codprod']} | Cant {sale['canti']} | Total {sale['vrtotal']}\n"
            )
            self.text_output.insert(tk.END, line)

    def show_summary(self) -> None:
        if "report" not in self.actions:
            messagebox.showwarning("Reportes", "No cuenta con permisos de reporte.")
            return
        period = self.period_var.get()
        start, end = self._get_dates()
        stats = self.service.summarize_sales(period, username=self.username, start_date=start or None, end_date=end or None)
        self.text_output.delete("1.0", tk.END)
        if not stats:
            self.text_output.insert(tk.END, "No hay datos para generar indicadores.\n")
            return
        self.text_output.insert(
            tk.END,
            f"Indicadores agrupados por {period}:\n\n",
        )
        for row in stats:
            line = (
                f"Periodo: {row['periodo']} | Total ventas: {row['total_ventas']} | IVA: {row['total_iva']} | "
                f"Clientes únicos: {row['clientes_unicos']} | Promedio por cliente: {row['promedio_por_cliente']}\n"
            )
            self.text_output.insert(tk.END, line)


def open_reports_window(parent, username: str, level: int) -> None:
    actions = allowed_actions("reports", level)
    if "report" not in actions:
        messagebox.showwarning("Reportes", "No tiene permisos para este módulo.")
        return
    window = Toplevel(parent)
    ReportsWindow(window, username, level, actions)
