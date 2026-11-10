"""
i18n.py
=======
Internacionalización (i18n) de Pharos.

Principios SOLID:
  S – Solo gestiona traducciones.
  O – Agregar idioma = añadir clave a TRANSLATIONS. Sin tocar Translator.
"""

# Nombre visible en el combobox → código interno
LANGUAGE_NAMES: dict[str, str] = {
    "Español":    "es",
    "English":    "en",
    "Português":  "pt",
    "Français":   "fr",
    "Deutsch":    "de",
}

# Código → nombre visible (inverso, útil para selección inicial)
LANGUAGE_DISPLAY: dict[str, str] = {v: k for k, v in LANGUAGE_NAMES.items()}

TRANSLATIONS: dict[str, dict[str, str]] = {
    # ── Español ───────────────────────────────────────────────────────────────
    "es": {
        "title":               "Pharos – Descargador de Videos",
        "video_link":          "🔗  Link del video:",
        "quality":             "Calidad:",
        "save_in":             "Guardar en:",
        "choose":              "Elegir…",
        "preview":             "▶  Vista previa",
        "open_in_player":      "▶  Abrir en reproductor",
        "open_in_browser":     "🌐  Ver en navegador",
        "download":            "⬇  Descargar",
        "language":            "🌐 Idioma",
        "logs":                "Registros / Logs",
        "check_updates":       "Buscar actualizaciones",
        "fullscreen":          "Pantalla completa",
        "minimize":            "Minimizar",
        "settings":            "⚙  Preferencias",
        "no_link":             "Pega el link del video primero.",
        "no_link_title":       "Falta el link",
        "done":                "\n✅  ¡Descarga completada!\n",
        "error_download":      "\n❌  Error. Revisa los registros.\n",
        "no_ytdlp":            "\n⚠  No se encontró yt-dlp. Instálalo o ponlo junto al programa.\n",
        "preview_loading":     "⏳ Cargando…",
        "preview_placeholder": "Vista previa",
        "opening_player":      "▶  Abriendo en reproductor…",
        "player_fallback":     "▶  Abriendo en navegador (VLC no encontrado)…",
        "update_checking":     "🔍  Buscando actualizaciones…",
        "update_found":        "Nueva versión disponible",
        "update_found_body":   "🎉  Pharos {ver} está disponible.\nTienes la versión {cur}.",
        "update_none":         "Ya tienes la última versión",
        "update_none_body":    "✅  Pharos {ver} está al día.",
        "update_error":        "No se pudo verificar",
        "update_error_body":   "⚠  {err}",
        "update_title":        "Actualizaciones",
        "startup_update":      "Actualización disponible",
        "startup_update_body": "🎉  Pharos {ver} está disponible.",
        "go_to_download":      "Ir a descargar",
        "cancel":              "Cancelar",
        "ok":                  "OK",
        "pref_startup_update": "Buscar actualizaciones al iniciar",
        "pref_save":           "💾  Guardar",
        "1080p":               "1080p (mp4)",
        "720p":                "720p (mp4)",
        "480p":                "480p (mp4)",
        "audio":               "Solo audio (mp3)",
        "status_ready":        "Pharos listo.",
    },
    # ── English ───────────────────────────────────────────────────────────────
    "en": {
        "title":               "Pharos – Video Downloader",
        "video_link":          "🔗  Video link:",
        "quality":             "Quality:",
        "save_in":             "Save to:",
        "choose":              "Choose…",
        "preview":             "▶  Preview",
        "open_in_player":      "▶  Open in player",
        "open_in_browser":     "🌐  Open in browser",
        "download":            "⬇  Download",
        "language":            "🌐 Language",
        "logs":                "Logs",
        "check_updates":       "Check for updates",
        "fullscreen":          "Fullscreen",
        "minimize":            "Minimize",
        "settings":            "⚙  Settings",
        "no_link":             "Please paste the video link first.",
        "no_link_title":       "Missing link",
        "done":                "\n✅  Download completed!\n",
        "error_download":      "\n❌  Error. Check the logs.\n",
        "no_ytdlp":            "\n⚠  yt-dlp not found. Install it or place it next to the program.\n",
        "preview_loading":     "⏳ Loading…",
        "preview_placeholder": "Preview",
        "opening_player":      "▶  Opening in player…",
        "player_fallback":     "▶  Opening in browser (VLC not found)…",
        "update_checking":     "🔍  Checking for updates…",
        "update_found":        "New version available",
        "update_found_body":   "🎉  Pharos {ver} is available.\nYou have version {cur}.",
        "update_none":         "You're up to date",
        "update_none_body":    "✅  Pharos {ver} is up to date.",
        "update_error":        "Could not check for updates",
        "update_error_body":   "⚠  {err}",
        "update_title":        "Updates",
        "startup_update":      "Update available",
        "startup_update_body": "🎉  Pharos {ver} is available.",
        "go_to_download":      "Download now",
        "cancel":              "Cancel",
        "ok":                  "OK",
        "pref_startup_update": "Check for updates on startup",
        "pref_save":           "💾  Save",
        "1080p":               "1080p (mp4)",
        "720p":                "720p (mp4)",
        "480p":                "480p (mp4)",
        "audio":               "Audio only (mp3)",
        "status_ready":        "Pharos ready.",
    },
    # ── Português ─────────────────────────────────────────────────────────────
    "pt": {
        "title":               "Pharos – Baixador de Vídeos",
        "video_link":          "🔗  Link do vídeo:",
        "quality":             "Qualidade:",
        "save_in":             "Salvar em:",
        "choose":              "Escolher…",
        "preview":             "▶  Pré-visualizar",
        "open_in_player":      "▶  Abrir no reprodutor",
        "open_in_browser":     "🌐  Ver no navegador",
        "download":            "⬇  Baixar",
        "language":            "🌐 Idioma",
        "logs":                "Registros / Logs",
        "check_updates":       "Verificar atualizações",
        "fullscreen":          "Tela cheia",
        "minimize":            "Minimizar",
        "settings":            "⚙  Preferências",
        "no_link":             "Cole o link do vídeo primeiro.",
        "no_link_title":       "Link ausente",
        "done":                "\n✅  Download concluído!\n",
        "error_download":      "\n❌  Erro. Verifique os registros.\n",
        "no_ytdlp":            "\n⚠  yt-dlp não encontrado. Instale-o ou coloque-o junto ao programa.\n",
        "preview_loading":     "⏳ Carregando…",
        "preview_placeholder": "Pré-visualização",
        "opening_player":      "▶  Abrindo no reprodutor…",
        "player_fallback":     "▶  Abrindo no navegador (VLC não encontrado)…",
        "update_checking":     "🔍  Verificando atualizações…",
        "update_found":        "Nova versão disponível",
        "update_found_body":   "🎉  Pharos {ver} está disponível.\nVocê tem a versão {cur}.",
        "update_none":         "Você está atualizado",
        "update_none_body":    "✅  Pharos {ver} está em dia.",
        "update_error":        "Não foi possível verificar",
        "update_error_body":   "⚠  {err}",
        "update_title":        "Atualizações",
        "startup_update":      "Atualização disponível",
        "startup_update_body": "🎉  Pharos {ver} está disponível.",
        "go_to_download":      "Baixar agora",
        "cancel":              "Cancelar",
        "ok":                  "OK",
        "pref_startup_update": "Verificar atualizações ao iniciar",
        "pref_save":           "💾  Salvar",
        "1080p":               "1080p (mp4)",
        "720p":                "720p (mp4)",
        "480p":                "480p (mp4)",
        "audio":               "Somente áudio (mp3)",
        "status_ready":        "Pharos pronto.",
    },
    # ── Français ──────────────────────────────────────────────────────────────
    "fr": {
        "title":               "Pharos – Téléchargeur de Vidéos",
        "video_link":          "🔗  Lien de la vidéo :",
        "quality":             "Qualité :",
        "save_in":             "Enregistrer dans :",
        "choose":              "Choisir…",
        "preview":             "▶  Aperçu",
        "open_in_player":      "▶  Ouvrir dans le lecteur",
        "open_in_browser":     "🌐  Voir dans le navigateur",
        "download":            "⬇  Télécharger",
        "language":            "🌐 Langue",
        "logs":                "Journaux / Logs",
        "check_updates":       "Vérifier les mises à jour",
        "fullscreen":          "Plein écran",
        "minimize":            "Réduire",
        "settings":            "⚙  Préférences",
        "no_link":             "Collez d'abord le lien de la vidéo.",
        "no_link_title":       "Lien manquant",
        "done":                "\n✅  Téléchargement terminé !\n",
        "error_download":      "\n❌  Erreur. Vérifiez les journaux.\n",
        "no_ytdlp":            "\n⚠  yt-dlp introuvable. Installez-le ou placez-le à côté du programme.\n",
        "preview_loading":     "⏳ Chargement…",
        "preview_placeholder": "Aperçu",
        "opening_player":      "▶  Ouverture dans le lecteur…",
        "player_fallback":     "▶  Ouverture dans le navigateur (VLC introuvable)…",
        "update_checking":     "🔍  Recherche de mises à jour…",
        "update_found":        "Nouvelle version disponible",
        "update_found_body":   "🎉  Pharos {ver} est disponible.\nVous avez la version {cur}.",
        "update_none":         "Vous êtes à jour",
        "update_none_body":    "✅  Pharos {ver} est à jour.",
        "update_error":        "Impossible de vérifier",
        "update_error_body":   "⚠  {err}",
        "update_title":        "Mises à jour",
        "startup_update":      "Mise à jour disponible",
        "startup_update_body": "🎉  Pharos {ver} est disponible.",
        "go_to_download":      "Télécharger",
        "cancel":              "Annuler",
        "ok":                  "OK",
        "pref_startup_update": "Vérifier les mises à jour au démarrage",
        "pref_save":           "💾  Enregistrer",
        "1080p":               "1080p (mp4)",
        "720p":                "720p (mp4)",
        "480p":                "480p (mp4)",
        "audio":               "Audio seulement (mp3)",
        "status_ready":        "Pharos prêt.",
    },
    # ── Deutsch ───────────────────────────────────────────────────────────────
    "de": {
        "title":               "Pharos – Video-Downloader",
        "video_link":          "🔗  Video-Link:",
        "quality":             "Qualität:",
        "save_in":             "Speichern in:",
        "choose":              "Wählen…",
        "preview":             "▶  Vorschau",
        "open_in_player":      "▶  Im Player öffnen",
        "open_in_browser":     "🌐  Im Browser öffnen",
        "download":            "⬇  Herunterladen",
        "language":            "🌐 Sprache",
        "logs":                "Protokoll / Logs",
        "check_updates":       "Nach Updates suchen",
        "fullscreen":          "Vollbild",
        "minimize":            "Minimieren",
        "settings":            "⚙  Einstellungen",
        "no_link":             "Bitte füge zuerst den Video-Link ein.",
        "no_link_title":       "Link fehlt",
        "done":                "\n✅  Download abgeschlossen!\n",
        "error_download":      "\n❌  Fehler. Protokoll prüfen.\n",
        "no_ytdlp":            "\n⚠  yt-dlp nicht gefunden. Installiere es oder lege es neben das Programm.\n",
        "preview_loading":     "⏳ Wird geladen…",
        "preview_placeholder": "Vorschau",
        "opening_player":      "▶  Im Player wird geöffnet…",
        "player_fallback":     "▶  Im Browser öffnen (VLC nicht gefunden)…",
        "update_checking":     "🔍  Suche nach Updates…",
        "update_found":        "Neue Version verfügbar",
        "update_found_body":   "🎉  Pharos {ver} ist verfügbar.\nDu hast Version {cur}.",
        "update_none":         "Du bist aktuell",
        "update_none_body":    "✅  Pharos {ver} ist auf dem neuesten Stand.",
        "update_error":        "Updates konnten nicht geprüft werden",
        "update_error_body":   "⚠  {err}",
        "update_title":        "Updates",
        "startup_update":      "Update verfügbar",
        "startup_update_body": "🎉  Pharos {ver} ist verfügbar.",
        "go_to_download":      "Jetzt herunterladen",
        "cancel":              "Abbrechen",
        "ok":                  "OK",
        "pref_startup_update": "Beim Start nach Updates suchen",
        "pref_save":           "💾  Speichern",
        "1080p":               "1080p (mp4)",
        "720p":                "720p (mp4)",
        "480p":                "480p (mp4)",
        "audio":               "Nur Audio (mp3)",
        "status_ready":        "Pharos bereit.",
    },
}

SUPPORTED_LANGUAGES = list(TRANSLATIONS.keys())


class Translator:
    """
    Encapsula la traducción de claves a texto según el idioma activo.

    Uso:
        t = Translator("es")
        t("download")                          # "⬇  Descargar"
        t("update_found_body", ver="1.1", cur="1.0")
    """

    def __init__(self, language: str = "es") -> None:
        self._lang  = language
        self._table = TRANSLATIONS.get(language, TRANSLATIONS["es"])

    @property
    def language(self) -> str:
        return self._lang

    def set_language(self, language: str) -> None:
        """Cambia el idioma activo en caliente."""
        self._lang  = language
        self._table = TRANSLATIONS.get(language, TRANSLATIONS["es"])

    def __call__(self, key: str, **kwargs) -> str:
        """Traduce una clave con interpolación opcional de variables."""
        text = self._table.get(key, key)
        return text.format(**kwargs) if kwargs else text
