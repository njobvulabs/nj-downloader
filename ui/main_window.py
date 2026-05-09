import queue
import customtkinter as ctk
from utils import clean_url
from ui.url_frame import UrlFrame
from ui.options_frame import OptionsFrame
from ui.progress_frame import ProgressFrame
from ui.queue_frame import QueueFrame

STATUS_MAP = {
    'pending': 'Pending',
    'downloading': 'Downloading',
    'completed': 'Completed',
    'error': 'Error',
    'cancelled': 'Cancelled',
}
COMPLETED_STATES = {'completed', 'error', 'cancelled'}
POLL_MS = 150


class MainWindow(ctk.CTkFrame):
    def __init__(self, parent, download_manager, on_toggle_theme=None):
        super().__init__(parent)
        self.download_manager = download_manager
        self.on_toggle_theme = on_toggle_theme
        self.queue = []
        self._next_id = 0
        self._is_downloading = False
        self._info_queues = {}
        self._dl_queue = None
        self._dl_item = None
        self._build()

    def _build(self):
        self.url_frame = UrlFrame(
            self,
            on_add_url=self._on_add_url,
            on_toggle_theme=self.on_toggle_theme,
        )
        self.url_frame.pack(fill='x', padx=15, pady=(15, 0))

        self.options_frame = OptionsFrame(self)
        self.options_frame.pack(fill='x', padx=15, pady=(10, 0))

        self.queue_frame = QueueFrame(self)
        self.queue_frame.pack(fill='both', expand=True, padx=15, pady=(10, 0))

        self.progress_frame = ProgressFrame(self)
        self.progress_frame.pack(fill='x', padx=15, pady=(10, 15))

        self.queue_frame.download_btn.configure(command=self._start_download)
        self.queue_frame.remove_btn.configure(command=self._remove_selected)
        self.queue_frame.cancel_btn.configure(command=self._cancel_downloads)
        self.queue_frame.clear_btn.configure(command=self._clear_completed)

    # --- URL handling ---------------------------------------------------

    def _on_add_url(self, url):
        url = clean_url(url)
        self.progress_frame.set_status('Parsing URL...')
        info_queue = self.download_manager.extract_info(url)
        self._info_queues[url] = info_queue
        self.after(POLL_MS, self._poll_info, url, info_queue)

    def _poll_info(self, url, info_queue):
        if url not in self._info_queues:
            return
        try:
            info = info_queue.get_nowait()
            del self._info_queues[url]
            self._on_info(url, info)
        except queue.Empty:
            self.after(POLL_MS, self._poll_info, url, info_queue)

    def _on_info(self, url, info):
        if info.get('_type') == 'error':
            self.progress_frame.set_status(
                f'Error: {info.get("error", "Unknown error")}',
            )
            return

        if info.get('_type') == 'playlist' and info.get('entries'):
            entries = [e for e in info['entries'] if e]
            playlist_title = info.get('title', 'Untitled Playlist')
            added = 0
            for entry in entries:
                entry_url = entry.get('url')
                if not entry_url:
                    continue
                entry_title = entry.get('title', 'Unknown')
                item = {
                    'id': self._next_id,
                    'url': entry_url,
                    'title': entry_title,
                    'type': 'Video',
                    'status': 'pending',
                    'info': entry,
                }
                self._next_id += 1
                self.queue.append(item)
                self.queue_frame.append(item['id'], 'Pending', entry_title, 'Video')
                added += 1

            self.progress_frame.set_status(
                f'Added {added} items from playlist: {playlist_title}',
            )
            return

        title = info.get('title', url)
        item = {
            'id': self._next_id,
            'url': url,
            'title': title,
            'type': 'Video',
            'status': 'pending',
            'info': info,
        }
        self._next_id += 1
        self.queue.append(item)
        self.queue_frame.append(item['id'], 'Pending', title, 'Video')
        self.progress_frame.set_status(f'Added: {title}')

    # --- Download orchestration -----------------------------------------

    def _start_download(self):
        if self._is_downloading:
            return
        self._is_downloading = True
        self.progress_frame.set_status('Starting downloads...')
        self._download_next()

    def _download_next(self):
        for item in self.queue:
            if item['status'] == 'pending':
                self._do_download(item)
                return
        self._is_downloading = False
        self.progress_frame.set_status('All downloads completed!')

    def _do_download(self, item):
        item['status'] = 'downloading'
        self.queue_frame.set_status(item['id'], 'Downloading')
        self.progress_frame.set_status(f'Downloading: {item["title"]}')

        options = self.options_frame.get_options()

        self._dl_queue = self.download_manager.download(item['url'], options)
        self._dl_item = item
        self.after(POLL_MS, self._poll_download)

    def _poll_download(self):
        if self._dl_queue is None:
            return
        try:
            while True:
                msg = self._dl_queue.get_nowait()
                if msg['type'] == 'progress':
                    self._on_progress(msg['data'])
                elif msg['type'] == 'complete':
                    self._on_complete(msg)
                    return
                elif msg['type'] == 'abort':
                    self._on_complete({'status': 'cancelled'})
                    return
        except queue.Empty:
            pass
        self.after(POLL_MS, self._poll_download)

    def _on_progress(self, data):
        self.progress_frame.update(data)
        info = data.get('info_dict', {})
        playlist_index = info.get('playlist_index')
        if playlist_index:
            self.progress_frame.set_status(
                '({}/{}) {}'.format(
                    playlist_index,
                    info.get('playlist_count', '?'),
                    self._dl_item['title'],
                )
            )

    def _on_complete(self, result):
        status = result['status']
        self._dl_item['status'] = status
        self.queue_frame.set_status(
            self._dl_item['id'], STATUS_MAP.get(status, status),
        )
        self.progress_frame.reset()
        self._dl_queue = None

        if status == 'completed':
            self.progress_frame.set_status(
                f'Completed: {self._dl_item["title"]}',
            )
        elif status == 'error':
            self.progress_frame.set_status(
                f'Error: {result.get("error", "Unknown")}',
            )
        elif status == 'cancelled':
            self.progress_frame.set_status('Download cancelled')
            self._is_downloading = False
            for qitem in self.queue:
                if qitem['status'] == 'pending':
                    qitem['status'] = 'cancelled'
                    self.queue_frame.set_status(qitem['id'], 'Cancelled')
            return

        self._dl_item = None
        self._download_next()

    # --- Queue management -----------------------------------------------

    def _remove_selected(self):
        selected = self.queue_frame.get_selected_ids()
        if not selected:
            return
        self.queue = [
            item for item in self.queue if item['id'] not in selected
        ]
        for sid in selected:
            self.queue_frame.delete(sid)

    def _cancel_downloads(self):
        self.download_manager.cancel_all()
        self.progress_frame.set_status('Cancelling...')

    def _clear_completed(self):
        self.queue = [
            item for item in self.queue
            if item['status'] not in COMPLETED_STATES
        ]
        display_items = [
            {
                'id': item['id'],
                'status_display': STATUS_MAP.get(
                    item['status'], item['status'],
                ),
                'title': item['title'],
                'type': item['type'],
            }
            for item in self.queue
        ]
        self.queue_frame.rebuild(display_items)
