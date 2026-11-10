"""
ui/settings_window.py
=====================
Ventana modal de Preferencias.

Principios SOLID aplicados:
  S – Single Responsibility: SOLO muestra y recoge preferencias del usuario.
  D – Dependency Inversion: recibe SettingsManager y Translator ya
      construidos; no los crea internamente.
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable

from pharos.constants import COLORS as C
from pharos.i18n import SUPPORTED_LANGUAGES, Translator
from pharos.settings import SettingsManager


class SettingsWindow(tk.Toplevel):
    """
    Ventana modal de configuración.

    Parámetros:
        parent      : ventana padre (tk.Tk).
        settings    : instancia de SettingsManager.
        translator  : instancia de Translator.
        on_save     : callback que se llama al guardar (recibe el nuevo idioma).
    """

    def __init__(
        self,
        parent: tk.Tk,
        settings: SettingsManager,
        translator: Translator,
        on_save: Callable[[str], None],
    ) -> None:
        super().__init__(parent)
        self._settings   = settings
        self._t          = translator
        self._on_save    = on_save
        self._setup_window()
        self._build_widgets()
        self.grab_set()   # modal

    # ── Privado ───────────────────────────────────────────────────────────────
    def _setup_window(self) -> None:
        self.title(self._t("settings"))
        self.geometry("360x200")
        self.configure(bg=C["bg"])
        self.resizable(False, False)

    def _build_widgets(self) -> None:
        pad = {"padx": 18, "pady": 10}

        # ── Selector de idioma ────────────────────────────────────────────────
        row_lang = tk.Frame(self, bg=C["bg"])
        row_lang.pack(fill="x", **pad)

        tk.Label(
            row_lang,
            text=self._t("language"),
            bg=C["bg"], fg=C["text"],
            font=("Segoe UI", 10),
        ).pack(side="left")

        self._lang_var = tk.StringVar(value=self._settings["language"])
        ttk.Combobox(
            row_lang,
            textvariable=self._lang_var,
            values=SUPPORTED_LANGUAGES,
            state="readonly",
            width=8,
        ).pack(side="left", padx=10)

        # ── Verificar actualizaciones al iniciar ──────────────────────────────
        self._startup_var = tk.BooleanVar(
            value=self._settings.get("check_updates_on_startup", True)
        )
        tk.Checkbutton(
            self,
            text=self._t("pref_startup_update"),
            variable=self._startup_var,
            bg=C["bg"], fg=C["text"],
            activebackground=C["bg"], activeforeground=C["text"],
            selectcolor=C["surface2"],
            font=("Segoe UI", 10),
        ).pack(anchor="w", **pad)

        # ── Botón Guardar ─────────────────────────────────────────────────────
        tk.Button(
            self,
            text=self._t("pref_save"),
            bg=C["accent"], fg="white",
            activebackground=C["accent_hover"], activeforeground="white",
            relief="flat", bd=0, padx=16, pady=7,
            font=("Segoe UI", 10, "bold"),
            command=self._save,
        ).pack(pady=12)

    def _save(self) -> None:
        new_lang = self._lang_var.get()
        self._settings["language"]                 = new_lang
        self._settings["check_updates_on_startup"] = self._startup_var.get()
        self._settings.save()
        self._on_save(new_lang)
        self.destroy()

