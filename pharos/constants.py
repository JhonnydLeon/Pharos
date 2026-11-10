"""
constants.py
============
Todas las constantes globales de Pharos:
versión, repositorio GitHub, calidades de descarga y paleta de colores.

Principio SOLID aplicado:
  S – Single Responsibility: este módulo SOLO almacena constantes;
      ninguna lógica vive aquí.
"""

# ── Versión y GitHub ─────────────────────────────────────────────────────────
APP_NAME    = "Pharos"
VERSION     = "1.0.0"
GITHUB_REPO = "JhonnydLeon/Pharos"           # ← tu usuario/repo en GitHub
GITHUB_API  = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"

# ── Calidades de descarga ─────────────────────────────────────────────────────
# Clave interna → flags que se pasan a yt-dlp
QUALITY_FLAGS: dict[str, list[str]] = {
    "1080p": ["-S", "res:1080,ext:mp4:m4a", "--merge-output-format", "mp4"],
    "720p":  ["-S", "res:720,ext:mp4:m4a",  "--merge-output-format", "mp4"],
    "480p":  ["-S", "res:480,ext:mp4:m4a",  "--merge-output-format", "mp4"],
    "audio": ["-x", "--audio-format", "mp3"],
}

# ── Paleta de colores ─────────────────────────────────────────────────────────
COLORS: dict[str, str] = {
    "bg":           "#1a1a1a",
    "surface":      "#242424",
    "surface2":     "#2e2e2e",
    "accent":       "#e02020",
    "accent_dark":  "#a01414",
    "accent_hover": "#ff3333",
    "text":         "#f0f0f0",
    "text_dim":     "#a0a0a0",
    "border":       "#3a3a3a",
    "log_bg":       "#0f0f0f",
    "log_fg":       "#cccccc",
    "success":      "#44cc44",
    "warning":      "#ffaa22",
    "error":        "#ff4444",
}

