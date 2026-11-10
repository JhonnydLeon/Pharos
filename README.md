# yt-dlp + ffmpeg GUI

Descarga videos y audio con una interfaz simple: pega el link, elige la calidad y listo. Sin comandos.
Potenciado por [yt-dlp](https://github.com/yt-dlp/yt-dlp) y [ffmpeg](https://ffmpeg.org/).

## Qué hace

- Pega el link y descarga con un clic
- Calidad a elegir: 1080p, 720p, 480p o solo audio (mp3)
- Elige la carpeta donde se guardan los archivos
- Muestra el progreso en tiempo real
- Funciona sin ventana de consola

## Requisitos

- Windows 10 u 11
- [Python 3.10 o superior](https://www.python.org/downloads/) (al instalar, marca la casilla **Add Python to PATH**)
- yt-dlp y ffmpeg (ver paso 3)

## Instalación

### 1. Descarga el proyecto

```
git clone https://github.com/TU_USUARIO/yt-dlp-ffmpeg-gui.git
```

O pulsa **Code → Download ZIP** y descomprímelo.

### 2. Abre una terminal en la carpeta del proyecto

Esto es importante: la terminal debe estar en la misma carpeta donde está `descargador.py`.
En el Explorador de archivos, entra a la carpeta, haz clic derecho en un espacio vacío y elige **Abrir en Terminal**.

### 3. Instala yt-dlp y ffmpeg

```
winget install yt-dlp.yt-dlp
winget install Gyan.FFmpeg
```

Cierra y vuelve a abrir la terminal después de instalarlos.

> Alternativa: descarga `yt-dlp.exe` y `ffmpeg.exe` y déjalos en la misma carpeta que el programa.

### 4. Crea el programa (.exe)

```
pip install pyinstaller
python -m PyInstaller --onefile --noconsole descargador.py
```

Al terminar, tu programa estará en `dist\descargador.exe`. Ábrelo con doble clic.

### Opción rápida: sin crear el .exe

Si solo quieres probarlo:

```
python descargador.py
```

## Uso

1. Abre el programa
2. Pega el link del video
3. Elige la calidad y la carpeta de destino
4. Pulsa **Descargar**

## Aviso

Algunos antivirus o SmartScreen pueden mostrar una advertencia con programas creados con PyInstaller.
Es un falso positivo común; puedes revisar el código fuente completo en este repositorio.

Usa esta herramienta solo con contenido que tengas derecho a descargar. Este proyecto no está afiliado a yt-dlp, ffmpeg ni YouTube.

## Licencia

MIT