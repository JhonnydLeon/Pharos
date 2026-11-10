"""
ui/log_window.py
================
Ventana secundaria de Registros / Logs.

Principios SOLID aplicados:
  S – Single Responsibility: SOLO muestra y gestiona el log de texto.
  L – Liskov: es un tk.Toplevel válido; puede usarse donde se espere
      una ventana secundaria.
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable

from pharos.constants import COLORS as C


class LogWindow(tk.Toplevel):
    """
    Ventana flotante que muestra la salida de yt-dlp en tiempo real.

    Uso:
        log = LogWindow(parent, translator)
        log.write("línea de texto\n")
        log.clear()
    """

    def __init__(self, parent: tk.Tk, translator: Callable) -> None:
        super().__init__(parent)
        self._t = translator
        self._setup_window()
        self._build_widgets()

    # ── Interfaz pública ──────────────────────────────────────────────────────
    def write(self, text: str) -> None:
        """Agrega texto al final del log."""
        self._text.configure(state="normal")
        self._text.insert("end", text)
        self._text.see("end")
        self._text.configure(state="disabled")

    def clear(self) -> None:
        """Borra todo el contenido del log."""
        self._text.configure(state="normal")
        self._text.delete("1.0", "end")
        self._text.configure(state="disabled")

    # ── Privado ───────────────────────────────────────────────────────────────
    def _setup_window(self) -> None:
        self.title(self._t("logs"))
        self.geometry("700x400")
        self.configure(bg=C["bg"])
        self.resizable(True, True)

    def _build_widgets(self) -> None:
        # Área de texto con scroll
        self._text = tk.Text(
            self,
            state="disabled",
            bg=C["log_bg"],
            fg=C["log_fg"],
            font=("Consolas", 9),
            wrap="none",
            relief="flat",
            bd=0,
            selectbackground=C["accent"],
        )
        sb_v = ttk.Scrollbar(self, orient="vertical",   command=self._text.yview)
        sb_h = ttk.Scrollbar(self, orient="horizontal", command=self._text.xview)
        self._text.configure(yscrollcommand=sb_v.set, xscrollcommand=sb_h.set)

        sb_v.pack(side="right",  fill="y")
        sb_h.pack(side="bottom", fill="x")
        self._text.pack(fill="both", expand=True)

        # Botón limpiar
        tk.Button(
            self,
            text="🗑  Limpiar / Clear",
            bg=C["surface2"], fg=C["text_dim"],
            activebackground=C["surface"], activeforeground=C["text"],
            relief="flat", bd=0, padx=10, pady=4,
            command=self.clear,
        ).pack(pady=4)

