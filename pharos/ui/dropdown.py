"""
ui/dropdown.py
==============
Botón desplegable personalizado con estética Pharos.

Reemplaza ttk.Combobox con:
  - Botón plano sin flecha (igual que los demás botones de la app)
  - Popup propio con overrideredirect (sin bordes del SO, sin líneas blancas/negras)
  - API básica compatible con Combobox: current(), dd["values"] = [...]
  - Hover y selección con colores de la app
  - Se cierra al hacer clic fuera

Principio SOLID:
  S – Solo gestiona la UI del desplegable, sin lógica de negocio.
  O – Los colores y fuentes son parámetros; no hay valores hardcodeados.
"""

import tkinter as tk
from typing import Callable, Optional

from pharos.constants import COLORS as C


class DropdownButton(tk.Frame):
    """
    Botón plano + popup propio.

    Uso:
        dd = DropdownButton(parent, values=["A", "B"], on_select=lambda i: print(i))
        dd.pack(...)
        dd.current(0)          # seleccionar por índice
        dd.current()           # obtener índice actual
        dd["values"] = [...]   # actualizar lista
    """

    def __init__(
        self,
        parent,
        values: list[str],
        bg: str = C["surface2"],
        fg: str = C["text_dim"],
        hover_bg: str = C["surface"],
        hover_fg: str = C["text"],
        active_bg: str = C["accent"],
        active_fg: str = "white",
        padx: int = 14,
        pady: int = 8,
        font=("Segoe UI", 10),
        min_width: int = 160,
        on_select: Optional[Callable[[int], None]] = None,
    ) -> None:
        # El Frame tiene el mismo bg que el botón → no se ve el borde del frame
        super().__init__(parent, bg=bg, bd=0, highlightthickness=0)

        self._values    = list(values)
        self._current   = 0
        self._on_select = on_select
        self._popup: Optional[tk.Toplevel] = None
        self._root_bid  = None   # binding id en la ventana raíz
        self._min_width = min_width

        # Paleta para el popup
        self._bg        = bg
        self._fg        = fg
        self._hover_bg  = hover_bg
        self._hover_fg  = hover_fg
        self._active_bg = active_bg
        self._active_fg = active_fg
        self._font      = font
        self._padx      = padx
        self._pady      = pady

        # Botón principal (trigger)
        self._btn = tk.Button(
            self,
            text=self._values[0] if self._values else "",
            bg=bg, fg=fg,
            activebackground=hover_bg, activeforeground=hover_fg,
            relief="flat", bd=0,
            padx=padx, pady=pady,
            font=font,
            cursor="hand2",
            command=self._toggle,
        )
        self._btn.pack(fill="both", expand=True)

    # ── API compatible con ttk.Combobox ───────────────────────────────────────
    def current(self, idx: Optional[int] = None) -> Optional[int]:
        """Sin arg: devuelve índice. Con arg: establece índice."""
        if idx is None:
            return self._current
        self._set(idx)
        return None

    def __setitem__(self, key: str, value) -> None:
        """Permite: dd["values"] = [...]"""
        if key == "values":
            self._values = list(value)
            safe = max(0, min(self._current, len(self._values) - 1))
            self._current = safe
            self._btn.configure(text=self._values[safe] if self._values else "")

    # ── Privado ───────────────────────────────────────────────────────────────
    def _set(self, idx: int) -> None:
        self._current = max(0, min(idx, len(self._values) - 1))
        self._btn.configure(text=self._values[self._current] if self._values else "")

    def _toggle(self) -> None:
        if self._popup and self._popup.winfo_exists():
            self._close()
        else:
            self._open()

    def _open(self) -> None:
        self.update_idletasks()

        popup = tk.Toplevel(self)
        popup.overrideredirect(True)
        # Border sutil: 1 px del color de borde de la app (no negro/blanco)
        popup.configure(bg=C["border"])
        self._popup = popup

        # Interior sin borde adicional
        inner = tk.Frame(popup, bg=C["surface2"], bd=0, highlightthickness=0)
        inner.pack(fill="both", expand=True, padx=1, pady=1)

        for i, label in enumerate(self._values):
            is_sel = (i == self._current)
            item_bg = self._active_bg if is_sel else C["surface2"]
            item_fg = self._active_fg if is_sel else C["text"]

            btn = tk.Button(
                inner,
                text=label,
                bg=item_bg, fg=item_fg,
                activebackground=C["accent_dark"],
                activeforeground="white",
                relief="flat", bd=0,
                padx=self._padx,
                pady=max(self._pady - 2, 4),
                font=self._font,
                anchor="w",
                cursor="hand2",
                command=lambda n=i: self._select(n),
            )
            btn.pack(fill="x")

            # Hover solo en las no-seleccionadas
            if not is_sel:
                btn.bind("<Enter>", lambda e, b=btn: b.configure(bg=C["surface"], fg=C["text"]))
                btn.bind("<Leave>", lambda e, b=btn: b.configure(bg=C["surface2"], fg=C["text"]))

        # Dimensionar y posicionar
        popup.update_idletasks()
        bx = self.winfo_rootx()
        by = self.winfo_rooty() + self.winfo_height()
        bw = max(self.winfo_width(), self._min_width)
        bh = popup.winfo_reqheight()

        # Si no cabe debajo, mostrar arriba
        if by + bh > self.winfo_screenheight() - 40:
            by = self.winfo_rooty() - bh - 2

        popup.geometry(f"{bw}x{bh}+{bx}+{by}")
        popup.lift()
        popup.attributes("-topmost", True)

        # Cerrar al hacer clic fuera del popup
        self._root_bid = self.winfo_toplevel().bind(
            "<Button-1>", self._on_outside_click, add="+"
        )

    def _on_outside_click(self, event: tk.Event) -> None:
        if not (self._popup and self._popup.winfo_exists()):
            return
        px, py = self._popup.winfo_rootx(), self._popup.winfo_rooty()
        pw, ph = self._popup.winfo_width(), self._popup.winfo_height()
        inside = px <= event.x_root <= px + pw and py <= event.y_root <= py + ph
        if not inside:
            self._close()

    def _select(self, idx: int) -> None:
        self._set(idx)
        self._close()
        if self._on_select:
            self._on_select(idx)

    def _close(self) -> None:
        if self._popup and self._popup.winfo_exists():
            self._popup.destroy()
        self._popup = None
        if self._root_bid:
            try:
                self.winfo_toplevel().unbind("<Button-1>", self._root_bid)
            except Exception:
                pass
            self._root_bid = None

