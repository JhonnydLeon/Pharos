"""
Pharos - Descargador de videos
Powered by yt-dlp + ffmpeg
"""

import os
import re
import sys
import json
import time
import threading
import subprocess
import urllib.request
import urllib.error
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# ─────────────────────────── Versión ────────────────────────────
__version__ = "1.0.0"
GITHUB_REPO = "JhonnydLeon/Pharos"   # ← cambia esto a tu usuario/repo real
GITHUB_API  = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"

# ─────────────────────────── i18n ───────────────────────────────
TRANSLATIONS = {
    "es": {
        # Ventana principal
        "title":           "Pharos – Descargador de Videos",
        "video_link":      "🔗  Link del video:",
        "quality":         "Calidad:",
        "save_in":         "Guardar en:",
        "choose":          "Elegir…",
        "preview":         "▶  Vista previa",
        "download":        "⬇  Descargar",
        "language":        "Idioma:",
        "logs":            "Registros / Logs",
        "check_updates":   "Buscar actualizaciones",
        "fullscreen":      "Pantalla completa",
        "minimize":        "Minimizar",
        # Mensajes
        "no_link":         "Pega el link del video primero.",
        "no_link_title":   "Falta el link",
        "done":            "\n✅  ¡Descarga completada!\n",
        "error":           "\n❌  Error. Revisa los registros.\n",
        "no_ytdlp":        "\n⚠  No se encontró yt-dlp. Instálalo o ponlo junto al programa.\n",
        "preview_note":    "🌐  Abriendo vista previa en el navegador…\n",
        "update_check":    "🔍  Buscando actualizaciones…",
        "update_found":    "🎉  Nueva versión disponible: {ver}\nActual: {cur}\n¿Ir a la página de descarga?",
        "update_none":     "✅  Ya tienes la versión más reciente ({ver}).",
        "update_error":    "⚠  No se pudo verificar actualizaciones:\n{err}",
        "update_title":    "Actualizaciones",
        "startup_update":  "🎉  Pharos {ver} está disponible.\n¿Deseas ir a la página de descarga?",
        "startup_title":   "Actualización disponible",
        # Calidades
        "1080p":           "1080p (mp4)",
        "720p":            "720p (mp4)",
        "480p":            "480p (mp4)",
        "audio":           "Solo audio (mp3)",
        # Preferencias
        "pref_startup_update": "Buscar actualizaciones al iniciar",
        "settings":        "⚙  Preferencias",
    },
    "en": {
        "title":           "Pharos – Video Downloader",
        "video_link":      "🔗  Video link:",
        "quality":         "Quality:",
        "save_in":         "Save to:",
        "choose":          "Choose…",
        "preview":         "▶  Preview",
        "download":        "⬇  Download",
        "language":        "Language:",
        "logs":            "Logs",
        "check_updates":   "Check for updates",
        "fullscreen":      "Fullscreen",
        "minimize":        "Minimize",
        "no_link":         "Please paste the video link first.",
        "no_link_title":   "Missing link",
        "done":            "\n✅  Download completed!\n",
        "error":           "\n❌  Error. Check the logs.\n",
        "no_ytdlp":        "\n⚠  yt-dlp not found. Install it or place it next to the program.\n",
        "preview_note":    "🌐  Opening preview in browser…\n",
        "update_check":    "🔍  Checking for updates…",
        "update_found":    "🎉  New version available: {ver}\nCurrent: {cur}\nGo to the download page?",
        "update_none":     "✅  You have the latest version ({ver}).",
        "update_error":    "⚠  Could not check for updates:\n{err}",
        "update_title":    "Updates",
        "startup_update":  "🎉  Pharos {ver} is available.\nDo you want to go to the download page?",
        "startup_title":   "Update available",
        "1080p":           "1080p (mp4)",
        "720p":            "720p (mp4)",
        "480p":            "480p (mp4)",
        "audio":           "Audio only (mp3)",
        "pref_startup_update": "Check for updates on startup",
        "settings":        "⚙  Settings",
    },
}

