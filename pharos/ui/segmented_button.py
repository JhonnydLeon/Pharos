"""
ui/segmented_button.py
======================
Control de botones segmentados (modo selector tipo pill).

Principio SOLID:
  S – Solo gestiona la UI del segmented button.
      No sabe nada del dominio de video.
"""

from __future__ import annotations

import tkinter as tk
from typing import Callable, Optional

from pharos.constants import COLORS as C


class SegmentedButton(tk.Frame):
    """
    Fila de botones planos del estilo Pharos donde exactamente uno
    está "activo" (rojo). Al hacer clic en uno, los demás se desactivan.

    IMPORTANTE: No usar self._options (nombre reservado por tkinter BaseWidget).
                Se usa self._labels en su lugar.

    Uso:
        seg = SegmentedButton(parent, options=["A", "B", "C"], on_change=callback)
        seg.pack(...)
        seg.set_index(1)        # activar "B"
        seg.active_index        # propiedad de solo lectura
    """

    def __init__(
        self,
        parent,
        options:   list[str],
        on_change: Optional[Callable[[int], None]] = None,
        font=("Segoe UI", 10),
        padx: int = 16,
        pady: int = 8,
    ) -> None:
        super().__init__(parent, bg=C["bg"], bd=0, highlightthickness=0)
        self._labels    = list(options)   # ← NO usar _options (reservado por tkinter)
        self._on_change = on_change
        self._font      = font
        self._padx      = padx
        self._pady      = pady
        self._active    = 0
        self._buttons: list[tk.Button] = []
        self._build()

    # ── API pública ───────────────────────────────────────────────────────────
    @property
    def active_index(self) -> int:
        return self._active

    def set_index(self, idx: int) -> None:
        """Activa el botón en la posición idx (sin disparar on_change)."""
        idx = max(0, min(idx, len(self._labels) - 1))
        self._active = idx
        self._refresh_colors()

    def set_options(self, options: list[str], active: int = 0) -> None:
        """Reemplaza las opciones y reconstruye los botones."""
        for btn in self._buttons:
            btn.destroy()
        self._buttons.clear()
        self._labels = list(options)
        self._active = max(0, min(active, len(self._labels) - 1))
        self._build()

    # ── Privado ───────────────────────────────────────────────────────────────
    def _build(self) -> None:
        for i, label in enumerate(self._labels):
            btn = tk.Button(
                self,
                text=label,
                bg=C["surface2"], fg=C["text_dim"],
                activebackground=C["accent_hover"], activeforeground="white",
                relief="flat", bd=0,
                padx=self._padx, pady=self._pady,
                font=self._font,
                cursor="hand2",
                command=lambda n=i: self._select(n),
            )
            btn.pack(side="left", padx=(0, 2))
            self._buttons.append(btn)
        self._refresh_colors()

    def _select(self, idx: int) -> None:
        self._active = idx
        self._refresh_colors()
        if self._on_change:
            self._on_change(idx)

    def _refresh_colors(self) -> None:
        for i, btn in enumerate(self._buttons):
            if i == self._active:
                btn.configure(
                    bg=C["accent"], fg="white",
                    activebackground=C["accent_hover"],
                )
            else:
                btn.configure(
                    bg=C["surface2"], fg=C["text_dim"],
                    activebackground=C["surface"],
                )
                btn.bind("<Enter>", lambda e, b=btn: b.configure(
                    bg=C["surface"], fg=C["text"]))
                btn.bind("<Leave>", lambda e, b=btn: b.configure(
                    bg=C["surface2"], fg=C["text_dim"]))
