import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk


class OptionsFrame(ctk.CTkFrame):
    def __init__(self, parent, config=None, on_config_change=None):
        super().__init__(parent)
        self._config = config or {}
        self._on_config_change = on_config_change
        self._build()
        self._load_from_config()

    def _build(self):
        ctk.CTkLabel(
            self, text='Options',
            font=ctk.CTkFont(size=14, weight='bold'),
        ).pack(anchor='w', padx=5, pady=(5, 0))

        inner = ctk.CTkFrame(self, fg_color='transparent')
        inner.pack(fill='x', padx=5, pady=(5, 5))

        ctk.CTkLabel(inner, text='Quality:').grid(row=0, column=0, sticky='w', padx=(0, 5))
        self.quality_var = ctk.StringVar(value='Best')
        self.quality_menu = ctk.CTkOptionMenu(
            inner, variable=self.quality_var,
            values=['Best', '4K (2160p)', '2K (1440p)', '1080p', '720p', '480p', '360p', 'Audio Only'],
            width=130,
            command=lambda _: self._save_to_config(),
        )
        self.quality_menu.grid(row=0, column=1, sticky='w', padx=(0, 15))

        ctk.CTkLabel(inner, text='Format:').grid(row=0, column=2, sticky='w', padx=(0, 5))
        self.container_var = ctk.StringVar(value='MP4')
        self.container_menu = ctk.CTkOptionMenu(
            inner, variable=self.container_var,
            values=['MP4', 'WebM', 'MKV'],
            width=80,
            command=lambda _: self._save_to_config(),
        )
        self.container_menu.grid(row=0, column=3, sticky='w', padx=(0, 15))

        self.subtitles_var = tk.IntVar(value=0)
        self.subtitles_cb = ctk.CTkCheckBox(
            inner, text='Subtitles',
            variable=self.subtitles_var, onvalue=1, offvalue=0,
            command=self._save_to_config,
        )
        self.subtitles_cb.grid(row=0, column=4, sticky='w')

        ctk.CTkLabel(inner, text='Output:').grid(row=1, column=0, sticky='w', padx=(0, 5), pady=(5, 0))
        self.output_var = ctk.StringVar(value=self._default_output_dir())
        self.output_entry = ctk.CTkEntry(inner, textvariable=self.output_var)
        self.output_entry.grid(row=1, column=1, columnspan=3, sticky='ew', padx=(0, 5), pady=(5, 0))
        self.output_var.trace_add('write', lambda *_: self._save_to_config())

        self.browse_btn = ctk.CTkButton(inner, text='Browse', width=70, command=self._browse)
        self.browse_btn.grid(row=1, column=4, sticky='w', pady=(5, 0))

        inner.columnconfigure(1, weight=1)

    def _default_output_dir(self):
        from config import DEFAULT
        return DEFAULT['output_dir']

    def _load_from_config(self):
        self.quality_var.set(self._config.get('quality', 'Best'))
        self.container_var.set(self._config.get('container', 'MP4'))
        self.subtitles_var.set(1 if self._config.get('subtitles', False) else 0)
        output = self._config.get('output_dir', self._default_output_dir())
        self.output_var.set(output)

    def _save_to_config(self):
        if not self._on_config_change:
            return
        self._config['quality'] = self.quality_var.get()
        self._config['container'] = self.container_var.get()
        self._config['subtitles'] = bool(self.subtitles_var.get())
        output = self.output_entry.get().strip()
        if output:
            self._config['output_dir'] = output
        self._on_config_change(self._config)

    def _browse(self):
        path = filedialog.askdirectory(title='Select Download Directory')
        if path:
            self.output_var.set(path)

    def get_options(self):
        output = self.output_entry.get().strip()
        if not output:
            output = self._default_output_dir()
        return {
            'quality': self.quality_var.get(),
            'container': self.container_var.get(),
            'subtitles': bool(self.subtitles_var.get()),
            'output_dir': output,
        }
