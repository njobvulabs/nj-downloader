import tkinter as tk
import customtkinter as ctk


class UrlFrame(ctk.CTkFrame):
    def __init__(self, parent, on_add_url=None, on_add_playlist=None, on_toggle_theme=None):
        super().__init__(parent)
        self.on_add_url = on_add_url
        self.on_add_playlist = on_add_playlist
        self.on_toggle_theme = on_toggle_theme
        self._build()

    def _build(self):
        ctk.CTkLabel(
            self, text='URL',
            font=ctk.CTkFont(size=14, weight='bold'),
        ).pack(anchor='w', padx=5, pady=(5, 5))

        row = ctk.CTkFrame(self, fg_color='transparent')
        row.pack(fill='x', padx=5, pady=(0, 5))

        self.entry = ctk.CTkEntry(row, placeholder_text='Paste video or playlist URL...')
        self.entry.pack(side='left', fill='x', expand=True, padx=(0, 5))

        self.paste_btn = ctk.CTkButton(row, text='Paste', width=70, command=self._paste)
        self.paste_btn.pack(side='left', padx=(0, 5))

        self.add_btn = ctk.CTkButton(row, text='Add to Queue', command=self._add)
        self.add_btn.pack(side='left', padx=(0, 5))

        self.add_playlist_btn = ctk.CTkButton(
            row, text='Add Playlist', width=100, command=self._add_playlist,
        )
        self.add_playlist_btn.pack(side='left', padx=(0, 5))

        self.theme_btn = ctk.CTkButton(
            row, text='', width=40, command=self._toggle_theme,
        )
        self.theme_btn.pack(side='left', padx=(5, 0))
        self._update_theme_button()

        self.entry.bind('<Return>', lambda e: self._add())
        self.entry.bind('<FocusIn>', lambda e: self._auto_paste())

    def _update_theme_button(self):
        mode = ctk.get_appearance_mode()
        self.theme_btn.configure(text='\u263E' if mode == 'Dark' else '\u2600')

    def _toggle_theme(self):
        if self.on_toggle_theme:
            self.on_toggle_theme()
            self._update_theme_button()

    def _paste(self):
        try:
            text = self.winfo_toplevel().clipboard_get()
            self.entry.delete(0, 'end')
            self.entry.insert(0, text)
        except tk.TclError:
            pass

    def _auto_paste(self):
        if self.entry.get().strip():
            return
        try:
            text = self.winfo_toplevel().clipboard_get().strip()
            if text.startswith(('http://', 'https://')):
                self.entry.insert(0, text)
        except tk.TclError:
            pass

    def _add(self):
        url = self.entry.get().strip()
        if url and self.on_add_url:
            self.on_add_url(url)
            self.entry.delete(0, 'end')

    def _add_playlist(self):
        url = self.entry.get().strip()
        if url and self.on_add_playlist:
            self.on_add_playlist(url)
            self.entry.delete(0, 'end')
