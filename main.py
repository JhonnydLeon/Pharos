"""
main.py
=======
Punto de entrada de Pharos.

Responsabilidad:
  - Crear la ventana raíz de Tk.
  - Instanciar y conectar las dependencias (DI manual).
  - Arrancar el bucle de eventos.

Principio SOLID aplicado:
  D – Dependency Inversion: main.py es el único lugar donde se
      construyen las dependencias concretas (SettingsManager,
      Translator) y se inyectan en App. App no sabe cómo se crean.
"""

import tkinter as tk

from pharos.i18n import Translator
from pharos.settings import SettingsManager
from pharos.ui.app import App


def main() -> None:
    # 1. Cargar configuración persistente
    settings = SettingsManager()

    # 2. Crear el traductor con el idioma guardado
    translator = Translator(language=settings["language"])

    # 3. Crear la ventana principal de Tk
    root = tk.Tk()

    # 4. Inyectar dependencias en App y arrancar
    App(root=root, settings=settings, translator=translator)
    root.mainloop()


if __name__ == "__main__":
    main()
