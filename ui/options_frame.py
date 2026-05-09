import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk


class OptionsFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self._build()

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
        )
        self.quality_menu.grid(row=0, column=1, sticky='w', padx=(0, 15))

        ctk.CTkLabel(inner, text='Format:').grid(row=0, column=2, sticky='w', padx=(0, 5))
        self.container_var = ctk.StringVar(value='MP4')
        self.container_menu = ctk.CTkOptionMenu(
            inner, variable=self.container_var,
            values=['MP4', 'WebM', 'MKV'],
            width=80,
        )
        self.container_menu.grid(row=0, column=3, sticky='w', padx=(0, 15))

        self.subtitles_var = tk.IntVar(value=0)
        self.subtitles_cb = ctk.CTkCheckBox(
            inner, text='Subtitles',
            variable=self.subtitles_var, onvalue=1, offvalue=0,
        )
        self.subtitles_cb.grid(row=0, column=4, sticky='w')

        ctk.CTkLabel(inner, text='Output:').grid(row=1, column=0, sticky='w', padx=(0, 5), pady=(5, 0))
        self.output_var = ctk.StringVar(value=self._default_output_dir())
        self.output_entry = ctk.CTkEntry(inner, textvariable=self.output_var)
        self.output_entry.grid(row=1, column=1, columnspan=3, sticky='ew', padx=(0, 5), pady=(5, 0))

        self.browse_btn = ctk.CTkButton(inner, text='Browse', width=70, command=self._browse)
        self.browse_btn.grid(row=1, column=4, sticky='w', pady=(5, 0))

        inner.columnconfigure(1, weight=1)

    def _default_output_dir(self):
        import os
        return os.path.expanduser('~/Downloads/nj-downloader')

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