QUALITY_FLAGS = {
    "1080p": ["-S", "res:1080,ext:mp4:m4a", "--merge-output-format", "mp4"],
    "720p":  ["-S", "res:720,ext:mp4:m4a",  "--merge-output-format", "mp4"],
    "480p":  ["-S", "res:480,ext:mp4:m4a",  "--merge-output-format", "mp4"],
    "audio": ["-x", "--audio-format", "mp3"],
}

# ─────────────────────────── Paleta ─────────────────────────────
C = {
    "bg":          "#1a1a1a",
    "surface":     "#242424",
    "surface2":    "#2e2e2e",
    "accent":      "#e02020",
    "accent_dark": "#a01414",
    "accent_hover":"#ff3333",
    "text":        "#f0f0f0",
    "text_dim":    "#a0a0a0",
    "border":      "#3a3a3a",
    "log_bg":      "#0f0f0f",
    "log_fg":      "#cccccc",
    "success":     "#44cc44",
    "warning":     "#ffaa22",
    "error":       "#ff4444",
}

SETTINGS_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "pharos_settings.json"
)


# ─────────────────────────── Helpers ────────────────────────────
def carpeta_base():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def load_settings():
    defaults = {"language": "es", "check_updates_on_startup": True}
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            defaults.update(data)
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return defaults


def save_settings(data: dict):
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except OSError:
        pass


def fetch_latest_version():
    """Consulta la API de GitHub y devuelve (tag_name, html_url).
    
    Retorna (None, None) si no hay releases publicadas (HTTP 404).
    Lanza excepción en cualquier otro error de red.
    """
    req = urllib.request.Request(
        GITHUB_API,
        headers={"User-Agent": f"Pharos/{__version__}"}
    )
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode())
        return data["tag_name"].lstrip("v"), data["html_url"]
    except urllib.error.HTTPError as e:
        if e.code == 404:
            # Sin releases publicadas → se trata como "sin actualizaciones"
            return None, None
        raise


# ─────────────────────────── Ventana de logs ────────────────────
class LogWindow(tk.Toplevel):
    def __init__(self, parent, t):
        super().__init__(parent)
        self.t = t
        self.title(t("logs"))
        self.geometry("700x400")
        self.configure(bg=C["bg"])
        self.resizable(True, True)

        self.text = tk.Text(
            self, state="disabled",
            bg=C["log_bg"], fg=C["log_fg"],
            font=("Consolas", 9), wrap="none",
            relief="flat", bd=0,
            selectbackground=C["accent"],
        )
        sb_v = ttk.Scrollbar(self, orient="vertical",   command=self.text.yview)
        sb_h = ttk.Scrollbar(self, orient="horizontal", command=self.text.xview)
        self.text.configure(yscrollcommand=sb_v.set, xscrollcommand=sb_h.set)

        sb_v.pack(side="right",  fill="y")
        sb_h.pack(side="bottom", fill="x")
        self.text.pack(fill="both", expand=True)

        # Botón limpiar
        btn = tk.Button(
            self, text="🗑  Limpiar", bg=C["surface2"], fg=C["text_dim"],
            activebackground=C["surface"], activeforeground=C["text"],
            relief="flat", bd=0, padx=10, pady=4,
            command=self.clear
        )
        btn.pack(pady=4)

    def write(self, text: str):
        self.text.configure(state="normal")
        self.text.insert("end", text)
        self.text.see("end")
        self.text.configure(state="disabled")

    def clear(self):
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        self.text.configure(state="disabled")


