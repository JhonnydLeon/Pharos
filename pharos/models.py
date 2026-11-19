"""
models.py
=========
Dataclasses que representan los formatos y metadatos de un video.

Principio SOLID aplicado:
  S – Single Responsibility: solo define la estructura de datos.
      Ningún I/O, ningún subprocess, ningún tkinter aquí.
  O – Fácil de extender con nuevos campos sin romper lo existente.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


# ── Mapas de codecs a etiquetas legibles ──────────────────────────────────────
_VIDEO_CODEC_LABELS: dict[str, str] = {
    "avc1": "H.264",
    "avc":  "H.264",
    "h264": "H.264",
    "vp09": "VP9",
    "vp9":  "VP9",
    "av01": "AV1",
    "av1":  "AV1",
    "hvc1": "H.265",
    "hev1": "H.265",
}

_AUDIO_CODEC_LABELS: dict[str, str] = {
    "mp4a": "AAC",
    "aac":  "AAC",
    "opus": "Opus",
    "vorbis": "Vorbis",
    "mp3":  "MP3",
}

# Alturas estándar → etiqueta visible
_RESOLUTION_LABELS: dict[int, str] = {
    4320: "4320p (8K)",
    2160: "2160p (4K)",
    1440: "1440p (2K)",
    1080: "1080p",
    720:  "720p",
    480:  "480p",
    360:  "360p",
    240:  "240p",
    144:  "144p",
}

# Idiomas comunes → nombre legible
LANG_DISPLAY: dict[str, str] = {
    "en":      "English",
    "en-US":   "English (US)",
    "es":      "Español",
    "es-US":   "Español (US)",
    "es-419":  "Español (Latinoamérica)",
    "es-ES":   "Español (España)",
    "pt":      "Português",
    "pt-BR":   "Português (BR)",
    "fr":      "Français",
    "fr-FR":   "Français (France)",
    "de":      "Deutsch",
    "it":      "Italiano",
    "ja":      "日本語",
    "ko":      "한국어",
    "zh":      "中文",
    "zh-CN":   "中文 (简体)",
    "zh-TW":   "中文 (繁體)",
    "ar":      "العربية",
    "ru":      "Русский",
    "hi":      "हिन्दी",
    "tr":      "Türkçe",
    "pl":      "Polski",
    "nl":      "Nederlands",
    "sv":      "Svenska",
    "id":      "Bahasa Indonesia",
    "th":      "ภาษาไทย",
    "vi":      "Tiếng Việt",
}


def _lang_name(code: str) -> str:
    """Nombre legible para un código de idioma."""
    if code in LANG_DISPLAY:
        return LANG_DISPLAY[code]
    # Buscar prefijo (ej. "es-MX" → "Español (MX)")
    base = code.split("-")[0]
    base_name = LANG_DISPLAY.get(base, base.upper())
    suffix = code[len(base):].lstrip("-")
    return f"{base_name} ({suffix})" if suffix else base_name


@dataclass
class Format:
    """
    Representa un único formato disponible en el JSON de yt-dlp.
    Todos los campos opcionales tienen valor predeterminado seguro.
    """

    format_id:      str
    ext:            str = ""
    vcodec:         str = "none"
    acodec:         str = "none"
    height:         Optional[int] = None
    width:          Optional[int] = None
    fps:            Optional[float] = None
    dynamic_range:  Optional[str] = None
    filesize:       Optional[int] = None
    filesize_approx: Optional[int] = None
    language:       Optional[str] = None
    format_note:    str = ""
    tbr:            Optional[float] = None
    abr:            Optional[float] = None
    vbr:            Optional[float] = None
    protocol:       str = ""

    # ── Clasificación ─────────────────────────────────────────────────────────
    @property
    def has_video(self) -> bool:
        return self.vcodec not in (None, "none", "")

    @property
    def has_audio(self) -> bool:
        return self.acodec not in (None, "none", "")

    @property
    def is_video_only(self) -> bool:
        return self.has_video and not self.has_audio

    @property
    def is_audio_only(self) -> bool:
        return self.has_audio and not self.has_video

    @property
    def is_combined(self) -> bool:
        return self.has_video and self.has_audio

    # ── DRC / doblaje ─────────────────────────────────────────────────────────
    @property
    def is_drc(self) -> bool:
        return "-drc" in self.format_id or "drc" in self.format_note.lower()

    @property
    def is_original_audio(self) -> bool:
        return "original" in self.format_note.lower()

    @property
    def is_dubbed(self) -> bool:
        note = self.format_note.lower()
        return "dubbed" in note or "translated" in note or "dubbed-auto" in note

    # ── Etiquetas legibles ────────────────────────────────────────────────────
    @property
    def video_codec_label(self) -> str:
        if not self.vcodec or self.vcodec == "none":
            return ""
        base = self.vcodec.split(".")[0].lower()
        return _VIDEO_CODEC_LABELS.get(base, self.vcodec.upper())

    @property
    def audio_codec_label(self) -> str:
        if not self.acodec or self.acodec == "none":
            return ""
        base = self.acodec.split(".")[0].lower()
        return _AUDIO_CODEC_LABELS.get(base, self.acodec.upper())

    @property
    def resolution_label(self) -> str:
        if self.height is None:
            return "?"
        return _RESOLUTION_LABELS.get(self.height, f"{self.height}p")

    @property
    def estimated_size(self) -> Optional[int]:
        return self.filesize or self.filesize_approx

    @property
    def is_hdr(self) -> bool:
        return bool(self.dynamic_range) and self.dynamic_range.upper() not in ("SDR", "NONE", "")

    @property
    def language_name(self) -> str:
        if not self.language:
            return ""
        return _lang_name(self.language)

    @property
    def fps_int(self) -> Optional[int]:
        return round(self.fps) if self.fps else None


@dataclass
class LanguageInfo:
    """Información agregada de un idioma en el video."""
    code:      str           # e.g. "es-US"
    display:   str           # e.g. "Español (US) (doblaje IA)"
    is_original: bool = False
    is_dubbed:   bool = False
    formats:   list[Format] = field(default_factory=list)
    has_drc:   bool = False


@dataclass
class VideoInfo:
    """
    Metadatos completos de un video analizados desde yt-dlp -J.
    Se construye en VideoAnalyzer._parse(); App y FormatPanel lo consumen.
    """

    title:        str
    uploader:     str
    duration:     int         # segundos
    thumbnail:    str
    original_url: str

    # Todos los formatos filtrados (sin mhtml, sin m3u8)
    all_formats:      list[Format] = field(default_factory=list)

    # Sub-listas por tipo
    video_formats:    list[Format] = field(default_factory=list)   # video-only
    audio_formats:    list[Format] = field(default_factory=list)   # audio-only
    combined_formats: list[Format] = field(default_factory=list)   # video+audio

    # Metadatos derivados
    resolutions:  list[int] = field(default_factory=list)   # alturas únicas, desc
    has_hdr:      bool = False
    has_drc:      bool = False

    # Idiomas: orden fijo [original, es*, resto alpha]
    languages:    list[str] = field(default_factory=list)        # codes ordenados
    language_info: dict[str, LanguageInfo] = field(default_factory=dict)

    @property
    def has_spanish_dubbed(self) -> bool:
        for code, info in self.language_info.items():
            if code.startswith("es") and info.is_dubbed:
                return True
        return False

    @property
    def duration_str(self) -> str:
        if not self.duration:
            return "—"
        h, rem = divmod(self.duration, 3600)
        m, s   = divmod(rem, 60)
        if h:
            return f"{h}:{m:02d}:{s:02d}"
        return f"{m}:{s:02d}"
