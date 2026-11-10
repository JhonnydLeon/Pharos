"""
ui/dialog.py
============
Diálogos modernos de Pharos que reemplazan a tkinter.messagebox.

Características:
  - Sin icono de tkinter (overrideredirect + chrome propio)
  - Colores y tipografía de la app (rojo/negro)
  - Arrastrable desde la barra de título
  - Soporta botones personalizados y devuelve el resultado

Principio SOLID:
  S – Solo construye y gestiona diálogos modales.
"""

import tkinter as tk
from typing import Any, Optional

from pharos.constants import APP_NAME, COLORS as C, VERSION


class PharosDialog(tk.Toplevel):
    """
    Diálogo modal base con estética Pharos (sin chrome de tkinter).

    Parámetros:
        parent   : ventana padre.
        title    : texto de la barra de título del diálogo.
        message  : mensaje principal.
        submsg   : texto secundario (más pequeño, opcional).
        buttons  : lista de (etiqueta, valor_de_retorno).
                   El último botón se trata como acción primaria (rojo).
        icon     : emoji que se muestra a la izquierda del mensaje.
    """

    def __init__(
        self,
        parent: tk.Tk,
        title: str,
        message: str,
        submsg: str = "",
        buttons: Optional[list[tuple[str, Any]]] = None,
        icon: str = "",
    ) -> None:
        super().__init__(parent)
        self.result: Any = None
        self._buttons_cfg = buttons or [("OK", True)]

        # Sin decoración de sistema operativo
        self.overrideredirect(True)
        self.configure(bg=C["bg"])
        self.resizable(False, False)

        # Siempre encima y modal
        self.transient(parent)
        self.grab_set()
        self.focus_force()

        self._build(title, message, submsg, icon)
        self._center(parent)

        # Permitir arrastrar desde la barra de título
        self._drag_x = self._drag_y = 0

    # ── Construcción ──────────────────────────────────────────────────────────
    def _build(self, title: str, message: str, submsg: str, icon: str) -> None:
        # Barra de título (roja, arrastrable)
        titlebar = tk.Frame(self, bg=C["accent"], height=38)
        titlebar.pack(fill="x")
        titlebar.pack_propagate(False)
        titlebar.bind("<ButtonPress-1>",   self._drag_start)
        titlebar.bind("<B1-Motion>",       self._drag_move)

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

        # Cuerpo del mensaje
        body = tk.Frame(self, bg=C["bg"], padx=24, pady=20)
        body.pack(fill="both", expand=True)

        if icon:
            tk.Label(
                body, text=icon,
                bg=C["bg"], fg=C["text"],
                font=("Segoe UI", 28),
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
            btn = tk.Button(
                btn_row,
                text=label,
                bg=C["accent"] if is_primary else C["surface"],
                fg="white" if is_primary else C["text_dim"],
                activebackground=C["accent_hover"] if is_primary else C["surface2"],
                activeforeground="white",
                relief="flat", bd=0,
                padx=20, pady=8,
                font=("Segoe UI", 10, "bold" if is_primary else "normal"),
                cursor="hand2",
                command=lambda v=value: self._close(v),
            )
            btn.pack(side="right", padx=(0 if i else 8, 8))

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

    def _center(self, parent: tk.Tk) -> None:
        """Centra el diálogo sobre la ventana padre."""
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
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
    """Diálogo informativo con un botón OK."""
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
    Diálogo de pregunta Sí/No.

    Returns:
        True si el usuario pulsó el botón primario (Sí / acción positiva).
    """
    d = PharosDialog(
        parent, title, message, submsg,
        buttons=[(no_label, False), (yes_label, True)],
        icon=icon,
    )
    parent.wait_window(d)
    return bool(d.result)
