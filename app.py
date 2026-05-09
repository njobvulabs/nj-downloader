import customtkinter as ctk
import config as cfg
from downloader import DownloadManager
from ui.main_window import MainWindow


class App:
    def __init__(self):
        self.config = cfg.load()
        ctk.set_appearance_mode(self.config['theme'])
        ctk.set_default_color_theme('blue')

        self.root = ctk.CTk()
        self.root.title('nj-downloader')
        self.root.geometry('800x650')
        self.root.minsize(650, 450)

        self.download_manager = DownloadManager()
        self.main_window = MainWindow(
            self.root, self.download_manager,
            on_toggle_theme=self._toggle_theme,
        )
        self.main_window.pack(fill='both', expand=True)

        self.root.protocol('WM_DELETE_WINDOW', self._on_close)

    def _toggle_theme(self):
        current = ctk.get_appearance_mode()
        new = 'Light' if current == 'Dark' else 'Dark'
        ctk.set_appearance_mode(new)
        self.config['theme'] = new
        cfg.save(self.config)

    def _on_close(self):
        self.download_manager.cancel_all()
        self.root.destroy()

    def run(self):
        self.root.mainloop()
