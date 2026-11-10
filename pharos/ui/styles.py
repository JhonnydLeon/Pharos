"""
ui/styles.py
============
Gestión del tema visual de Pharos (colores y estilos ttk).

Principios SOLID aplicados:
  S – Single Responsibility: SOLO aplica estilos; no construye widgets.
  O – Open/Closed: cambiar colores solo requiere editar constants.py,
      no tocar esta clase.
"""

import tkinter as tk
from tkinter import ttk

from pharos.constants import COLORS as C


class ThemeManager:
    """
    Aplica el tema oscuro rojo/negro a una instancia de Tk.

    Uso:
        ThemeManager(root).apply()
    """

    def __init__(self, root: tk.Tk) -> None:
        self._root  = root
        self._style = ttk.Style(root)

    def apply(self) -> None:
        """Configura todos los estilos ttk y el fondo de la ventana."""
        self._root.configure(bg=C["bg"])
        self._configure_base()
        self._configure_entry()
        self._configure_combobox()
        self._configure_scrollbar()
        self._configure_progressbar()

    # ── Privado ───────────────────────────────────────────────────────────────
    def _configure_base(self) -> None:
        self._style.theme_use("clam")
        self._style.configure(
            ".",
            background=C["bg"],
            foreground=C["text"],
            fieldbackground=C["surface2"],
            selectbackground=C["accent"],
            selectforeground="white",
            bordercolor=C["border"],
            troughcolor=C["surface"],
            font=("Segoe UI", 10),
        )
        self._style.configure("TFrame", background=C["bg"])
        self._style.configure("TLabel", background=C["bg"], foreground=C["text"])

    def _configure_entry(self) -> None:
        self._style.configure(
            "TEntry",
            fieldbackground=C["surface2"],
            foreground=C["text"],
            insertcolor=C["text"],
        )
        self._style.map("TEntry", fieldbackground=[("focus", C["surface2"])])

    def _configure_combobox(self) -> None:
        self._style.configure(
            "TCombobox",
            fieldbackground=C["surface2"],
            background=C["surface2"],
            foreground=C["text"],
            arrowcolor=C["accent"],
        )
        self._style.map(
            "TCombobox",
            fieldbackground=[("readonly", C["surface2"])],
            selectbackground=[("readonly", C["accent"])],
        )

    def _configure_scrollbar(self) -> None:
        self._style.configure(
            "TScrollbar",
            background=C["surface2"],
            troughcolor=C["surface"],
            arrowcolor=C["text_dim"],
        )

    def _configure_progressbar(self) -> None:
        self._style.configure(
            "TProgressbar",
            troughcolor=C["surface2"],
            background=C["accent"],
            darkcolor=C["accent_dark"],
            lightcolor=C["accent_hover"],
        )
