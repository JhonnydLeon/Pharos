"""
analyzer.py
===========
Analiza un video con `yt-dlp -J` en un hilo separado y construye un VideoInfo.

Principios SOLID:
  S – Single Responsibility: solo analiza; no descarga ni toca la UI.
  D – Dependency Inversion: comunica resultados via callbacks inyectados.
      La UI nunca se toca directamente desde aquí.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
from typing import Callable, Optional

from pharos.models import Format, LanguageInfo, VideoInfo, _lang_name


def _base_dir() -> str:
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _find_ytdlp() -> str:
    base = _base_dir()
    local = os.path.join(base, "yt-dlp.exe")
    return local if os.path.exists(local) else "yt-dlp"


# Protocolos HLS/DASH que descartamos
_BAD_PROTOCOLS = {"m3u8", "m3u8_native", "http_dash_segments", "mpdvideo",
                  "mpdaudio", "dash", "hls"}


class VideoAnalyzer:
    """
    Analiza un video con yt-dlp -J y construye un VideoInfo.

    Callbacks:
        on_info(VideoInfo)  → análisis completado
        on_error(str)       → mensaje de error legible
        on_progress(str)    → mensajes intermedios (log)
    """

    def __init__(
        self,
        on_info:     Callable[[VideoInfo], None],
        on_error:    Callable[[str], None],
        on_progress: Callable[[str], None],
    ) -> None:
        self._on_info     = on_info
        self._on_error    = on_error
        self._on_progress = on_progress

    # ── Interfaz pública ──────────────────────────────────────────────────────
    def analyze(self, url: str) -> None:
        """Lanza el análisis en un hilo demonio."""
        threading.Thread(
            target=self._run,
            args=(url,),
            daemon=True,
        ).start()

    # ── Privado ───────────────────────────────────────────────────────────────
    def _run(self, url: str) -> None:
        ytdlp = _find_ytdlp()
        self._on_progress("🔍 Ejecutando yt-dlp -J …\n")

        try:
            flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
            result = subprocess.run(
                [ytdlp, "-J", "--no-playlist", url],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=30,
                creationflags=flags,
            )
        except FileNotFoundError:
            self._on_error("yt-dlp no encontrado. Instálalo o colócalo junto al programa.")
            return
        except subprocess.TimeoutExpired:
            self._on_error("Tiempo de espera agotado. Comprueba tu conexión a internet.")
            return
        except Exception as exc:
            self._on_error(f"Error inesperado: {exc}")
            return

        stderr = result.stderr.strip()

        if result.returncode != 0:
            if "private video" in stderr.lower() or "this video is private" in stderr.lower():
                self._on_error("Video privado. No se puede analizar.")
            elif "video unavailable" in stderr.lower():
                self._on_error("Video no disponible.")
            elif "unable to download" in stderr.lower() or "network" in stderr.lower():
                self._on_error("Sin conexión a internet o URL inaccesible.")
            elif "unsupported url" in stderr.lower():
                self._on_error("URL no válida o no compatible.")
            else:
                # Mostrar primeras líneas del error para diagnóstico
                first_err = "\n".join(stderr.splitlines()[:5])
                self._on_error(f"yt-dlp retornó error:\n{first_err}")
            return

        if not result.stdout.strip():
            self._on_error("yt-dlp no devolvió datos. ¿URL válida?")
            return

        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            self._on_error(f"Error al parsear JSON de yt-dlp: {exc}")
            return

        try:
            info = self._parse(data, url)
        except Exception as exc:
            self._on_error(f"Error al procesar formatos: {exc}")
            return

        self._on_info(info)

    # ── Parseo ────────────────────────────────────────────────────────────────
    def _parse(self, data: dict, original_url: str) -> VideoInfo:
        raw_formats = data.get("formats", [])

        # Filtrar y convertir a Format
        all_fmts: list[Format] = []
        for f in raw_formats:
            parsed = self._parse_format(f)
            if parsed is not None:
                all_fmts.append(parsed)

        # Separar por tipo
        video_fmts    = [f for f in all_fmts if f.is_video_only]
        audio_fmts    = [f for f in all_fmts if f.is_audio_only]
        combined_fmts = [f for f in all_fmts if f.is_combined]

        # Metadatos
        has_hdr = any(f.is_hdr for f in video_fmts + combined_fmts)
        has_drc = any(f.is_drc for f in audio_fmts)

        # Resoluciones únicas ordenadas de mayor a menor
        heights = sorted(
            {f.height for f in video_fmts + combined_fmts if f.height},
            reverse=True,
        )

        # Idiomas
        languages, lang_info = self._parse_languages(audio_fmts)

        # Duración
        duration = int(data.get("duration") or 0)

        info = VideoInfo(
            title        = data.get("title", "—"),
            uploader     = data.get("uploader") or data.get("channel") or "",
            duration     = duration,
            thumbnail    = data.get("thumbnail", ""),
            original_url = original_url,
            all_formats      = all_fmts,
            video_formats    = video_fmts,
            audio_formats    = audio_fmts,
            combined_formats = combined_fmts,
            resolutions  = heights,
            has_hdr      = has_hdr,
            has_drc      = has_drc,
            languages    = languages,
            language_info = lang_info,
        )

        self._on_progress(
            f"✅ Análisis completo: {len(all_fmts)} formatos "
            f"({len(video_fmts)} video, {len(audio_fmts)} audio, "
            f"{len(combined_fmts)} combinado)\n"
        )
        return info

    @staticmethod
    def _parse_format(f: dict) -> Optional[Format]:
        """Convierte un dict de formato yt-dlp en Format, o None si se descarta."""
        ext      = f.get("ext", "")
        protocol = f.get("protocol", "")

        # Descartar storyboards (mhtml)
        if ext == "mhtml":
            return None

        # Descartar HLS/m3u8 y similares
        for bad in _BAD_PROTOCOLS:
            if bad in protocol.lower():
                return None

        # Descartar manifests dash sin url directa
        if not f.get("url"):
            return None

        return Format(
            format_id      = f.get("format_id", ""),
            ext            = ext,
            vcodec         = f.get("vcodec", "none") or "none",
            acodec         = f.get("acodec", "none") or "none",
            height         = f.get("height"),
            width          = f.get("width"),
            fps            = f.get("fps"),
            dynamic_range  = f.get("dynamic_range"),
            filesize       = f.get("filesize"),
            filesize_approx= f.get("filesize_approx"),
            language       = f.get("language"),
            format_note    = f.get("format_note") or "",
            tbr            = f.get("tbr"),
            abr            = f.get("abr"),
            vbr            = f.get("vbr"),
            protocol       = protocol,
        )

    def _parse_languages(
        self, audio_fmts: list[Format]
    ) -> tuple[list[str], dict[str, LanguageInfo]]:
        """
        Agrupa formatos de audio por idioma, detecta original/doblado,
        y devuelve la lista de códigos ordenada (original → es* → resto alpha).

        También hace LOG de todos los campos de audio para diagnóstico.
        """
        self._on_progress("\n── Formatos de audio (diagnóstico) ──────────────────\n")
        for f in audio_fmts:
            self._on_progress(
                f"  format_id={f.format_id!r:20s} "
                f"language={f.language!r:12s} "
                f"format_note={f.format_note!r:25s} "
                f"acodec={f.acodec!r}\n"
            )
        self._on_progress("─" * 55 + "\n\n")

        # Agrupar por código de idioma
        lang_map: dict[str, LanguageInfo] = {}

        for f in audio_fmts:
            code = f.language or "unknown"
            if code not in lang_map:
                lang_map[code] = LanguageInfo(
                    code=code,
                    display="",           # se rellena abajo
                    is_original=False,
                    is_dubbed=False,
                    formats=[],
                    has_drc=False,
                )
            info = lang_map[code]
            info.formats.append(f)
            if f.is_original_audio:
                info.is_original = True
            if f.is_dubbed:
                info.is_dubbed = True
            if f.is_drc:
                info.has_drc = True

        # Si ningún idioma tiene "original" marcado explícitamente,
        # asumir que el primero (sin "dubbed") es el original
        if not any(v.is_original for v in lang_map.values()):
            for code, info in lang_map.items():
                if not info.is_dubbed:
                    info.is_original = True
                    break

        # Construir etiqueta display
        for code, info in lang_map.items():
            base_name = _lang_name(code)
            if info.is_original:
                info.display = f"{base_name} (original)"
            elif info.is_dubbed:
                info.display = f"{base_name} (doblaje IA)"
            else:
                info.display = base_name

        # Ordenar: original primero, luego es*, luego resto alphabético
        def _sort_key(code: str) -> tuple:
            info = lang_map[code]
            if info.is_original:
                return (0, code)
            if code.startswith("es"):
                return (1, code)
            return (2, code)

        ordered = sorted(lang_map.keys(), key=_sort_key)
        return ordered, lang_map
