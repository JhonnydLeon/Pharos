"""
ui/format_panel.py
==================
Panel de selección de formatos avanzado.

Se muestra después de un análisis exitoso y reemplaza el combobox
simple de calidad. Permite seleccionar modo, resolución, códec, idioma,
DRC y más, mostrando solo las opciones que el video realmente tiene.

Principios SOLID:
  S – Solo UI de selección; no descarga ni analiza.
  O – Fácil añadir nuevas opciones sin romper el panel.
  D – Recibe VideoInfo y Translator por constructor (DI).
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

from pharos.constants import COLORS as C, QUALITY_FLAGS
from pharos.i18n import Translator
from pharos.models import Format, VideoInfo
from pharos.ui.dropdown import DropdownButton
from pharos.ui.segmented_button import SegmentedButton


# ── Modos de descarga ─────────────────────────────────────────────────────────
MODE_VIDEO_AUDIO = 0
MODE_VIDEO_ONLY  = 1
MODE_AUDIO_ONLY  = 2


class FormatPanel(tk.Frame):
    """
    Panel completo de selección de formatos.

    Uso:
        fp = FormatPanel(parent, translator=t, on_args_changed=callback)
        fp.pack(fill="x")
        fp.load(video_info)         # llamar cuando el análisis termina
        fp.show_analyzing()         # mientras yt-dlp corre
        fp.show_error("msg")        # si falla
        args = fp.get_download_args()  # lista de flags para yt-dlp
    """

    def __init__(
        self,
        parent,
        translator:        Translator,
        on_args_changed:   Optional[Callable[[], None]] = None,
    ) -> None:
        super().__init__(parent, bg=C["bg"], bd=0, highlightthickness=0)
        self._t             = translator
        self._on_args_changed = on_args_changed
        self._info:  Optional[VideoInfo] = None

        # Estado de los controles
        self._mode          = MODE_VIDEO_AUDIO
        self._resolution:   Optional[int]  = None
        self._fps:          Optional[int]  = None
        self._dynamic_range: Optional[str] = None
        self._video_codec:  Optional[str]  = None
        self._container:    str            = "mp4"
        self._audio_lang:   Optional[str]  = None
        self._audio_codec:  Optional[str]  = None
        self._audio_quality: Optional[str] = None
        self._drc:          bool           = False
        self._audio_format: str            = "mp3"
        self._mp3_quality:  str            = "192"

        self._build()

    # ══════════════════════════════════════════════════════════════════════════
    # API pública
    # ══════════════════════════════════════════════════════════════════════════
    def show_idle(self) -> None:
        """Estado inicial: panel colapsado (sin análisis)."""
        self._frame_analysis.pack_forget()
        self._frame_controls.pack_forget()
        self._frame_presets.pack_forget()
        self._lbl_status.configure(
            text="", fg=C["text_dim"]
        )

    def show_analyzing(self) -> None:
        """Muestra 'Analizando…'."""
        self._frame_controls.pack_forget()
        self._frame_presets.pack_forget()
        self._frame_analysis.pack(fill="x", pady=(0, 4))
        self._lbl_status.configure(
            text=self._t("analyzing"), fg=C["warning"]
        )

    def show_error(self, msg: str) -> None:
        """Muestra error de análisis."""
        self._frame_controls.pack_forget()
        self._frame_presets.pack_forget()
        self._frame_analysis.pack(fill="x", pady=(0, 4))
        self._lbl_status.configure(
            text=f"❌ {msg}", fg=C["error"]
        )

    def load(self, info: VideoInfo) -> None:
        """Carga un VideoInfo y muestra los controles completos."""
        self._info = info
        self._frame_analysis.pack(fill="x", pady=(0, 4))
        self._lbl_status.configure(
            text=self._t("analysis_ready"), fg=C["success"]
        )
        self._populate_controls()
        self._frame_controls.pack(fill="x", pady=(4, 4))
        self._frame_presets.pack(fill="x", pady=(4, 0))

    def get_download_args(self) -> list[str]:
        """
        Devuelve los flags de yt-dlp para la selección actual.
        Usa QUALITY_FLAGS como fallback hasta implementar items 7-8.
        """
        if self._info is None:
            # Sin análisis: usar calidad simple
            return QUALITY_FLAGS.get("1080p", [])

        if self._mode == MODE_AUDIO_ONLY:
            fmt = self._audio_format
            args = ["-x", "--audio-format", fmt]
            if fmt == "mp3":
                kbps = self._mp3_quality or "192"
                args += ["--audio-quality", f"{kbps}k"]
            return args

        # Mapear resolución a flag simple de QUALITY_FLAGS
        res = self._resolution
        if res and res >= 1080:
            key = "1080p"
        elif res and res >= 720:
            key = "720p"
        elif res and res >= 480:
            key = "480p"
        else:
            key = "1080p"

        return QUALITY_FLAGS.get(key, QUALITY_FLAGS["1080p"])

    def refresh_language(self, t: Translator) -> None:
        """Actualiza el idioma de los textos del panel."""
        self._t = t
        self._refresh_labels()

    # ══════════════════════════════════════════════════════════════════════════
    # Construcción de la UI
    # ══════════════════════════════════════════════════════════════════════════
    def _build(self) -> None:
        # ── Fila de estado (análisis / error) ─────────────────────────────────
        self._frame_analysis = tk.Frame(self, bg=C["bg"])
        self._lbl_status = tk.Label(
            self._frame_analysis,
            text="",
            bg=C["bg"], fg=C["text_dim"],
            font=("Segoe UI", 9),
            anchor="w",
        )
        self._lbl_status.pack(side="left")

        # ── Área de controles ─────────────────────────────────────────────────
        self._frame_controls = tk.Frame(self, bg=C["surface"], pady=10, padx=10)

        # Selector de modo (siempre visible cuando hay análisis)
        self._lbl_mode = tk.Label(
            self._frame_controls,
            text=self._t("mode_label"),
            bg=C["surface"], fg=C["text_dim"],
            font=("Segoe UI", 9, "bold"),
        )
        self._lbl_mode.pack(anchor="w", pady=(0, 4))

        self._seg_mode = SegmentedButton(
            self._frame_controls,
            options=[
                self._t("mode_video_audio"),
                self._t("mode_video_only"),
                self._t("mode_audio_only"),
            ],
            on_change=self._on_mode_change,
            font=("Segoe UI", 9),
            padx=14, pady=7,
        )
        self._seg_mode._frame = tk.Frame(self._frame_controls, bg=C["surface"])
        self._seg_mode.pack(anchor="w", pady=(0, 10))

        # Grid de controles opcionales
        self._grid = tk.Frame(self._frame_controls, bg=C["surface"])
        self._grid.pack(fill="x")

        # Fila 1: Resolución | FPS
        self._row_res = self._make_row(self._grid, 0)
        self._lbl_res = self._make_label(self._row_res, "resolution")
        self._dd_res  = DropdownButton(
            self._row_res, values=["—"],
            on_select=lambda i: self._on_res_changed(i),
            font=("Segoe UI", 9), padx=12, pady=6, min_width=130,
        )
        self._dd_res.pack(anchor="w", pady=(2, 0))

        self._row_fps = self._make_row(self._grid, 1)
        self._lbl_fps = self._make_label(self._row_fps, "fps_label")
        self._dd_fps  = DropdownButton(
            self._row_fps, values=["—"],
            on_select=lambda i: self._on_fps_changed(i),
            font=("Segoe UI", 9), padx=12, pady=6, min_width=100,
        )
        self._dd_fps.pack(anchor="w", pady=(2, 0))

        # Fila 2: HDR | Códec de video
        self._row_hdr = self._make_row(self._grid, 0, row=1)
        self._lbl_hdr = self._make_label(self._row_hdr, "dynamic_range")
        self._dd_hdr  = DropdownButton(
            self._row_hdr, values=["SDR"],
            on_select=lambda i: self._on_hdr_changed(i),
            font=("Segoe UI", 9), padx=12, pady=6, min_width=100,
        )
        self._dd_hdr.pack(anchor="w", pady=(2, 0))

        self._row_vcodec = self._make_row(self._grid, 1, row=1)
        self._lbl_vcodec = self._make_label(self._row_vcodec, "video_codec")
        self._dd_vcodec  = DropdownButton(
            self._row_vcodec, values=["H.264"],
            on_select=lambda i: self._on_vcodec_changed(i),
            font=("Segoe UI", 9), padx=12, pady=6, min_width=140,
        )
        self._dd_vcodec.pack(anchor="w", pady=(2, 0))

        # Fila 3: Contenedor | Idioma de audio
        self._row_container = self._make_row(self._grid, 0, row=2)
        self._lbl_container = self._make_label(self._row_container, "container")
        self._dd_container  = DropdownButton(
            self._row_container, values=["mp4", "mkv", "webm"],
            on_select=lambda i: self._on_container_changed(i),
            font=("Segoe UI", 9), padx=12, pady=6, min_width=100,
        )
        self._dd_container.pack(anchor="w", pady=(2, 0))

        self._row_lang = self._make_row(self._grid, 1, row=2)
        self._lbl_lang = self._make_label(self._row_lang, "audio_language")
        self._dd_lang  = DropdownButton(
            self._row_lang, values=["—"],
            on_select=lambda i: self._on_lang_changed(i),
            font=("Segoe UI", 9), padx=12, pady=6, min_width=180,
        )
        self._dd_lang.pack(anchor="w", pady=(2, 0))

        # Fila 4: Códec audio | Calidad audio
        self._row_acodec = self._make_row(self._grid, 0, row=3)
        self._lbl_acodec = self._make_label(self._row_acodec, "audio_codec")
        self._dd_acodec  = DropdownButton(
            self._row_acodec, values=["AAC", "Opus"],
            on_select=lambda i: self._on_acodec_changed(i),
            font=("Segoe UI", 9), padx=12, pady=6, min_width=120,
        )
        self._dd_acodec.pack(anchor="w", pady=(2, 0))

        self._row_aquality = self._make_row(self._grid, 1, row=3)
        self._lbl_aquality = self._make_label(self._row_aquality, "audio_quality")
        self._dd_aquality  = DropdownButton(
            self._row_aquality, values=["Mejor automática"],
            on_select=lambda i: self._on_aquality_changed(i),
            font=("Segoe UI", 9), padx=12, pady=6, min_width=140,
        )
        self._dd_aquality.pack(anchor="w", pady=(2, 0))

        # Fila 5: DRC checkbox | Formato de audio (audio-only)
        self._row_drc = self._make_row(self._grid, 0, row=4)
        self._lbl_drc = self._make_label(self._row_drc, "drc_audio")
        self._drc_var = tk.BooleanVar(value=False)
        self._chk_drc = tk.Checkbutton(
            self._row_drc,
            variable=self._drc_var,
            text=self._t("drc_tooltip_short"),
            bg=C["surface"], fg=C["text_dim"],
            activebackground=C["surface"], activeforeground=C["text"],
            selectcolor=C["surface2"],
            font=("Segoe UI", 9),
            command=self._on_drc_changed,
        )
        self._chk_drc.pack(anchor="w", pady=(2, 0))

        self._row_afmt = self._make_row(self._grid, 1, row=4)
        self._lbl_afmt = self._make_label(self._row_afmt, "audio_format")
        self._dd_afmt  = DropdownButton(
            self._row_afmt, values=["mp3", "m4a", "opus", "flac", "wav"],
            on_select=lambda i: self._on_afmt_changed(i),
            font=("Segoe UI", 9), padx=12, pady=6, min_width=100,
        )
        self._dd_afmt.pack(anchor="w", pady=(2, 0))

        # Fila 6: Calidad MP3 (solo cuando audio_format == mp3)
        self._row_mp3q = self._make_row(self._grid, 0, row=5)
        self._lbl_mp3q = self._make_label(self._row_mp3q, "mp3_quality")
        self._dd_mp3q  = DropdownButton(
            self._row_mp3q, values=["128 kbps", "192 kbps", "256 kbps", "320 kbps"],
            on_select=lambda i: self._on_mp3q_changed(i),
            font=("Segoe UI", 9), padx=12, pady=6, min_width=120,
        )
        self._dd_mp3q.current(1)   # 192 por defecto
        self._dd_mp3q.pack(anchor="w", pady=(2, 0))

        # ── Presets ───────────────────────────────────────────────────────────
        self._frame_presets = tk.Frame(self, bg=C["bg"])
        preset_lbl = tk.Label(
            self._frame_presets,
            text=self._t("presets_label"),
            bg=C["bg"], fg=C["text_dim"],
            font=("Segoe UI", 9, "bold"),
        )
        preset_lbl.pack(anchor="w", pady=(0, 4))

        preset_row = tk.Frame(self._frame_presets, bg=C["bg"])
        preset_row.pack(anchor="w")

        self._btn_preset_best   = self._make_preset_btn(preset_row, "preset_best",   self._preset_best)
        self._btn_preset_light  = self._make_preset_btn(preset_row, "preset_light",  self._preset_light)
        self._btn_preset_compat = self._make_preset_btn(preset_row, "preset_compat", self._preset_compat)
        self._btn_preset_es     = self._make_preset_btn(preset_row, "preset_es",     self._preset_es)

        for btn in (self._btn_preset_best, self._btn_preset_light,
                    self._btn_preset_compat, self._btn_preset_es):
            btn.pack(side="left", padx=(0, 6))

    # ── Helpers de construcción ───────────────────────────────────────────────
    @staticmethod
    def _make_row(grid: tk.Frame, col: int, row: int = 0) -> tk.Frame:
        f = tk.Frame(grid, bg=C["surface"])
        f.grid(row=row, column=col, sticky="nw", padx=(0, 20), pady=(0, 10))
        return f

    def _make_label(self, parent: tk.Frame, key: str) -> tk.Label:
        lbl = tk.Label(
            parent,
            text=self._t(key),
            bg=C["surface"], fg=C["text_dim"],
            font=("Segoe UI", 8, "bold"),
            anchor="w",
        )
        lbl.pack(anchor="w")
        return lbl

    def _make_preset_btn(self, parent, key: str, cmd) -> tk.Button:
        return tk.Button(
            parent,
            text=self._t(key),
            bg=C["surface2"], fg=C["text_dim"],
            activebackground=C["surface"], activeforeground=C["text"],
            relief="flat", bd=0, padx=12, pady=7,
            font=("Segoe UI", 9),
            cursor="hand2",
            command=cmd,
        )

    # ══════════════════════════════════════════════════════════════════════════
    # Relleno de controles desde VideoInfo
    # ══════════════════════════════════════════════════════════════════════════
    def _populate_controls(self) -> None:
        """Llena todos los controles con los datos del VideoInfo actual."""
        info = self._info
        if info is None:
            return

        # ── Resoluciones ──────────────────────────────────────────────────────
        from pharos.models import _RESOLUTION_LABELS
        res_labels = [
            _RESOLUTION_LABELS.get(h, f"{h}p") for h in info.resolutions
        ]
        if res_labels:
            self._dd_res["values"] = res_labels
            self._dd_res.current(0)
            self._resolution = info.resolutions[0] if info.resolutions else None
        else:
            self._dd_res["values"] = ["—"]
            self._resolution = None

        # ── FPS para la resolución seleccionada ───────────────────────────────
        self._refresh_fps()

        # ── HDR ───────────────────────────────────────────────────────────────
        hdr_ranges = sorted(
            {f.dynamic_range for f in info.video_formats
             if f.height == self._resolution and f.dynamic_range and f.is_hdr},
            reverse=True,
        )
        if hdr_ranges:
            vals = ["SDR"] + list(hdr_ranges)
            self._dd_hdr["values"] = vals
            self._dd_hdr.current(0)
        else:
            self._dd_hdr["values"] = ["SDR"]
            self._dd_hdr.current(0)
        self._dynamic_range = "SDR"

        # ── Códecs de video ───────────────────────────────────────────────────
        self._refresh_vcodecs()

        # ── Contenedor ───────────────────────────────────────────────────────
        self._dd_container["values"] = ["mp4", "mkv", "webm"]
        self._dd_container.current(0)
        self._container = "mp4"

        # ── Idiomas ───────────────────────────────────────────────────────────
        if info.languages:
            lang_labels = [
                info.language_info[code].display for code in info.languages
            ]
            self._dd_lang["values"] = lang_labels
            self._dd_lang.current(0)
            self._audio_lang = info.languages[0]
        else:
            self._dd_lang["values"] = ["—"]
            self._audio_lang = None

        # ── Códecs de audio ───────────────────────────────────────────────────
        self._refresh_acodecs()

        # ── DRC ───────────────────────────────────────────────────────────────
        self._refresh_drc()

        # ── Preset de español: habilitar/deshabilitar ─────────────────────────
        if info.has_spanish_dubbed:
            self._btn_preset_es.configure(state="normal", fg=C["text_dim"])
        else:
            self._btn_preset_es.configure(state="disabled", fg=C["border"])

        # Aplicar visibilidad según modo actual
        self._refresh_visibility()

    def _refresh_fps(self) -> None:
        """Actualiza el combobox de FPS para la resolución actual."""
        if self._info is None:
            return
        fps_set = {
            f.fps_int for f in self._info.video_formats
            if f.height == self._resolution and f.fps_int
        }
        if len(fps_set) > 1:
            fps_list = sorted(fps_set, reverse=True)
            self._dd_fps["values"] = [f"{v} fps" for v in fps_list]
            self._dd_fps.current(0)
            self._fps = fps_list[0]
            self._row_fps.grid()
        else:
            self._fps = next(iter(fps_set), None)
            self._row_fps.grid_remove()

    def _refresh_vcodecs(self) -> None:
        """Actualiza el combobox de códec de video para la resolución actual."""
        if self._info is None:
            return
        label_map = {}
        for f in self._info.video_formats:
            if f.height == self._resolution:
                lbl = f.video_codec_label
                if lbl and lbl not in label_map:
                    label_map[lbl] = lbl
        # Orden de preferencia: H.264, VP9, AV1, el resto
        order = ["H.264", "VP9", "AV1"]
        sorted_codecs = [c for c in order if c in label_map] + \
                        [c for c in label_map if c not in order]
        if sorted_codecs:
            self._dd_vcodec["values"] = sorted_codecs
            self._dd_vcodec.current(0)
            self._video_codec = sorted_codecs[0]
        else:
            self._dd_vcodec["values"] = ["—"]
            self._video_codec = None

    def _refresh_acodecs(self) -> None:
        """Actualiza el combobox de códec de audio para el idioma actual."""
        if self._info is None:
            return
        lang_info = (
            self._info.language_info.get(self._audio_lang)
            if self._audio_lang else None
        )
        codecs = set()
        if lang_info:
            for f in lang_info.formats:
                if not f.is_drc and f.audio_codec_label:
                    codecs.add(f.audio_codec_label)
        order = ["AAC", "Opus"]
        sorted_codecs = [c for c in order if c in codecs] + \
                        [c for c in codecs if c not in order]
        if sorted_codecs:
            self._dd_acodec["values"] = sorted_codecs
            self._dd_acodec.current(0)
            self._audio_codec = sorted_codecs[0]
        else:
            self._dd_acodec["values"] = ["—"]
            self._audio_codec = None

    def _refresh_drc(self) -> None:
        """Habilita/deshabilita el checkbox DRC según el idioma seleccionado."""
        if self._info is None or not self._audio_lang:
            self._chk_drc.configure(state="disabled")
            return
        lang_info = self._info.language_info.get(self._audio_lang)
        if lang_info and lang_info.has_drc:
            self._chk_drc.configure(state="normal")
        else:
            self._chk_drc.configure(state="disabled")
            self._drc_var.set(False)
            self._drc = False

    def _refresh_visibility(self) -> None:
        """Muestra u oculta controles según el modo activo."""
        is_video = self._mode in (MODE_VIDEO_AUDIO, MODE_VIDEO_ONLY)
        is_audio = self._mode in (MODE_VIDEO_AUDIO, MODE_AUDIO_ONLY)
        is_only_audio = self._mode == MODE_AUDIO_ONLY
        has_hdr = self._info.has_hdr if self._info else False

        # Video controls
        self._show_row(self._row_res,      is_video)
        self._show_row(self._row_hdr,      is_video and has_hdr)
        self._show_row(self._row_vcodec,   is_video)
        self._show_row(self._row_container, is_video)

        # Audio controls
        self._show_row(self._row_lang,    is_audio)
        self._show_row(self._row_acodec,  is_audio)
        self._show_row(self._row_aquality, is_audio)
        self._show_row(self._row_drc,     is_audio)

        # Solo audio
        self._show_row(self._row_afmt,    is_only_audio)
        # MP3 quality
        is_mp3 = is_only_audio and self._audio_format == "mp3"
        self._show_row(self._row_mp3q,    is_mp3)
        # FPS: solo si hay múltiples valores (ya se gestiona en _refresh_fps)
        # pero también ocultamos si no hay video
        if not is_video:
            self._row_fps.grid_remove()

    @staticmethod
    def _show_row(row: tk.Frame, visible: bool) -> None:
        if visible:
            row.grid()
        else:
            row.grid_remove()

    # ══════════════════════════════════════════════════════════════════════════
    # Callbacks de controles
    # ══════════════════════════════════════════════════════════════════════════
    def _on_mode_change(self, idx: int) -> None:
        self._mode = idx
        self._refresh_visibility()
        self._notify()

    def _on_res_changed(self, idx: int) -> None:
        if self._info and self._info.resolutions:
            self._resolution = self._info.resolutions[idx] if idx < len(self._info.resolutions) else None
        self._refresh_fps()
        self._refresh_vcodecs()
        self._notify()

    def _on_fps_changed(self, idx: int) -> None:
        vals = self._dd_fps._values
        if vals and idx < len(vals):
            try:
                self._fps = int(vals[idx].replace(" fps", ""))
            except ValueError:
                pass
        self._notify()

    def _on_hdr_changed(self, idx: int) -> None:
        vals = self._dd_hdr._values
        if vals and idx < len(vals):
            self._dynamic_range = vals[idx]
        self._notify()

    def _on_vcodec_changed(self, idx: int) -> None:
        vals = self._dd_vcodec._values
        if vals and idx < len(vals):
            self._video_codec = vals[idx]
        self._notify()

    def _on_container_changed(self, idx: int) -> None:
        vals = self._dd_container._values
        if vals and idx < len(vals):
            self._container = vals[idx]
        self._notify()

    def _on_lang_changed(self, idx: int) -> None:
        if self._info and self._info.languages and idx < len(self._info.languages):
            self._audio_lang = self._info.languages[idx]
        self._refresh_acodecs()
        self._refresh_drc()
        self._notify()

    def _on_acodec_changed(self, idx: int) -> None:
        vals = self._dd_acodec._values
        if vals and idx < len(vals):
            self._audio_codec = vals[idx]
        self._notify()

    def _on_aquality_changed(self, idx: int) -> None:
        vals = self._dd_aquality._values
        if vals and idx < len(vals):
            self._audio_quality = vals[idx]
        self._notify()

    def _on_drc_changed(self) -> None:
        self._drc = self._drc_var.get()
        self._notify()

    def _on_afmt_changed(self, idx: int) -> None:
        vals = self._dd_afmt._values
        if vals and idx < len(vals):
            self._audio_format = vals[idx]
            is_mp3 = self._audio_format == "mp3"
            self._show_row(self._row_mp3q, is_mp3)
        self._notify()

    def _on_mp3q_changed(self, idx: int) -> None:
        kbps_map = {0: "128", 1: "192", 2: "256", 3: "320"}
        self._mp3_quality = kbps_map.get(idx, "192")
        self._notify()

    def _notify(self) -> None:
        if self._on_args_changed:
            self._on_args_changed()

    # ══════════════════════════════════════════════════════════════════════════
    # Presets
    # ══════════════════════════════════════════════════════════════════════════
    def _preset_best(self) -> None:
        """Mejor calidad: mayor resolución, mejor códec, mejor audio."""
        if self._info is None:
            return
        self._seg_mode.set_index(MODE_VIDEO_AUDIO)
        self._mode = MODE_VIDEO_AUDIO
        # Mayor resolución
        if self._info.resolutions:
            self._dd_res.current(0)
            self._resolution = self._info.resolutions[0]
        # Mejor códec: AV1 > VP9 > H.264
        vals = self._dd_vcodec._values
        for preferred in ("AV1", "VP9", "H.264"):
            if preferred in vals:
                self._dd_vcodec.current(vals.index(preferred))
                self._video_codec = preferred
                break
        self._refresh_visibility()
        self._notify()

    def _preset_light(self) -> None:
        """Más ligero: 720p, AV1 o VP9."""
        if self._info is None:
            return
        self._seg_mode.set_index(MODE_VIDEO_AUDIO)
        self._mode = MODE_VIDEO_AUDIO
        # Buscar 720p o la más cercana por debajo
        target = 720
        candidates = [h for h in self._info.resolutions if h <= target]
        chosen = candidates[0] if candidates else (self._info.resolutions[-1] if self._info.resolutions else None)
        if chosen and chosen in self._info.resolutions:
            idx = self._info.resolutions.index(chosen)
            self._dd_res.current(idx)
            self._resolution = chosen
            self._refresh_vcodecs()
        vals = self._dd_vcodec._values
        for preferred in ("AV1", "VP9", "H.264"):
            if preferred in vals:
                self._dd_vcodec.current(vals.index(preferred))
                self._video_codec = preferred
                break
        self._refresh_visibility()
        self._notify()

    def _preset_compat(self) -> None:
        """Más compatible: H.264 + AAC + mp4."""
        if self._info is None:
            return
        self._seg_mode.set_index(MODE_VIDEO_AUDIO)
        self._mode = MODE_VIDEO_AUDIO
        # H.264
        vals = self._dd_vcodec._values
        if "H.264" in vals:
            self._dd_vcodec.current(vals.index("H.264"))
            self._video_codec = "H.264"
        # mp4
        cont_vals = self._dd_container._values
        if "mp4" in cont_vals:
            self._dd_container.current(cont_vals.index("mp4"))
            self._container = "mp4"
        # AAC
        avals = self._dd_acodec._values
        if "AAC" in avals:
            self._dd_acodec.current(avals.index("AAC"))
            self._audio_codec = "AAC"
        self._refresh_visibility()
        self._notify()

    def _preset_es(self) -> None:
        """Español (doblaje IA): mejor resolución + audio en español."""
        if self._info is None or not self._info.has_spanish_dubbed:
            return
        self._seg_mode.set_index(MODE_VIDEO_AUDIO)
        self._mode = MODE_VIDEO_AUDIO
        # Mejor resolución
        if self._info.resolutions:
            self._dd_res.current(0)
            self._resolution = self._info.resolutions[0]
        # Buscar idioma español
        for i, code in enumerate(self._info.languages):
            if code.startswith("es"):
                self._dd_lang.current(i)
                self._audio_lang = code
                self._refresh_acodecs()
                self._refresh_drc()
                break
        self._refresh_visibility()
        self._notify()

    # ══════════════════════════════════════════════════════════════════════════
    # Actualización de idioma de la UI
    # ══════════════════════════════════════════════════════════════════════════
    def _refresh_labels(self) -> None:
        """Re-aplica todas las etiquetas traducibles."""
        self._lbl_mode.configure(text=self._t("mode_label"))
        self._seg_mode.set_options(
            [
                self._t("mode_video_audio"),
                self._t("mode_video_only"),
                self._t("mode_audio_only"),
            ],
            active=self._mode,
        )
        for lbl, key in [
            (self._lbl_res,       "resolution"),
            (self._lbl_fps,       "fps_label"),
            (self._lbl_hdr,       "dynamic_range"),
            (self._lbl_vcodec,    "video_codec"),
            (self._lbl_container, "container"),
            (self._lbl_lang,      "audio_language"),
            (self._lbl_acodec,    "audio_codec"),
            (self._lbl_aquality,  "audio_quality"),
            (self._lbl_drc,       "drc_audio"),
            (self._lbl_afmt,      "audio_format"),
            (self._lbl_mp3q,      "mp3_quality"),
        ]:
            lbl.configure(text=self._t(key))
        self._chk_drc.configure(text=self._t("drc_tooltip_short"))
        for btn, key in [
            (self._btn_preset_best,   "preset_best"),
            (self._btn_preset_light,  "preset_light"),
            (self._btn_preset_compat, "preset_compat"),
            (self._btn_preset_es,     "preset_es"),
        ]:
            btn.configure(text=self._t(key))
