import threading
import queue
import os
import yt_dlp


class AbortDownload(Exception):
    pass


class DownloadManager:
    def __init__(self):
        self._threads = []
        self._cancelled = False

    def extract_info(self, url):
        q = queue.Queue()

        def _extract():
            try:
                opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'extract_flat': 'in_playlist',
                }
                with yt_dlp.YoutubeDL(opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                q.put(info)
            except Exception as e:
                q.put({'_type': 'error', 'error': str(e)})

        t = threading.Thread(target=_extract, daemon=True)
        t.start()
        self._threads.append(t)
        return q

    def download(self, url, options):
        q = queue.Queue()
        t = _DownloadThread(url, options, q)
        t.start()
        self._threads.append(t)
        return q

    def cancel_all(self):
        for t in self._threads:
            t.cancel()
        self._threads.clear()


class _DownloadThread(threading.Thread):
    def __init__(self, url, options, result_queue):
        super().__init__()
        self.url = url
        self.options = options
        self.queue = result_queue
        self._cancelled = False
        self.daemon = True

    def cancel(self):
        self._cancelled = True

    def progress_hook(self, d):
        if self._cancelled:
            self.queue.put({'type': 'abort'})
            raise AbortDownload('Cancelled by user')
        self.queue.put({'type': 'progress', 'data': d})

    def run(self):
        try:
            output_dir = self.options.get(
                'output_dir', os.path.expanduser('~/Downloads/nj-downloader'),
            )
            os.makedirs(output_dir, exist_ok=True)

            ydl_opts = {
                'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
                'progress_hooks': [self.progress_hook],
                'quiet': True,
                'no_warnings': True,
                'ignoreerrors': True,
                'restrictfilenames': True,
            }

            quality = self.options.get('quality', 'Best')
            container = self.options.get('container', 'MP4')
            subtitles = self.options.get('subtitles', False)
            playlist_items = self.options.get('playlist_items')

            if quality == 'Audio Only':
                ydl_opts['format'] = 'bestaudio/best'
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                }]
            else:
                quality_map = {
                    'Best': None,
                    '4K (2160p)': 2160,
                    '2K (1440p)': 1440,
                    '1080p': 1080,
                    '720p': 720,
                    '480p': 480,
                    '360p': 360,
                }
                max_h = quality_map.get(quality)
                if max_h:
                    ydl_opts['format'] = (
                        f'bestvideo[height<={max_h}]+bestaudio/best[height<={max_h}]'
                    )
                else:
                    ydl_opts['format'] = 'bestvideo+bestaudio/best'

                container_map = {'MP4': 'mp4', 'WebM': 'webm', 'MKV': 'mkv'}
                if container in container_map:
                    ydl_opts['merge_output_format'] = container_map[container]

            if subtitles:
                ydl_opts['writesubtitles'] = True
                ydl_opts['writeautomaticsub'] = True
                ydl_opts['subtitleslangs'] = ['en']

            if playlist_items:
                ydl_opts['playlist_items'] = playlist_items

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])

            self.queue.put({'type': 'complete', 'status': 'completed'})

        except AbortDownload:
            pass
        except Exception as e:
            self.queue.put({'type': 'complete', 'status': 'error', 'error': str(e)})
