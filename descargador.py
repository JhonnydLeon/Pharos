import os
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

CALIDADES = {
    "1080p (mp4)": ["-S", "res:1080,ext:mp4:m4a", "--merge-output-format", "mp4"],
    "720p (mp4)": ["-S", "res:720,ext:mp4:m4a", "--merge-output-format", "mp4"],
    "480p (mp4)": ["-S", "res:480,ext:mp4:m4a", "--merge-output-format", "mp4"],
    "Solo audio (mp3)": ["-x", "--audio-format", "mp3"],
}


def carpeta_base():
    # Carpeta del .exe (o del .py) para buscar yt-dlp.exe y ffmpeg.exe ahi primero
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


class App:
    def __init__(self, root):
        self.root = root
        root.title("Descargador de videos")
        root.geometry("640x420")
        root.resizable(False, False)

        self.carpeta = tk.StringVar(value=os.path.join(os.path.expanduser("~"), "Downloads"))
        self.calidad = tk.StringVar(value="1080p (mp4)")

        frm = ttk.Frame(root, padding=12)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="Link del video:").pack(anchor="w")
        self.url = ttk.Entry(frm)
        self.url.pack(fill="x", pady=(0, 8))

        fila = ttk.Frame(frm)
        fila.pack(fill="x", pady=(0, 8))
        ttk.Label(fila, text="Calidad:").pack(side="left")
        ttk.Combobox(fila, textvariable=self.calidad, values=list(CALIDADES),
                     state="readonly", width=18).pack(side="left", padx=8)

        fila2 = ttk.Frame(frm)
        fila2.pack(fill="x", pady=(0, 8))
        ttk.Label(fila2, text="Guardar en:").pack(side="left")
        ttk.Entry(fila2, textvariable=self.carpeta).pack(side="left", fill="x", expand=True, padx=8)
        ttk.Button(fila2, text="Elegir...", command=self.elegir_carpeta).pack(side="left")

        self.boton = ttk.Button(frm, text="Descargar", command=self.iniciar)
        self.boton.pack(pady=6)

        self.log = tk.Text(frm, height=14, state="disabled", bg="#111", fg="#ddd")
        self.log.pack(fill="both", expand=True)

    def elegir_carpeta(self):
        c = filedialog.askdirectory(initialdir=self.carpeta.get())
        if c:
            self.carpeta.set(c)

    def escribir(self, texto):
        self.log.configure(state="normal")
        self.log.insert("end", texto)
        self.log.see("end")
        self.log.configure(state="disabled")

    def iniciar(self):
        link = self.url.get().strip()
        if not link:
            messagebox.showwarning("Falta el link", "Pega el link del video.")
            return
        self.boton.configure(state="disabled")
        threading.Thread(target=self.descargar, args=(link,), daemon=True).start()

    def descargar(self, link):
        base = carpeta_base()
        ytdlp = os.path.join(base, "yt-dlp.exe")
        if not os.path.exists(ytdlp):
            ytdlp = "yt-dlp"  # usa el del PATH

        cmd = [ytdlp, *CALIDADES[self.calidad.get()],
               "--newline", "--no-playlist",
               "-P", self.carpeta.get(),
               "-o", "%(title)s.%(ext)s"]
        if os.path.exists(os.path.join(base, "ffmpeg.exe")):
            cmd += ["--ffmpeg-location", base]
        cmd.append(link)

        self.root.after(0, self.escribir, f"> {' '.join(cmd)}\n")
        try:
            flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                 text=True, encoding="utf-8", errors="replace",
                                 creationflags=flags)
            for linea in p.stdout:
                self.root.after(0, self.escribir, linea)
            p.wait()
            ok = p.returncode == 0
            self.root.after(0, self.escribir, "\nListo.\n" if ok else "\nError, revisa el log.\n")
        except FileNotFoundError:
            self.root.after(0, self.escribir, "\nNo encontre yt-dlp. Ponlo junto al programa o en el PATH.\n")
        finally:
            self.root.after(0, lambda: self.boton.configure(state="normal"))


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
