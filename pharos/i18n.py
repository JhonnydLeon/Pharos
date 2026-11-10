"""
i18n.py
=======
Internacionalización (i18n) de Pharos.

Contiene:
  - TRANSLATIONS : diccionario con todos los textos en cada idioma.
  - Translator   : clase que encapsula la lógica de traducción.

Principios SOLID aplicados:
  S – Single Responsibility: solo gestiona traducciones, nada más.
  O – Open/Closed: agregar un nuevo idioma solo requiere añadir
      una clave a TRANSLATIONS, sin tocar la clase Translator.
"""

TRANSLATIONS: dict[str, dict[str, str]] = {
    "es": {
        # Ventana principal
        "title":                "Pharos – Descargador de Videos",
        "video_link":           "🔗  Link del video:",
        "quality":              "Calidad:",
        "save_in":              "Guardar en:",
        "choose":               "Elegir…",
        "preview":              "▶  Vista previa",
        "download":             "⬇  Descargar",
        "language":             "Idioma:",
        "logs":                 "Registros / Logs",
        "check_updates":        "Buscar actualizaciones",
        "fullscreen":           "Pantalla completa",
        "minimize":             "Minimizar",
        "settings":             "⚙  Preferencias",
        # Mensajes de descarga
        "no_link":              "Pega el link del video primero.",
        "no_link_title":        "Falta el link",
        "done":                 "\n✅  ¡Descarga completada!\n",
        "error_download":       "\n❌  Error. Revisa los registros.\n",
        "no_ytdlp":             "\n⚠  No se encontró yt-dlp. Instálalo o ponlo junto al programa.\n",
        # Vista previa
        "preview_note":         "🌐  Abriendo vista previa en el navegador…\n",
        "preview_loading":      "⏳ Cargando…",
        "preview_placeholder":  "Vista previa",
        # Actualizaciones
        "update_checking":      "🔍  Buscando actualizaciones…",
        "update_found":         "🎉  Nueva versión disponible: {ver}\nActual: {cur}\n¿Ir a la página de descarga?",
        "update_none":          "✅  Ya tienes la versión más reciente ({ver}).",
        "update_error":         "⚠  No se pudo verificar actualizaciones:\n{err}",
        "update_title":         "Actualizaciones",
        "startup_update":       "🎉  Pharos {ver} está disponible.\n¿Deseas ir a la página de descarga?",
        "startup_title":        "Actualización disponible",
        # Preferencias
        "pref_startup_update":  "Buscar actualizaciones al iniciar",
        "pref_save":            "💾  Guardar",
        # Calidades (etiquetas visibles)
        "1080p":                "1080p (mp4)",
        "720p":                 "720p (mp4)",
        "480p":                 "480p (mp4)",
        "audio":                "Solo audio (mp3)",
        # Barra de estado
        "status_ready":         "Pharos listo.",
    },
    "en": {
        "title":                "Pharos – Video Downloader",
        "video_link":           "🔗  Video link:",
        "quality":              "Quality:",
        "save_in":              "Save to:",
        "choose":               "Choose…",
        "preview":              "▶  Preview",
        "download":             "⬇  Download",
        "language":             "Language:",
        "logs":                 "Logs",
        "check_updates":        "Check for updates",
        "fullscreen":           "Fullscreen",
        "minimize":             "Minimize",
        "settings":             "⚙  Settings",
        "no_link":              "Please paste the video link first.",
        "no_link_title":        "Missing link",
        "done":                 "\n✅  Download completed!\n",
        "error_download":       "\n❌  Error. Check the logs.\n",
        "no_ytdlp":             "\n⚠  yt-dlp not found. Install it or place it next to the program.\n",
        "preview_note":         "🌐  Opening preview in browser…\n",
        "preview_loading":      "⏳ Loading…",
        "preview_placeholder":  "Preview",
        "update_checking":      "🔍  Checking for updates…",
        "update_found":         "🎉  New version available: {ver}\nCurrent: {cur}\nGo to the download page?",
        "update_none":          "✅  You have the latest version ({ver}).",
        "update_error":         "⚠  Could not check for updates:\n{err}",
        "update_title":         "Updates",
        "startup_update":       "🎉  Pharos {ver} is available.\nDo you want to go to the download page?",
        "startup_title":        "Update available",
        "pref_startup_update":  "Check for updates on startup",
        "pref_save":            "💾  Save",
        "1080p":                "1080p (mp4)",
        "720p":                 "720p (mp4)",
        "480p":                 "480p (mp4)",
        "audio":                "Audio only (mp3)",
        "status_ready":         "Pharos ready.",
    },
}

SUPPORTED_LANGUAGES = list(TRANSLATIONS.keys())


class Translator:
    """
    Encapsula la traducción de claves a texto según el idioma activo.

    Uso:
        t = Translator("es")
        t("download")                        # "⬇  Descargar"
        t("update_found", ver="1.1.0", cur="1.0.0")
    """

    def __init__(self, language: str = "es") -> None:
        self._lang = language
        self._table = TRANSLATIONS.get(language, TRANSLATIONS["es"])

    # ── Propiedades ───────────────────────────────────────────────────────────
    @property
    def language(self) -> str:
        return self._lang

    # ── Métodos públicos ──────────────────────────────────────────────────────
    def set_language(self, language: str) -> None:
        """Cambia el idioma activo en caliente."""
        self._lang  = language
        self._table = TRANSLATIONS.get(language, TRANSLATIONS["es"])

    def __call__(self, key: str, **kwargs: str) -> str:
        """Traduce una clave, con soporte de interpolación de variables."""
        text = self._table.get(key, key)
        return text.format(**kwargs) if kwargs else text
