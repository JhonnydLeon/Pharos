"""
downloader.py
=============
Lógica de descarga usando yt-dlp y ffmpeg.

Principios SOLID aplicados:
  S – Single Responsibility: SOLO ejecuta yt-dlp y emite líneas de salida.
      No sabe nada de tkinter, ventanas ni botones.
  D – Dependency Inversion: en lugar de escribir directamente en un
      widget de texto, llama a callbacks inyectados:
        on_line(text)   → recibe cada línea de salida de yt-dlp
        on_done(ok)     → señala si terminó bien (True) o con error (False)
      Así la UI puede conectar cualquier destino de log sin cambiar Downloader.
"""

import os
import subprocess
import sys
import threading
from typing import Callable

from pharos.constants import QUALITY_FLAGS


def _base_dir() -> str:
    """Devuelve la carpeta del ejecutable o del script."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Downloader:
    """
    Ejecuta yt-dlp en un hilo separado y notifica el progreso
    mediante callbacks, sin depender de la interfaz gráfica.

    Uso:
        dl = Downloader(
            on_line=lambda text: print(text, end=""),
            on_done=lambda ok:  print("OK" if ok else "ERROR"),
        )
        dl.start(url="https://...", quality_key="1080p", save_dir="/ruta")
    """

    def __init__(
        self,
        on_line: Callable[[str], None],
        on_done: Callable[[bool], None],
    ) -> None:
        self._on_line = on_line
        self._on_done = on_done

    # ── Interfaz pública ──────────────────────────────────────────────────────
    def start(self, url: str, quality_key: str, save_dir: str) -> None:
        """Lanza la descarga en un hilo demonio."""
        thread = threading.Thread(
            target=self._run,
            args=(url, quality_key, save_dir),
            daemon=True,
        )
        thread.start()

    # ── Privado ───────────────────────────────────────────────────────────────
    def _run(self, url: str, quality_key: str, save_dir: str) -> None:
        base  = _base_dir()
        ytdlp = self._find_ytdlp(base)
        cmd   = self._build_command(ytdlp, quality_key, save_dir, base, url)

        self._on_line(f"> {' '.join(cmd)}\n")

        try:
            flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                creationflags=flags,
            )
            for line in process.stdout:
                self._on_line(line)
            process.wait()
            self._on_done(process.returncode == 0)

        except FileNotFoundError:
            self._on_line("\n⚠  yt-dlp no encontrado.\n")
            self._on_done(False)

    @staticmethod
    def _find_ytdlp(base_dir: str) -> str:
        """Busca yt-dlp.exe junto al programa; si no, usa el del PATH."""
        local = os.path.join(base_dir, "yt-dlp.exe")
        return local if os.path.exists(local) else "yt-dlp"

    @staticmethod
    def _build_command(
        ytdlp: str,
        quality_key: str,
        save_dir: str,
        base_dir: str,
        url: str,
    ) -> list[str]:
        """Construye el comando completo de yt-dlp."""
        flags = QUALITY_FLAGS.get(quality_key, QUALITY_FLAGS["1080p"])
        cmd = [
            ytdlp, *flags,
            "--newline", "--no-playlist",
            "-P", save_dir,
            "-o", "%(title)s.%(ext)s",
        ]
        ffmpeg_local = os.path.join(base_dir, "ffmpeg.exe")
        if os.path.exists(ffmpeg_local):
            cmd += ["--ffmpeg-location", base_dir]
        cmd.append(url)
        return cmd

