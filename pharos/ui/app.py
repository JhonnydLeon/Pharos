"""
ui/app.py
=========
Ventana principal de Pharos. Orquesta todos los módulos.

Principios SOLID aplicados:
  S – Single Responsibility: coordina la UI; no contiene lógica de
      descarga, actualización ni persistencia (cada una está en su módulo).
  D – Dependency Inversion: recibe Downloader, Updater, Translator y
      SettingsManager ya construidos; solo los usa.
"""

import os
import subprocess
import threading
import tkinter as tk
import urllib.request
import webbrowser
from tkinter import filedialog, messagebox, ttk
from typing import Optional

from pharos.constants import COLORS as C, QUALITY_FLAGS, VERSION
from pharos.downloader import Downloader
from pharos.i18n import Translator
from pharos.settings import SettingsManager
from pharos.updater import Updater
from pharos.ui.log_window import LogWindow
from pharos.ui.settings_window import SettingsWindow
from pharos.ui.styles import ThemeManager


class App:
    """
    Ventana principal de Pharos.

    Recibe todas las dependencias por constructor (Dependency Injection).
    """

    def __init__(
        self,
        root: tk.Tk,
        settings: SettingsManager,
        translator: Translator,
    ) -> None:
        self._root       = root
        self._settings   = settings
        self._t          = translator
        self._log_win: Optional[LogWindow] = None
        self._is_fullscreen = False

        # Variables de UI
        self._save_dir  = tk.StringVar(
            value=os.path.join(os.path.expanduser("~"), "Downloads")
        )
        self._status    = tk.StringVar(value=self._t("status_ready"))
        self._quality_idx = 0   # índice en QUALITY_FLAGS

        # Aplicar tema visual
        ThemeManager(root).apply()

        # Construir interfaz
        self._build_ui()

        # Crear Downloader inyectando callbacks de esta UI
        self._downloader = Downloader(
            on_line=self._on_download_line,
            on_done=self._on_download_done,
        )

        # Crear Updater inyectando callbacks de esta UI
        self._updater = Updater(
            on_update_found=self._on_update_found,
            on_no_update=self._on_no_update,
            on_error=self._on_update_error,
        )

        # Verificación de actualizaciones al arrancar
        if self._settings.get("check_updates_on_startup", True):
            self._updater.check(startup=True)

    # ══════════════════════════════════════════════════════════════════════════
    # Construcción de la UI
    # ══════════════════════════════════════════════════════════════════════════
    def _build_ui(self) -> None:
        self._root.title(self._t("title"))
        self._root.geometry("780x580")
        self._root.minsize(640, 480)
        self._root.resizable(True, True)

        self._build_topbar()
        self._build_body()
        self._build_statusbar()

        # Atajos de teclado
        self._root.bind("<F11>",  lambda _: self.toggle_fullscreen())
        self._root.bind("<Escape>", lambda _: self._exit_fullscreen())

    # ── Barra superior ────────────────────────────────────────────────────────
    def _build_topbar(self) -> None:
        bar = tk.Frame(self._root, bg=C["accent"], height=48)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        tk.Label(
            bar, text=f"⚡ {VERSION and 'PHAROS'}",
            bg=C["accent"], fg="white",
            font=("Segoe UI Black", 14, "bold"),
        ).pack(side="left", padx=16)

        tk.Label(
            bar, text=f"v{VERSION}",
            bg=C["accent"], fg="#ffcccc",
            font=("Segoe UI", 9),
        ).pack(side="left")

        # Controles derecha
        ctrl = tk.Frame(bar, bg=C["accent"])
        ctrl.pack(side="right", padx=6)

        self._btn_minimize = self._make_bar_btn(
            ctrl, "minimize", self._root.iconify
        )
        self._btn_fullscreen = self._make_bar_btn(
            ctrl, "fullscreen", self.toggle_fullscreen
        )
        self._btn_minimize.pack(side="left",   padx=2)
        self._btn_fullscreen.pack(side="left", padx=2)

    def _make_bar_btn(self, parent, key: str, cmd) -> tk.Button:
        return tk.Button(
            parent, text=self._t(key),
            bg=C["accent_dark"], fg="white",
            activebackground=C["accent_hover"], activeforeground="white",
            relief="flat", bd=0, padx=10, pady=6,
            font=("Segoe UI", 9),
            command=cmd,
        )

    # ── Cuerpo ────────────────────────────────────────────────────────────────
    def _build_body(self) -> None:
        body = tk.Frame(self._root, bg=C["bg"])
        body.pack(fill="both", expand=True, padx=20, pady=16)

        self._build_link_row(body)
        self._build_quality_row(body)
        self._build_preview_panel(body)
        self._build_progress(body)
        self._build_action_row(body)

    def _build_link_row(self, parent: tk.Frame) -> None:
        self._lbl_link = tk.Label(
            parent, text=self._t("video_link"),
            bg=C["bg"], fg=C["text_dim"],
            font=("Segoe UI", 9, "bold"),
        )
        self._lbl_link.pack(anchor="w")

        frame = tk.Frame(parent, bg=C["border"])
        frame.pack(fill="x", pady=(4, 14))
        self._entry_url = tk.Entry(
            frame,
            bg=C["surface2"], fg=C["text"],
            insertbackground=C["text"],
            relief="flat", bd=8,
            font=("Segoe UI", 11),
        )
        self._entry_url.pack(fill="x")

    def _build_quality_row(self, parent: tk.Frame) -> None:
        row = tk.Frame(parent, bg=C["bg"])
        row.pack(fill="x", pady=(0, 12))

        # Calidad
        col_q = tk.Frame(row, bg=C["bg"])
        col_q.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self._lbl_quality = tk.Label(
            col_q, text=self._t("quality"),
            bg=C["bg"], fg=C["text_dim"],
            font=("Segoe UI", 9, "bold"),
        )
        self._lbl_quality.pack(anchor="w")

        self._cb_quality = ttk.Combobox(
            col_q,
            values=[self._t(k) for k in QUALITY_FLAGS],
            state="readonly", width=20,
            font=("Segoe UI", 10),
        )
        self._cb_quality.current(0)
        self._cb_quality.pack(anchor="w", pady=(4, 0))

        # Guardar en
        col_s = tk.Frame(row, bg=C["bg"])
        col_s.pack(side="left", fill="x", expand=True)

        self._lbl_save = tk.Label(
            col_s, text=self._t("save_in"),
            bg=C["bg"], fg=C["text_dim"],
            font=("Segoe UI", 9, "bold"),
        )
        self._lbl_save.pack(anchor="w")

        row_save = tk.Frame(col_s, bg=C["bg"])
        row_save.pack(fill="x", pady=(4, 0))

        tk.Entry(
            row_save, textvariable=self._save_dir,
            bg=C["surface2"], fg=C["text"],
            insertbackground=C["text"],
            relief="flat", bd=6,
            font=("Segoe UI", 10),
        ).pack(side="left", fill="x", expand=True)

        self._btn_choose = tk.Button(
            row_save, text=self._t("choose"),
            bg=C["surface2"], fg=C["text_dim"],
            activebackground=C["surface"], activeforeground=C["text"],
            relief="flat", bd=0, padx=10, pady=5,
            font=("Segoe UI", 9),
            command=self._choose_folder,
        )
        self._btn_choose.pack(side="left", padx=(6, 0))

    def _build_preview_panel(self, parent: tk.Frame) -> None:
        frame = tk.Frame(parent, bg=C["surface"])
        frame.pack(fill="x", pady=(0, 14))

        # Canvas miniatura
        self._canvas = tk.Canvas(
            frame, bg=C["surface"],
            width=320, height=180, highlightthickness=0,
        )
        self._canvas.pack(side="left", padx=12, pady=12)
        self._draw_placeholder()

        # Info derecha
        info = tk.Frame(frame, bg=C["surface"])
        info.pack(side="left", fill="both", expand=True, pady=12, padx=(0, 12))

        self._lbl_title = tk.Label(
            info, text="—",
            bg=C["surface"], fg=C["text"],
            font=("Segoe UI", 10, "bold"),
            wraplength=340, justify="left", anchor="w",
        )
        self._lbl_title.pack(anchor="w")

        self._lbl_meta = tk.Label(
            info, text="",
            bg=C["surface"], fg=C["text_dim"],
            font=("Segoe UI", 9),
            wraplength=340, justify="left", anchor="w",
        )
        self._lbl_meta.pack(anchor="w", pady=(4, 0))

        self._btn_preview = tk.Button(
            info, text=self._t("preview"),
            bg=C["surface2"], fg=C["text_dim"],
            activebackground=C["accent_dark"], activeforeground="white",
            relief="flat", bd=0, padx=14, pady=6,
            font=("Segoe UI", 9),
            command=self._open_preview,
        )
        self._btn_preview.pack(anchor="w", pady=(10, 0))

    def _build_progress(self, parent: tk.Frame) -> None:
        self._progress = ttk.Progressbar(
            parent, orient="horizontal", mode="indeterminate",
        )
        self._progress.pack(fill="x", pady=(0, 10))

    def _build_action_row(self, parent: tk.Frame) -> None:
        row = tk.Frame(parent, bg=C["bg"])
        row.pack(fill="x")

        self._btn_download = tk.Button(
            row, text=self._t("download"),
            bg=C["accent"], fg="white",
            activebackground=C["accent_hover"], activeforeground="white",
            relief="flat", bd=0, padx=22, pady=10,
            font=("Segoe UI", 11, "bold"),
            cursor="hand2",
            command=self._start_download,
        )
        self._btn_download.pack(side="left", padx=(0, 10))

        self._btn_logs = self._make_secondary_btn(row, "logs",    self._open_logs)
        self._btn_logs.pack(side="left", padx=(0, 6))

        self._btn_updates = self._make_secondary_btn(row, "check_updates", self._manual_update)
        self._btn_updates.pack(side="left", padx=(0, 6))

        self._btn_settings = self._make_secondary_btn(row, "settings", self._open_settings)
        self._btn_settings.pack(side="right")

    def _make_secondary_btn(self, parent, key: str, cmd) -> tk.Button:
        return tk.Button(
            parent, text=self._t(key),
            bg=C["surface2"], fg=C["text_dim"],
            activebackground=C["surface"], activeforeground=C["text"],
            relief="flat", bd=0, padx=14, pady=10,
            font=("Segoe UI", 10),
            command=cmd,
        )

    # ── Barra de estado ───────────────────────────────────────────────────────
    def _build_statusbar(self) -> None:
        bar = tk.Frame(self._root, bg=C["surface2"], height=24)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)

        tk.Label(
            bar, textvariable=self._status,
            bg=C["surface2"], fg=C["text_dim"],
            font=("Segoe UI", 8), anchor="w",
        ).pack(side="left", padx=10, fill="y")

        tk.Label(
            bar, text=f"Pharos v{VERSION}",
            bg=C["surface2"], fg=C["text_dim"],
            font=("Segoe UI", 8), anchor="e",
        ).pack(side="right", padx=10, fill="y")

    # ══════════════════════════════════════════════════════════════════════════
    # Acciones del usuario
    # ══════════════════════════════════════════════════════════════════════════
    def _choose_folder(self) -> None:
        path = filedialog.askdirectory(initialdir=self._save_dir.get())
        if path:
            self._save_dir.set(path)

    def _open_logs(self) -> None:
        if self._log_win and self._log_win.winfo_exists():
            self._log_win.lift()
            return
        self._log_win = LogWindow(self._root, self._t)
        self._log_win.write(f"Pharos v{VERSION} – log\n{'─' * 60}\n")

    def _open_settings(self) -> None:
        SettingsWindow(
            parent=self._root,
            settings=self._settings,
            translator=self._t,
            on_save=self._apply_language,
        )

    def toggle_fullscreen(self) -> None:
        self._is_fullscreen = not self._is_fullscreen
        self._root.attributes("-fullscreen", self._is_fullscreen)
        label = self._t("minimize") if self._is_fullscreen else self._t("fullscreen")
        self._btn_fullscreen.configure(text=label)

    def _exit_fullscreen(self) -> None:
        if self._is_fullscreen:
            self._is_fullscreen = False
            self._root.attributes("-fullscreen", False)
            self._btn_fullscreen.configure(text=self._t("fullscreen"))

    # ── Vista previa ──────────────────────────────────────────────────────────
    def _open_preview(self) -> None:
        url = self._entry_url.get().strip()
        if not url:
            messagebox.showwarning(self._t("no_link_title"), self._t("no_link"))
            return
        webbrowser.open(url)
        self._draw_placeholder()
        self._lbl_title.configure(text=self._t("preview_loading"))
        self._lbl_meta.configure(text="")
        threading.Thread(target=self._fetch_meta, args=(url,), daemon=True).start()

    def _fetch_meta(self, url: str) -> None:
        """Obtiene título, canal, duración y miniatura con yt-dlp."""
        import sys, os
        base  = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        ytdlp = os.path.join(base, "yt-dlp.exe")
        if not os.path.exists(ytdlp):
            ytdlp = "yt-dlp"
        try:
            flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
            result = subprocess.run(
                [ytdlp, "--print",
                 "%(title)s|||%(uploader)s|||%(duration_string)s|||%(thumbnail)s",
                 "--no-playlist", url],
                capture_output=True, text=True, encoding="utf-8",
                errors="replace", timeout=15, creationflags=flags,
            )
            parts = result.stdout.strip().split("\n")[0].split("|||")
            title    = parts[0] if len(parts) > 0 else "—"
            uploader = parts[1] if len(parts) > 1 else ""
            duration = parts[2] if len(parts) > 2 else ""
            thumb    = parts[3] if len(parts) > 3 else ""
            meta = f"📺 {uploader}  •  ⏱ {duration}" if uploader else duration

            self._root.after(0, self._lbl_title.configure, {"text": title[:80]})
            self._root.after(0, self._lbl_meta.configure,  {"text": meta})

            if thumb:
                self._load_thumbnail(thumb)
        except Exception:
            pass

    def _load_thumbnail(self, thumb_url: str) -> None:
        try:
            from PIL import Image, ImageTk
            import io
            req = urllib.request.Request(thumb_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=8) as r:
                img_data = r.read()
            img   = Image.open(io.BytesIO(img_data)).resize((320, 180), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)

            def _show():
                self._canvas.image = photo
                self._canvas.create_image(0, 0, anchor="nw", image=photo)

            self._root.after(0, _show)
        except Exception:
            pass

    def _draw_placeholder(self) -> None:
        self._canvas.delete("all")
        self._canvas.create_rectangle(0, 0, 320, 180, fill=C["surface2"], outline="")
        self._canvas.create_polygon(120, 60, 120, 120, 200, 90, fill=C["border"], outline="")
        self._canvas.create_text(
            160, 150,
            text=self._t("preview_placeholder"),
            fill=C["text_dim"], font=("Segoe UI", 9),
        )

    # ── Descarga ──────────────────────────────────────────────────────────────
    def _start_download(self) -> None:
        url = self._entry_url.get().strip()
        if not url:
            messagebox.showwarning(self._t("no_link_title"), self._t("no_link"))
            return
        self._open_logs()
        self._btn_download.configure(state="disabled", bg=C["accent_dark"])
        self._progress.start(12)

        q_key = list(QUALITY_FLAGS.keys())[self._cb_quality.current()]
        self._downloader.start(
            url=url,
            quality_key=q_key,
            save_dir=self._save_dir.get(),
        )

    def _on_download_line(self, text: str) -> None:
        """Callback: recibe cada línea de salida de yt-dlp."""
        line = text.strip().split("\n")[0]
        if line:
            self._root.after(0, self._status.set, line[:120])
        if self._log_win and self._log_win.winfo_exists():
            self._root.after(0, self._log_win.write, text)

    def _on_download_done(self, success: bool) -> None:
        """Callback: descarga terminó."""
        msg = self._t("done") if success else self._t("error_download")
        self._on_download_line(msg)

        def _reset():
            self._btn_download.configure(state="normal", bg=C["accent"])
            self._progress.stop()
            self._status.set(self._t("status_ready"))

        self._root.after(0, _reset)

    # ── Actualizaciones ───────────────────────────────────────────────────────
    def _manual_update(self) -> None:
        self._status.set(self._t("update_checking"))
        self._updater.check(startup=False)

    def _on_update_found(self, ver: str, url: str) -> None:
        def _ask():
            msg = self._t("update_found", ver=ver, cur=VERSION)
            if messagebox.askyesno(self._t("update_title"), msg):
                webbrowser.open(url)
            self._status.set(self._t("status_ready"))
        self._root.after(0, _ask)

    def _on_no_update(self, ver: str) -> None:
        def _show():
            messagebox.showinfo(
                self._t("update_title"),
                self._t("update_none", ver=ver),
            )
            self._status.set(self._t("status_ready"))
        self._root.after(0, _show)

    def _on_update_error(self, error: str) -> None:
        def _show():
            messagebox.showwarning(
                self._t("update_title"),
                self._t("update_error", err=error),
            )
            self._status.set(self._t("status_ready"))
        self._root.after(0, _show)

    # ── Idioma ────────────────────────────────────────────────────────────────
    def _apply_language(self, lang: str) -> None:
        self._t.set_language(lang)
        self._refresh_labels()

    def _refresh_labels(self) -> None:
        """Re-aplica todos los textos traducibles de la UI."""
        self._root.title(self._t("title"))
        self._lbl_link.configure(text=self._t("video_link"))
        self._lbl_quality.configure(text=self._t("quality"))
        self._lbl_save.configure(text=self._t("save_in"))
        self._btn_choose.configure(text=self._t("choose"))
        self._btn_preview.configure(text=self._t("preview"))
        self._btn_download.configure(text=self._t("download"))
        self._btn_logs.configure(text=self._t("logs"))
        self._btn_updates.configure(text=self._t("check_updates"))
        self._btn_settings.configure(text=self._t("settings"))
        self._btn_fullscreen.configure(text=self._t("fullscreen"))
        self._btn_minimize.configure(text=self._t("minimize"))
        # Combobox calidades
        idx = self._cb_quality.current()
        self._cb_quality["values"] = [self._t(k) for k in QUALITY_FLAGS]
        self._cb_quality.current(idx)
        self._draw_placeholder()