# ─────────────────────────── Ventana de preferencias ────────────
class SettingsWindow(tk.Toplevel):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        t = app.t
        self.title(t("settings"))
        self.geometry("360x180")
        self.configure(bg=C["bg"])
        self.resizable(False, False)
        self.grab_set()

        pad = {"padx": 18, "pady": 8}

        # Idioma
        frm = tk.Frame(self, bg=C["bg"])
        frm.pack(fill="x", **pad)
        tk.Label(frm, text=t("language"), bg=C["bg"], fg=C["text"],
                 font=("Segoe UI", 10)).pack(side="left")
        self.lang_var = tk.StringVar(value=app.settings["language"])
        lang_cb = ttk.Combobox(
            frm, textvariable=self.lang_var,
            values=["es", "en"], state="readonly", width=8
        )
        lang_cb.pack(side="left", padx=10)

        # Buscar actualizaciones al iniciar
        self.startup_var = tk.BooleanVar(value=app.settings.get("check_updates_on_startup", True))
        chk = tk.Checkbutton(
            self, text=t("pref_startup_update"),
            variable=self.startup_var,
            bg=C["bg"], fg=C["text"],
            activebackground=C["bg"], activeforeground=C["text"],
            selectcolor=C["surface2"],
            font=("Segoe UI", 10)
        )
        chk.pack(anchor="w", **pad)

        # Guardar
        btn_save = tk.Button(
            self, text="💾  Guardar / Save",
            bg=C["accent"], fg="white",
            activebackground=C["accent_hover"], activeforeground="white",
            relief="flat", bd=0, padx=16, pady=6,
            font=("Segoe UI", 10, "bold"),
            command=self.save
        )
        btn_save.pack(pady=12)

    def save(self):
        self.app.settings["language"] = self.lang_var.get()
        self.app.settings["check_updates_on_startup"] = self.startup_var.get()
        save_settings(self.app.settings)
        self.app.apply_language(self.lang_var.get())
        self.destroy()


