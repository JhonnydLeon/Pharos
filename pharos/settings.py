"""
settings.py
===========
Gestión de preferencias del usuario (carga y guardado en JSON).

Principios SOLID aplicados:
  S – Single Responsibility: SOLO lee y escribe configuración.
      No sabe nada de UI ni de lógica de descarga.
  O – Open/Closed: para agregar una nueva preferencia, solo se
      añade a DEFAULTS; el resto del código no cambia.
"""

import json
import os

# Ruta del archivo de configuración (junto al ejecutable/script)
_SETTINGS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "pharos_settings.json",
)

# Valores por defecto
DEFAULTS: dict = {
    "language":                 "es",
    "check_updates_on_startup": True,
}


class SettingsManager:
    """
    Gestiona las preferencias persistentes de Pharos.

    Carga automáticamente al instanciar; persiste con .save().

    Ejemplo:
        cfg = SettingsManager()
        cfg["language"]             # "es"
        cfg["language"] = "en"
        cfg.save()
    """

    def __init__(self, path: str = _SETTINGS_PATH) -> None:
        self._path = path
        self._data: dict = {**DEFAULTS}
        self._load()

    # ── Interfaz de diccionario ───────────────────────────────────────────────
    def __getitem__(self, key: str):
        return self._data[key]

    def __setitem__(self, key: str, value) -> None:
        self._data[key] = value

    def get(self, key: str, default=None):
        return self._data.get(key, default)

    def update(self, mapping: dict) -> None:
        self._data.update(mapping)

    # ── Persistencia ──────────────────────────────────────────────────────────
    def save(self) -> None:
        """Guarda la configuración actual en disco."""
        try:
            with open(self._path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)
        except OSError:
            pass  # Si no se puede guardar, se sigue usando en memoria

    # ── Privado ───────────────────────────────────────────────────────────────
    def _load(self) -> None:
        try:
            with open(self._path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            self._data.update(loaded)
        except (FileNotFoundError, json.JSONDecodeError):
            pass  # Usa valores por defecto si el archivo no existe o está corrupto

