import customtkinter as ctk
from utils import format_bytes, format_eta


class ProgressFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self._build()

    def _build(self):
        ctk.CTkLabel(
            self, text='Progress',
            font=ctk.CTkFont(size=14, weight='bold'),
        ).pack(anchor='w', padx=5, pady=(5, 0))

        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.set(0.0)
        self.progress_bar.pack(fill='x', padx=5, pady=(5, 2))

        info = ctk.CTkFrame(self, fg_color='transparent')
        info.pack(fill='x', padx=5)

        self.percent_var = ctk.StringVar(value='0%')
        ctk.CTkLabel(info, textvariable=self.percent_var, width=60).pack(side='left')

        self.speed_var = ctk.StringVar(value='Speed: --')
        ctk.CTkLabel(info, textvariable=self.speed_var, width=160).pack(side='left', padx=(5, 0))

        self.eta_var = ctk.StringVar(value='ETA: --:--:--')
        ctk.CTkLabel(info, textvariable=self.eta_var, width=150).pack(side='left', padx=(5, 0))

        self.size_var = ctk.StringVar(value='Size: --')
        ctk.CTkLabel(info, textvariable=self.size_var, width=220).pack(side='left', padx=(5, 0))

        self.phase_var = ctk.StringVar(value='')
        self.phase_label = ctk.CTkLabel(
            info, textvariable=self.phase_var,
            width=120, anchor='e',
        )
        self.phase_label.pack(side='right', padx=(5, 0))

        self.status_var = ctk.StringVar(value='Ready')
        ctk.CTkLabel(self, textvariable=self.status_var, anchor='w').pack(
            fill='x', padx=5, pady=(2, 5),
        )

    def update(self, data):
        status = data.get('status')

        if status == 'downloading':
            total = data.get('total_bytes') or data.get('total_bytes_estimate', 0)
            downloaded = data.get('downloaded_bytes', 0)
            speed = data.get('speed')
            eta = data.get('eta')

            if total > 0:
                percent = downloaded / total
                self.progress_bar.set(percent)
                self.percent_var.set(f'{percent * 100:.1f}%')
            else:
                self.progress_bar.set(0)
                self.percent_var.set('--%')

            self.speed_var.set(
                f'Speed: {format_bytes(speed)}/s' if speed else 'Speed: --'
            )
            self.eta_var.set(f'ETA: {format_eta(eta)}')
            self.size_var.set(
                f'Size: {format_bytes(downloaded)} / {format_bytes(total)}'
            )

            info_dict = data.get('info_dict', {})
            vcodec = info_dict.get('vcodec', '')
            acodec = info_dict.get('acodec', '')
            if vcodec and vcodec != 'none' and (not acodec or acodec == 'none'):
                self.phase_var.set('Video stream')
            elif acodec and acodec != 'none' and (not vcodec or vcodec == 'none'):
                self.phase_var.set('Audio stream')
            else:
                self.phase_var.set('')

        elif status == 'finished':
            self.progress_bar.set(1.0)
            self.percent_var.set('100%')
            self.phase_var.set('Processing...')
            self.status_var.set('Merging video & audio...')

    def reset(self):
        self.progress_bar.set(0.0)
        self.percent_var.set('0%')
        self.speed_var.set('Speed: --')
        self.eta_var.set('ETA: --:--:--')
        self.size_var.set('Size: --')
        self.phase_var.set('')

    def set_status(self, text):
        self.status_var.set(text)