# ─────────────────────────── App principal ──────────────────────
class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.settings = load_settings()
        self._lang   = self.settings.get("language", "es")
        self._tr     = TRANSLATIONS.get(self._lang, TRANSLATIONS["es"])

        self._is_fullscreen = False
        self._log_win: LogWindow | None = None

        self.carpeta = tk.StringVar(value=os.path.join(os.path.expanduser("~"), "Downloads"))
        self.calidad_key = tk.StringVar(value="1080p")

        self._build_styles()
        self._build_ui()
        self._apply_theme()

        # Buscar actualizaciones al inicio (en background)
        if self.settings.get("check_updates_on_startup", True):
            threading.Thread(target=self._startup_update_check, daemon=True).start()

    # ── traducción ───────────────────────────────────────────────
    def t(self, key: str, **kwargs) -> str:
        text = self._tr.get(key, key)
        return text.format(**kwargs) if kwargs else text

    def apply_language(self, lang: str):
        self._lang = lang
        self._tr   = TRANSLATIONS.get(lang, TRANSLATIONS["es"])
        self._refresh_texts()

    def _refresh_texts(self):
        """Re-aplica todos los textos traducibles."""
        self.root.title(self.t("title"))
        self.lbl_link.configure(text=self.t("video_link"))
        self.lbl_quality.configure(text=self.t("quality"))
        self.lbl_save.configure(text=self.t("save_in"))
        self.btn_choose.configure(text=self.t("choose"))
        self.btn_preview.configure(text=self.t("preview"))
        self.btn_download.configure(text=self.t("download"))
        self.btn_logs.configure(text=self.t("logs"))
        self.btn_updates.configure(text=self.t("check_updates"))
        self.btn_fullscreen.configure(text=self.t("fullscreen"))
        self.btn_minimize.configure(text=self.t("minimize"))
        self.btn_settings.configure(text=self.t("settings"))
        # Calidades del combobox
        q_labels = [self.t(k) for k in QUALITY_FLAGS]
        self.cb_quality["values"] = q_labels
        # mantener selección correcta
        idx = list(QUALITY_FLAGS.keys()).index(self.calidad_key.get())
        self.cb_quality.current(idx)

    # ── estilos ttk ─────────────────────────────────────────────
    def _build_styles(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure(".",
            background=C["bg"],
            foreground=C["text"],
            fieldbackground=C["surface2"],
            selectbackground=C["accent"],
            selectforeground="white",
            bordercolor=C["border"],
            troughcolor=C["surface"],
            font=("Segoe UI", 10),
        )
        self.style.configure("TFrame",   background=C["bg"])
        self.style.configure("TLabel",   background=C["bg"], foreground=C["text"])
        self.style.configure("TEntry",
            fieldbackground=C["surface2"],
            foreground=C["text"],
            insertcolor=C["text"],
        )
        self.style.map("TEntry", fieldbackground=[("focus", C["surface2"])])
        self.style.configure("TCombobox",
            fieldbackground=C["surface2"],
            background=C["surface2"],
            foreground=C["text"],
            arrowcolor=C["accent"],
        )
        self.style.map("TCombobox",
            fieldbackground=[("readonly", C["surface2"])],
            selectbackground=[("readonly", C["accent"])],
        )
        self.style.configure("TScrollbar",
            background=C["surface2"],
            troughcolor=C["surface"],
            arrowcolor=C["text_dim"],
        )

    # ── construcción de la UI ────────────────────────────────────
    def _build_ui(self):
        self.root.title(self.t("title"))
        self.root.geometry("780x560")
        self.root.minsize(640, 480)
        self.root.configure(bg=C["bg"])
        self.root.resizable(True, True)

        # ── Barra superior (título + controles) ──────────────────
        topbar = tk.Frame(self.root, bg=C["accent"], height=48)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)

        tk.Label(
            topbar, text="⚡ PHAROS",
            bg=C["accent"], fg="white",
            font=("Segoe UI Black", 14, "bold")
        ).pack(side="left", padx=16)

        # Versión
        tk.Label(
            topbar, text=f"v{__version__}",
            bg=C["accent"], fg="#ffcccc",
            font=("Segoe UI", 9)
        ).pack(side="left")

        # Controles de ventana (derecha)
        ctrl_frame = tk.Frame(topbar, bg=C["accent"])
        ctrl_frame.pack(side="right", padx=6)

        self.btn_minimize = tk.Button(
            ctrl_frame, text=self.t("minimize"),
            bg=C["accent_dark"], fg="white",
            activebackground=C["accent_hover"], activeforeground="white",
            relief="flat", bd=0, padx=10, pady=6,
            font=("Segoe UI", 9),
            command=self.root.iconify
        )
        self.btn_minimize.pack(side="left", padx=2)

        self.btn_fullscreen = tk.Button(
            ctrl_frame, text=self.t("fullscreen"),
            bg=C["accent_dark"], fg="white",
            activebackground=C["accent_hover"], activeforeground="white",
            relief="flat", bd=0, padx=10, pady=6,
            font=("Segoe UI", 9),
            command=self.toggle_fullscreen
        )
        self.btn_fullscreen.pack(side="left", padx=2)

        # ── Cuerpo ───────────────────────────────────────────────
        body = tk.Frame(self.root, bg=C["bg"])
        body.pack(fill="both", expand=True, padx=20, pady=16)

        # Sección: Link
        self.lbl_link = tk.Label(body, text=self.t("video_link"),
                                  bg=C["bg"], fg=C["text_dim"],
                                  font=("Segoe UI", 9, "bold"))
        self.lbl_link.pack(anchor="w")

        entry_frame = tk.Frame(body, bg=C["border"], bd=0)
        entry_frame.pack(fill="x", pady=(4, 14))
        self.url = tk.Entry(
            entry_frame, bg=C["surface2"], fg=C["text"],
            insertbackground=C["text"],
            relief="flat", bd=8,
            font=("Segoe UI", 11),
        )
        self.url.pack(fill="x")

        # Sección: Calidad + Guardar
        row1 = tk.Frame(body, bg=C["bg"])
        row1.pack(fill="x", pady=(0, 12))

        # Calidad
        col_q = tk.Frame(row1, bg=C["bg"])
        col_q.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.lbl_quality = tk.Label(col_q, text=self.t("quality"),
                                     bg=C["bg"], fg=C["text_dim"],
                                     font=("Segoe UI", 9, "bold"))
        self.lbl_quality.pack(anchor="w")
        self.cb_quality = ttk.Combobox(
            col_q,
            values=[self.t(k) for k in QUALITY_FLAGS],
            state="readonly", width=20,
            font=("Segoe UI", 10),
        )
        self.cb_quality.current(0)
        self.cb_quality.pack(anchor="w", pady=(4, 0))

        # Guardar en
        col_s = tk.Frame(row1, bg=C["bg"])
        col_s.pack(side="left", fill="x", expand=True)
        self.lbl_save = tk.Label(col_s, text=self.t("save_in"),
                                  bg=C["bg"], fg=C["text_dim"],
                                  font=("Segoe UI", 9, "bold"))
        self.lbl_save.pack(anchor="w")
        row_save = tk.Frame(col_s, bg=C["bg"])
        row_save.pack(fill="x", pady=(4, 0))
        self.entry_save = tk.Entry(
            row_save, textvariable=self.carpeta,
            bg=C["surface2"], fg=C["text"],
            insertbackground=C["text"],
            relief="flat", bd=6,
            font=("Segoe UI", 10),
        )
        self.entry_save.pack(side="left", fill="x", expand=True)
        self.btn_choose = tk.Button(
            row_save, text=self.t("choose"),
            bg=C["surface2"], fg=C["text_dim"],
            activebackground=C["surface"], activeforeground=C["text"],
            relief="flat", bd=0, padx=10, pady=5,
            font=("Segoe UI", 9),
            command=self.elegir_carpeta
        )
        self.btn_choose.pack(side="left", padx=(6, 0))

        # ── Vista previa del video ───────────────────────────────
        preview_frame = tk.Frame(body, bg=C["surface"], relief="flat", bd=0)
        preview_frame.pack(fill="x", pady=(0, 14))

        self.preview_canvas = tk.Canvas(
            preview_frame, bg=C["surface"],
            width=320, height=180, highlightthickness=0
        )
        self.preview_canvas.pack(side="left", padx=12, pady=12)
        self._draw_preview_placeholder()

        info_right = tk.Frame(preview_frame, bg=C["surface"])
        info_right.pack(side="left", fill="both", expand=True, pady=12, padx=(0, 12))

        self.lbl_video_title = tk.Label(
            info_right, text="—",
            bg=C["surface"], fg=C["text"],
            font=("Segoe UI", 10, "bold"),
            wraplength=340, justify="left", anchor="w"
        )
        self.lbl_video_title.pack(anchor="w")

        self.lbl_video_meta = tk.Label(
            info_right, text="",
            bg=C["surface"], fg=C["text_dim"],
            font=("Segoe UI", 9),
            wraplength=340, justify="left", anchor="w"
        )
        self.lbl_video_meta.pack(anchor="w", pady=(4, 0))

        self.btn_preview = tk.Button(
            info_right, text=self.t("preview"),
            bg=C["surface2"], fg=C["text_dim"],
            activebackground=C["accent_dark"], activeforeground="white",
            relief="flat", bd=0, padx=14, pady=6,
            font=("Segoe UI", 9),
            command=self.open_preview
        )
        self.btn_preview.pack(anchor="w", pady=(10, 0))

        # ── Barra de progreso ────────────────────────────────────
        self.progress = ttk.Progressbar(
            body, orient="horizontal", mode="indeterminate", length=100
        )
        self.progress.pack(fill="x", pady=(0, 10))

        # ── Botones de acción ────────────────────────────────────
        btn_row = tk.Frame(body, bg=C["bg"])
        btn_row.pack(fill="x", pady=(0, 4))

        self.btn_download = tk.Button(
            btn_row, text=self.t("download"),
            bg=C["accent"], fg="white",
            activebackground=C["accent_hover"], activeforeground="white",
            relief="flat", bd=0, padx=22, pady=10,
            font=("Segoe UI", 11, "bold"),
            cursor="hand2",
            command=self.iniciar
        )
        self.btn_download.pack(side="left", padx=(0, 10))

        self.btn_logs = tk.Button(
            btn_row, text=self.t("logs"),
            bg=C["surface2"], fg=C["text_dim"],
            activebackground=C["surface"], activeforeground=C["text"],
            relief="flat", bd=0, padx=14, pady=10,
            font=("Segoe UI", 10),
            command=self.open_logs
        )
        self.btn_logs.pack(side="left", padx=(0, 6))

        self.btn_updates = tk.Button(
            btn_row, text=self.t("check_updates"),
            bg=C["surface2"], fg=C["text_dim"],
            activebackground=C["surface"], activeforeground=C["text"],
            relief="flat", bd=0, padx=14, pady=10,
            font=("Segoe UI", 10),
            command=self.check_updates_manual
        )
        self.btn_updates.pack(side="left", padx=(0, 6))

        self.btn_settings = tk.Button(
            btn_row, text=self.t("settings"),
            bg=C["surface2"], fg=C["text_dim"],
            activebackground=C["surface"], activeforeground=C["text"],
            relief="flat", bd=0, padx=14, pady=10,
            font=("Segoe UI", 10),
            command=self.open_settings
        )
        self.btn_settings.pack(side="right")

        # ── Barra de estado ──────────────────────────────────────
        self.status_var = tk.StringVar(value="Pharos listo.")
        status_bar = tk.Frame(self.root, bg=C["surface2"], height=24)
        status_bar.pack(fill="x", side="bottom")
        status_bar.pack_propagate(False)
        tk.Label(
            status_bar, textvariable=self.status_var,
            bg=C["surface2"], fg=C["text_dim"],
            font=("Segoe UI", 8), anchor="w"
        ).pack(side="left", padx=10, fill="y")

        tk.Label(
            status_bar, text=f"Pharos v{__version__}",
            bg=C["surface2"], fg=C["text_dim"],
            font=("Segoe UI", 8), anchor="e"
        ).pack(side="right", padx=10, fill="y")

        # Atajo teclado F11
        self.root.bind("<F11>", lambda e: self.toggle_fullscreen())
        self.root.bind("<Escape>", lambda e: self._exit_fullscreen())

    def _apply_theme(self):
        """Configura colores del Combobox dropdown (widget interno de tk)."""
        try:
            self.root.tk.eval("""
                ttk::style configure TCombobox -padding {4 4}
            """)
        except Exception:
            pass

    # ── Vista previa (placeholder) ───────────────────────────────
    def _draw_preview_placeholder(self):
        c = self.preview_canvas
        c.delete("all")
        c.create_rectangle(0, 0, 320, 180, fill=C["surface2"], outline="")
        c.create_polygon(120, 60, 120, 120, 200, 90, fill=C["border"], outline="")
        c.create_text(160, 150, text="Vista previa",
                      fill=C["text_dim"], font=("Segoe UI", 9))

    def _fetch_thumbnail(self, url: str):
        """Intenta descargar el thumbnail con yt-dlp y mostrarlo (requiere Pillow)."""
        base  = carpeta_base()
        ytdlp = os.path.join(base, "yt-dlp.exe")
        if not os.path.exists(ytdlp):
            ytdlp = "yt-dlp"
        try:
            flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
            result = subprocess.run(
                [ytdlp, "--print", "%(title)s|||%(uploader)s|||%(duration_string)s|||%(thumbnail)s",
                 "--no-playlist", url],
                capture_output=True, text=True, encoding="utf-8",
                errors="replace", timeout=15, creationflags=flags
            )
            line = result.stdout.strip().split("\n")[0]
            parts = line.split("|||")
            title    = parts[0] if len(parts) > 0 else "—"
            uploader = parts[1] if len(parts) > 1 else ""
            duration = parts[2] if len(parts) > 2 else ""
            thumb    = parts[3] if len(parts) > 3 else ""

            meta = f"📺 {uploader}  •  ⏱ {duration}" if uploader else duration

            self.root.after(0, self.lbl_video_title.configure, {"text": title[:80]})
            self.root.after(0, self.lbl_video_meta.configure,  {"text": meta})

            # Intentar mostrar thumbnail si Pillow está disponible
            if thumb:
                try:
                    from PIL import Image, ImageTk
                    import io
                    req = urllib.request.Request(thumb, headers={"User-Agent": "Mozilla/5.0"})
                    with urllib.request.urlopen(req, timeout=8) as r:
                        img_data = r.read()
                    img = Image.open(io.BytesIO(img_data)).resize((320, 180), Image.LANCZOS)
                    photo = ImageTk.PhotoImage(img)

                    def _show():
                        self.preview_canvas.image = photo  # keep reference
                        self.preview_canvas.create_image(0, 0, anchor="nw", image=photo)

                    self.root.after(0, _show)
                except Exception:
                    pass  # Pillow no instalado – sin thumbnail, solo metadatos
        except Exception:
            pass

    def open_preview(self):
        url = self.url.get().strip()
        if not url:
            messagebox.showwarning(self.t("no_link_title"), self.t("no_link"))
            return
        self._write_log(self.t("preview_note"))
        # Abrir en navegador
        import webbrowser
        webbrowser.open(url)
        # Cargar metadatos en background
        self._draw_preview_placeholder()
        self.lbl_video_title.configure(text="⏳ Cargando…")
        self.lbl_video_meta.configure(text="")
        threading.Thread(target=self._fetch_thumbnail, args=(url,), daemon=True).start()

    # ── Logs ─────────────────────────────────────────────────────
    def _write_log(self, text: str):
        """Escribe en la ventana de logs (si está abierta) y en la barra de estado."""
        # Status bar: primera línea no vacía
        line = text.strip().split("\n")[0] if text.strip() else ""
        if line:
            self.root.after(0, self.status_var.set, line[:120])
        if self._log_win and self._log_win.winfo_exists():
            self.root.after(0, self._log_win.write, text)

    def open_logs(self):
        if self._log_win and self._log_win.winfo_exists():
            self._log_win.lift()
            return
        self._log_win = LogWindow(self.root, self.t)
        self._log_win.write(f"Pharos v{__version__} – log\n{'─'*60}\n")

    # ── Pantalla completa ────────────────────────────────────────
    def toggle_fullscreen(self):
        self._is_fullscreen = not self._is_fullscreen
        self.root.attributes("-fullscreen", self._is_fullscreen)
        label = self.t("minimize") if self._is_fullscreen else self.t("fullscreen")
        self.btn_fullscreen.configure(text=label)

    def _exit_fullscreen(self):
        if self._is_fullscreen:
            self._is_fullscreen = False
            self.root.attributes("-fullscreen", False)
            self.btn_fullscreen.configure(text=self.t("fullscreen"))

    # ── Carpeta ──────────────────────────────────────────────────
    def elegir_carpeta(self):
        c = filedialog.askdirectory(initialdir=self.carpeta.get())
        if c:
            self.carpeta.set(c)

    # ── Preferencias ─────────────────────────────────────────────
    def open_settings(self):
        SettingsWindow(self.root, self)

    # ── Actualizaciones ──────────────────────────────────────────
    def _startup_update_check(self):
        time.sleep(2)  # dar tiempo a que la UI arranque
        try:
            latest_ver, dl_url = fetch_latest_version()
            # latest_ver es None si no hay releases publicadas → sin aviso
            if latest_ver and self._version_newer(latest_ver, __version__):
                def _ask():
                    msg = self.t("startup_update", ver=latest_ver)
                    if messagebox.askyesno(self.t("startup_title"), msg):
                        import webbrowser
                        webbrowser.open(dl_url)
                self.root.after(0, _ask)
        except Exception:
            pass  # silencioso en arranque

    def check_updates_manual(self):
        self.status_var.set(self.t("update_check"))
        threading.Thread(target=self._do_update_check, daemon=True).start()

    def _do_update_check(self):
        try:
            latest_ver, dl_url = fetch_latest_version()
            if latest_ver is None:
                # No hay releases publicadas → misma respuesta que "al día"
                msg = self.t("update_none", ver=__version__)
                self.root.after(0, messagebox.showinfo, self.t("update_title"), msg)
            elif self._version_newer(latest_ver, __version__):
                msg = self.t("update_found", ver=latest_ver, cur=__version__)
                def _ask():
                    if messagebox.askyesno(self.t("update_title"), msg):
                        import webbrowser
                        webbrowser.open(dl_url)
                self.root.after(0, _ask)
            else:
                msg = self.t("update_none", ver=latest_ver)
                self.root.after(0, messagebox.showinfo, self.t("update_title"), msg)
        except Exception as e:
            msg = self.t("update_error", err=str(e))
            self.root.after(0, messagebox.showwarning, self.t("update_title"), msg)
        finally:
            self.root.after(0, self.status_var.set, "Pharos listo.")

    @staticmethod
    def _version_newer(remote: str, local: str) -> bool:
        """Compara versiones en formato X.Y.Z."""
        def to_tuple(v):
            try:
                return tuple(int(x) for x in re.split(r"[.\-]", v)[:3])
            except ValueError:
                return (0,)
        return to_tuple(remote) > to_tuple(local)

    # ── Descarga ─────────────────────────────────────────────────
    def iniciar(self):
        link = self.url.get().strip()
        if not link:
            messagebox.showwarning(self.t("no_link_title"), self.t("no_link"))
            return
        # Abrir logs automáticamente
        self.open_logs()
        self.btn_download.configure(state="disabled", bg=C["accent_dark"])
        self.progress.start(12)
        threading.Thread(target=self.descargar, args=(link,), daemon=True).start()

    def descargar(self, link: str):
        base  = carpeta_base()
        ytdlp = os.path.join(base, "yt-dlp.exe")
        if not os.path.exists(ytdlp):
            ytdlp = "yt-dlp"

        # Mapear etiqueta localizada → clave
        cb_idx = self.cb_quality.current()
        q_key  = list(QUALITY_FLAGS.keys())[cb_idx]
        flags  = QUALITY_FLAGS[q_key]

        cmd = [ytdlp, *flags,
               "--newline", "--no-playlist",
               "-P", self.carpeta.get(),
               "-o", "%(title)s.%(ext)s"]
        if os.path.exists(os.path.join(base, "ffmpeg.exe")):
            cmd += ["--ffmpeg-location", base]
        cmd.append(link)

        self._write_log(f"> {' '.join(cmd)}\n")
        try:
            flags_cf = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
            p = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, encoding="utf-8", errors="replace",
                creationflags=flags_cf
            )
            for linea in p.stdout:
                self._write_log(linea)
            p.wait()
            ok = p.returncode == 0
            msg = self.t("done") if ok else self.t("error")
            self._write_log(msg)
        except FileNotFoundError:
            self._write_log(self.t("no_ytdlp"))
        finally:
            def _reset():
                self.btn_download.configure(state="normal", bg=C["accent"])
                self.progress.stop()
                self.progress["value"] = 0
            self.root.after(0, _reset)


# ─────────────────────────── Punto de entrada ───────────────────
if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
