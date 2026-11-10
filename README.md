# ⚡ Pharos – Video Downloader

<p align="center">
  <img src="https://img.shields.io/badge/version-1.0.0-red?style=flat-square"/>
  <img src="https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square"/>
  <img src="https://img.shields.io/badge/platform-Windows-lightgrey?style=flat-square"/>
  <img src="https://img.shields.io/badge/powered%20by-yt--dlp%20%2B%20ffmpeg-orange?style=flat-square"/>
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square"/>
</p>

**Pharos** es una interfaz gráfica moderna para descargar videos y audio usando [yt-dlp](https://github.com/yt-dlp/yt-dlp) y [ffmpeg](https://ffmpeg.org/).  
Pega el link, elige la calidad y descarga — sin comandos.

---

## Características

| Función | Descripción |
|---|---|
| 🎨 **Interfaz moderna** | Diseño oscuro con acento rojo/blanco |
| 🌐 **Multiidioma** | Español e inglés (seleccionable en ⚙ Preferencias) |
| ▶ **Vista previa** | Muestra título, canal y duración del video antes de descargar; miniatura si tienes Pillow instalado |
| 📋 **Ventana de Logs** | Registros detallados en ventana separada (no estorba la UI principal) |
| 🔄 **Buscar actualizaciones** | Botón manual + opción de verificación automática al iniciar |
| ⛶ **Pantalla completa** | Botón y atajo `F11`; `Esc` para salir |
| 🗕 **Minimizar** | Botón directo en la barra de título |
| 📁 **Calidades** | 1080p, 720p, 480p (mp4) y solo audio (mp3) |
| 📂 **Carpeta personalizada** | Elige donde guardar cada descarga |
| ⚙ **Preferencias persistentes** | Idioma y comportamiento al arrancar se guardan en `pharos_settings.json` |

---

## Interfaz

```
![Pantalla de inicio](assets/main.png)
```

---

## 🔧 Requisitos

- **Windows 10 u 11**
- **Python 3.10 o superior** ([descargar](https://www.python.org/downloads/)) — marca **Add Python to PATH**
- **yt-dlp** y **ffmpeg** (ver instalación)
- *(Opcional)* **Pillow** — para mostrar miniatura en la vista previa

---

## 🚀 Instalación

### 1. Clona el repositorio

```bash
git clone https://github.com/TU_USUARIO/Pharos.git
cd Pharos
```

O pulsa **Code → Download ZIP** y descomprímelo.

### 2. Instala yt-dlp y ffmpeg

```bash
winget install yt-dlp.yt-dlp
winget install Gyan.FFmpeg
```

> Cierra y vuelve a abrir la terminal tras instalarlos.  
> **Alternativa:** descarga `yt-dlp.exe` y `ffmpeg.exe` y déjalos en la misma carpeta que `descargador.py`.

### 3. *(Opcional)* Instala Pillow para miniaturas

```bash
pip install Pillow
```

### 4. Ejecuta el programa

```bash
python descargador.py
```

### 5. *(Opcional)* Crear ejecutable .exe

```bash
pip install pyinstaller
python -m PyInstaller --onefile --noconsole descargador.py
```

El ejecutable quedará en `dist\descargador.exe`.

---

## 🌐 Idiomas

Pharos soporta **Español** e **Inglés**. Cambia el idioma en **⚙ Preferencias** — el cambio se aplica de inmediato y se guarda para la próxima sesión.

---

## 🔄 Actualizaciones

Pharos puede verificar si hay una nueva versión disponible en GitHub de dos formas:

1. **Automáticamente al iniciar** — activa/desactiva en ⚙ Preferencias → *Buscar actualizaciones al iniciar*.
2. **Manual** — botón **Buscar actualizaciones** en la interfaz principal.

> **Nota:** Para que las actualizaciones funcionen, edita la variable `GITHUB_REPO` en `descargador.py` con tu usuario y repositorio reales:
> ```python
> GITHUB_REPO = "TU_USUARIO/Pharos"
> ```

---

## 📋 Registros / Logs

Los registros de descarga se muestran en una **ventana separada** (botón **Registros / Logs**).  
La ventana se abre automáticamente al iniciar una descarga y puede limpiarse con el botón 🗑 Limpiar.

---

## 📂 Archivos del proyecto

```
Pharos/
├── descargador.py         # Programa principal
├── pharos_settings.json   # Preferencias guardadas (creado al primer uso)
├── yt-dlp.exe             # (opcional) si no usas el del PATH
├── ffmpeg.exe             # (opcional) si no usas el del PATH
└── README.md
```

---

## ⚠ Aviso

Algunos antivirus o SmartScreen pueden mostrar advertencias con ejecutables generados por PyInstaller.  
Es un falso positivo común — puedes revisar el código fuente completo en este repositorio.

Usa Pharos únicamente con contenido que tengas derecho a descargar.  
Este proyecto no está afiliado a yt-dlp, ffmpeg ni YouTube.

---

## 📄 Licencia

MIT
