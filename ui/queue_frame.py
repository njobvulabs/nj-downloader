import customtkinter as ctk
from utils import format_bytes

STATUS_COLORS = {
    'Pending': ('gray', 'gray'),
    'Downloading': ('#FFA500', '#FFA500'),
    'Completed': ('#00CC66', '#00CC66'),
    'Error': ('#FF4444', '#FF4444'),
    'Cancelled': ('#888888', '#888888'),
    'Paused': ('#5599FF', '#5599FF'),
}


class QueueRow(ctk.CTkFrame):
    def __init__(self, parent, item_id, status, title, type_, size, on_select):
        super().__init__(parent, corner_radius=4, fg_color=('gray90', 'gray25'), height=32)
        self.pack_propagate(False)

        self.item_id = item_id
        self.status = status
        self._on_select = on_select
        self.selected = False

        color = STATUS_COLORS.get(status, ('white', 'white'))
        self.status_label = ctk.CTkLabel(
            self, text=status, text_color=color,
            width=90, anchor='w',
        )
        self.status_label.pack(side='left', padx=(8, 5), pady=6)

        self.title_label = ctk.CTkLabel(self, text=title, anchor='w')
        self.title_label.pack(side='left', fill='x', expand=True, padx=5, pady=6)

        size_text = format_bytes(size)
        self.size_label = ctk.CTkLabel(self, text=size_text, width=80, anchor='e')
        self.size_label.pack(side='right', padx=5, pady=6)

        self.type_label = ctk.CTkLabel(self, text=type_, width=80, anchor='e')
        self.type_label.pack(side='right', padx=(5, 8), pady=6)

        self.bind('<Button-1>', self._click)
        self.status_label.bind('<Button-1>', self._click)
        self.title_label.bind('<Button-1>', self._click)
        self.size_label.bind('<Button-1>', self._click)
        self.type_label.bind('<Button-1>', self._click)

    def _click(self, event):
        if self._on_select:
            self._on_select(self.item_id)

    def select(self):
        self.selected = True
        self.configure(fg_color=('#3a7ebf', '#1f538d'))

    def deselect(self):
        self.selected = False
        self.configure(fg_color=('gray90', 'gray25'))

    def update_status(self, status):
        self.status = status
        color = STATUS_COLORS.get(status, ('white', 'white'))
        self.status_label.configure(text=status, text_color=color)

    def update_title(self, title):
        self.title_label.configure(text=title)

    def update_type(self, type_):
        self.type_label.configure(text=type_)


class QueueFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self._rows = {}
        self._selected_ids = set()
        self._build()

    def _build(self):
        ctk.CTkLabel(
            self, text='Download Queue',
            font=ctk.CTkFont(size=14, weight='bold'),
        ).pack(anchor='w', padx=5, pady=(5, 0))

        header = ctk.CTkFrame(self, fg_color='transparent')
        header.pack(fill='x', padx=5, pady=(2, 0))
        ctk.CTkLabel(
            header, text='Status', width=90, anchor='w',
            font=ctk.CTkFont(size=12, weight='bold'),
        ).pack(side='left', padx=(8, 5))
        ctk.CTkLabel(
            header, text='Title', anchor='w',
            font=ctk.CTkFont(size=12, weight='bold'),
        ).pack(side='left', fill='x', expand=True, padx=5)
        ctk.CTkLabel(
            header, text='Type', width=80, anchor='e',
            font=ctk.CTkFont(size=12, weight='bold'),
        ).pack(side='right', padx=(5, 8))
        ctk.CTkLabel(
            header, text='Size', width=80, anchor='e',
            font=ctk.CTkFont(size=12, weight='bold'),
        ).pack(side='right', padx=5)

        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.pack(fill='both', expand=True, padx=5, pady=2)

        btn_frame = ctk.CTkFrame(self, fg_color='transparent')
        btn_frame.pack(fill='x', padx=5, pady=(2, 5))

        self.download_btn = ctk.CTkButton(btn_frame, text='Download All')
        self.download_btn.pack(side='left', padx=(0, 5))

        self.remove_btn = ctk.CTkButton(btn_frame, text='Remove Selected')
        self.remove_btn.pack(side='left', padx=(0, 5))

        self.cancel_btn = ctk.CTkButton(btn_frame, text='Cancel Downloads')
        self.cancel_btn.pack(side='left', padx=(0, 5))

        self.pause_btn = ctk.CTkButton(btn_frame, text='Pause')
        self.pause_btn.pack(side='left', padx=(0, 5))

        self.retry_btn = ctk.CTkButton(btn_frame, text='Retry Failed')
        self.retry_btn.pack(side='left', padx=(0, 5))

        self.clear_btn = ctk.CTkButton(btn_frame, text='Clear Completed')
        self.clear_btn.pack(side='left')

    def _on_row_select(self, item_id):
        if item_id in self._selected_ids:
            self._selected_ids.discard(item_id)
        else:
            self._selected_ids.add(item_id)

        for iid, row in self._rows.items():
            if iid in self._selected_ids:
                row.select()
            else:
                row.deselect()

    def append(self, item_id, status, title, type_, size):
        row = QueueRow(
            self.scroll_frame, item_id, status, title, type_, size,
            on_select=self._on_row_select,
        )
        row.pack(fill='x', padx=2, pady=1)
        self._rows[item_id] = row

    def set_status(self, item_id, status):
        if item_id in self._rows:
            self._rows[item_id].update_status(status)

    def delete(self, item_id):
        if item_id in self._rows:
            self._rows[item_id].destroy()
            del self._rows[item_id]
            self._selected_ids.discard(item_id)

    def get_selected_ids(self):
        return list(self._selected_ids)

    def get_all_ids(self):
        return list(self._rows.keys())

    def rebuild(self, items):
        for row in list(self._rows.values()):
            row.destroy()
        self._rows.clear()
        self._selected_ids.clear()
        for item in items:
            self.append(
                item['id'], item['status_display'],
                item['title'], item['type'], item.get('size'),
            )
