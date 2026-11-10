"""
updater.py
==========
Lógica de verificación de actualizaciones desde GitHub Releases.

Principios SOLID aplicados:
  S – Single Responsibility: SOLO consulta GitHub y compara versiones.
      No toca la UI, no muestra diálogos.
  O – Open/Closed: para cambiar la fuente de actualizaciones
      (p. ej. un servidor propio), se subclasifica Updater o se
      inyecta otra implementación; el App no cambia.
  D – Dependency Inversion: el App recibe callbacks on_update_found /
      on_no_update / on_error, en lugar de llamar directamente a
      messagebox. Así Updater no depende de tkinter.
"""

import json
import re
import threading
import time
import urllib.error
import urllib.request
from typing import Callable, Optional, Tuple

from pharos.constants import GITHUB_API, VERSION


class Updater:
    """
    Consulta la API de GitHub Releases y notifica el resultado
    mediante callbacks, sin acoplarse a la interfaz gráfica.

    Parámetros de los callbacks:
      on_update_found(latest_version: str, download_url: str)
      on_no_update(current_version: str)
      on_error(error_message: str)
    """

    def __init__(
        self,
        on_update_found: Callable[[str, str], None],
        on_no_update:    Callable[[str], None],
        on_error:        Callable[[str], None],
    ) -> None:
        self._on_update_found = on_update_found
        self._on_no_update    = on_no_update
        self._on_error        = on_error

    # ── Interfaz pública ──────────────────────────────────────────────────────
    def check(self, startup: bool = False) -> None:
        """
        Lanza la verificación en un hilo demonio.

        Args:
            startup: Si es True, espera 2 s antes de verificar (para
                     que la UI termine de arrancar) y no llama a
                     on_error (el arranque es silencioso).
        """
        thread = threading.Thread(
            target=self._run,
            args=(startup,),
            daemon=True,
        )
        thread.start()

    # ── Privado ───────────────────────────────────────────────────────────────
    def _run(self, startup: bool) -> None:
        if startup:
            time.sleep(2)

        try:
            latest_ver, dl_url = self._fetch_latest()

            if latest_ver is None:
                # Sin releases publicadas → tratar como "al día"
                self._on_no_update(VERSION)
                return

            if self._is_newer(latest_ver, VERSION):
                self._on_update_found(latest_ver, dl_url)
            else:
                self._on_no_update(latest_ver)

        except Exception as exc:
            if not startup:
                self._on_error(str(exc))

    @staticmethod
    def _fetch_latest() -> Tuple[Optional[str], Optional[str]]:
        """
        Consulta GitHub API.

        Returns:
            (tag, html_url) si hay releases, o (None, None) si HTTP 404.

        Raises:
            urllib.error.HTTPError: para cualquier otro código HTTP.
            Exception: para errores de red.
        """
        req = urllib.request.Request(
            GITHUB_API,
            headers={"User-Agent": f"Pharos/{VERSION}"},
        )
        try:
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode())
            return data["tag_name"].lstrip("v"), data["html_url"]
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                return None, None
            raise

    @staticmethod
    def _is_newer(remote: str, local: str) -> bool:
        """Devuelve True si remote > local (formato X.Y.Z)."""
        def to_tuple(v: str) -> tuple:
            try:
                return tuple(int(x) for x in re.split(r"[.\-]", v)[:3])
            except ValueError:
                return (0,)
        return to_tuple(remote) > to_tuple(local)

