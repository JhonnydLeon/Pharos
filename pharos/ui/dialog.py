"""
ui/dialog.py
============
Diálogos modernos de Pharos que reemplazan a tkinter.messagebox.

FIX v1.1.1:
  - grab_set() / focus_force() ahora se llaman DESPUÉS de que la ventana
    está construida y visible (antes causaba freeze al buscar actualizaciones).
  - Se elimina transient() que conflictuaba con overrideredirect en Windows.
  - Se agrega -topmost y lift() para garantizar visibilidad.
"""

import tkinter as tk
from typing import Any, Optional

from pharos.constants import APP_NAME, COLORS as C, VERSION


class PharosDialog(tk.Toplevel):
    """
    Diálogo modal con estética Pharos (sin chrome de tkinter).

    El flujo correcto es:
      1. Construir widgets  (_build)
      2. Forzar render      (update)
      3. Centrar            (_center)
      4. Colocar encima     (lift / -topmost)
      5. Capturar eventos   (grab_set / focus_force)
    """

    def __init__(
        self,
        parent: tk.Tk,
        title: str,
        message: str = "",
        submsg: str = "",
        buttons: Optional[list[tuple[str, Any]]] = None,
        icon: str = "",
    ) -> None:
        super().__init__(parent)
        self.result: Any = None
        self._buttons_cfg = buttons or [("OK", True)]
        self._drag_x = self._drag_y = 0

        # Sin decoración del SO
        self.overrideredirect(True)
        self.configure(bg=C["bg"])
        self.resizable(False, False)

        # 1. Construir la UI primero
        self._build(title, message, submsg, icon)

        # 2. Forzar que la ventana se renderice antes de medir/mover
        self.update()

        # 3. Centrar sobre el padre
        self._center(parent)

        # 4. Garantizar visibilidad
        self.lift()
        self.attributes("-topmost", True)

        # 5. AHORA sí capturar eventos (en este orden)
        self.grab_set()
        self.focus_force()

    # ── Construcción ──────────────────────────────────────────────────────────
    def _build(self, title: str, message: str, submsg: str, icon: str) -> None:
        # Barra de título (roja, arrastrable)
        titlebar = tk.Frame(self, bg=C["accent"], height=38)
        titlebar.pack(fill="x")
        titlebar.pack_propagate(False)
        titlebar.bind("<ButtonPress-1>", self._drag_start)
        titlebar.bind("<B1-Motion>",     self._drag_move)

        tk.Label(
            titlebar, text=f"⚡ {APP_NAME}",
            bg=C["accent"], fg="white",
            font=("Segoe UI Black", 11, "bold"),
        ).pack(side="left", padx=12, pady=6)

        tk.Label(
            titlebar, text=f"v{VERSION}",
            bg=C["accent"], fg="#ffcccc",
            font=("Segoe UI", 8),
        ).pack(side="left")

        # Separador
        tk.Frame(self, bg=C["border"], height=1).pack(fill="x")

        # Cuerpo
        body = tk.Frame(self, bg=C["bg"], padx=28, pady=20)
        body.pack(fill="both", expand=True)

        if icon:
            tk.Label(
                body, text=icon,
                bg=C["bg"], fg=C["text"],
                font=("Segoe UI", 30),
            ).pack(pady=(0, 10))

        tk.Label(
            body, text=title,
            bg=C["bg"], fg=C["text"],
            font=("Segoe UI", 13, "bold"),
            wraplength=340, justify="center",
        ).pack()

        if message:
            tk.Label(
                body, text=message,
                bg=C["bg"], fg=C["text_dim"],
                font=("Segoe UI", 10),
                wraplength=340, justify="center",
            ).pack(pady=(8, 0))

        if submsg:
            tk.Label(
                body, text=submsg,
                bg=C["bg"], fg=C["text_dim"],
                font=("Segoe UI", 9),
                wraplength=340, justify="center",
            ).pack(pady=(4, 0))

        # Separador
        tk.Frame(self, bg=C["border"], height=1).pack(fill="x")

        # Fila de botones
        btn_row = tk.Frame(self, bg=C["surface2"], pady=12)
        btn_row.pack(fill="x")

        for i, (label, value) in enumerate(self._buttons_cfg):
            is_primary = (i == len(self._buttons_cfg) - 1)
            tk.Button(
                btn_row,
                text=label,
                bg=C["accent"]  if is_primary else C["surface"],
                fg="white"      if is_primary else C["text_dim"],
                activebackground=C["accent_hover"] if is_primary else C["surface2"],
                activeforeground="white",
                relief="flat", bd=0,
                padx=20, pady=8,
                font=("Segoe UI", 10, "bold" if is_primary else "normal"),
                cursor="hand2",
                command=lambda v=value: self._close(v),
            ).pack(side="right", padx=(0 if i else 8, 8))

    # ── Arrastre ──────────────────────────────────────────────────────────────
    def _drag_start(self, event: tk.Event) -> None:
        self._drag_x = event.x
        self._drag_y = event.y

    def _drag_move(self, event: tk.Event) -> None:
        x = self.winfo_x() + event.x - self._drag_x
        y = self.winfo_y() + event.y - self._drag_y
        self.geometry(f"+{x}+{y}")

    # ── Cierre ────────────────────────────────────────────────────────────────
    def _close(self, value: Any) -> None:
        self.result = value
        self.grab_release()
        self.destroy()

    # ── Centrado ──────────────────────────────────────────────────────────────
    def _center(self, parent: tk.Tk) -> None:
        w = self.winfo_width()
        h = self.winfo_height()
        px = parent.winfo_x() + (parent.winfo_width()  - w) // 2
        py = parent.winfo_y() + (parent.winfo_height() - h) // 2
        self.geometry(f"+{max(px, 0)}+{max(py, 0)}")


# ── Funciones de conveniencia ─────────────────────────────────────────────────

def show_info(
    parent: tk.Tk,
    title: str,
    message: str = "",
    submsg: str = "",
    icon: str = "✅",
    ok_label: str = "OK",
) -> None:
    """Diálogo informativo (un solo botón OK). Bloquea hasta que se cierra."""
    d = PharosDialog(
        parent, title, message, submsg,
        buttons=[(ok_label, True)],
        icon=icon,
    )
    parent.wait_window(d)


def show_warning(
    parent: tk.Tk,
    title: str,
    message: str = "",
    submsg: str = "",
    ok_label: str = "OK",
) -> None:
    """Diálogo de advertencia."""
    show_info(parent, title, message, submsg, icon="⚠", ok_label=ok_label)


def ask_yes_no(
    parent: tk.Tk,
    title: str,
    message: str = "",
    submsg: str = "",
    icon: str = "🎉",
    yes_label: str = "Sí",
    no_label: str = "No",
) -> bool:
    """
    Diálogo Sí / No.
    Returns True si el usuario pulsó el botón primario.
    """
    d = PharosDialog(
        parent, title, message, submsg,
        buttons=[(no_label, False), (yes_label, True)],
        icon=icon,
    )
    parent.wait_window(d)
    return bool(d.result)
