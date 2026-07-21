# AGENTS.md

## What this is

Python GUI video downloader using CustomTkinter + yt-dlp. Single flat package, no build system, no tests, no linter.

## Run

```bash
./run.sh
```

Creates venv if needed, installs deps from `requirements.txt`, runs `python main.py`. Requires Python 3.10+ and `ffmpeg` on PATH.

## Architecture

- `main.py` → entrypoint, instantiates `App`
- `app.py` → wires config, `DownloadManager`, and `MainWindow` together; saves window geometry on close
- `downloader.py` → `DownloadManager` spawns `_DownloadThread` per download; communicates via `queue.Queue`; extract_info threads are cancellable via `threading.Event`
- `config.py` → reads/writes `~/.config/nj-downloader/config.json`; single source of truth for all defaults (`DEFAULT` dict)
- `utils.py` → formatting helpers, YouTube URL tracking-param stripping (`clean_url`)
- `ui/` → CustomTkinter frames:
  - `main_window.py` → orchestrates queue, polling (`after(POLL_MS, ...)`), download lifecycle, pause/resume, retry
  - `url_frame.py` → URL entry with auto-paste on focus (detects clipboard URLs)
  - `options_frame.py` → quality/format/subtitles/output; persists changes to config via callback; Browse uses native OS folder picker (zenity/kdialog), no tkinter fallback
  - `queue_frame.py` → scrollable queue with status colors; buttons: Download All, Remove, Pause, Retry Failed, Clear Completed
  - `progress_frame.py` → progress bar, speed, ETA, size, DASH phase display

## Conventions

- All GUI classes subclass `ctk.CTkFrame`. Frame composition is all `pack()`, no `grid` or `place` (except `OptionsFrame` inner layout uses `grid`).
- Threading model: download threads push messages to a `queue.Queue`; the main thread polls every 150 ms via `self.after()`. Never call yt-dlp from the main thread.
- Config is a plain dict with keys: `theme`, `output_dir`, `quality`, `container`, `subtitles`, `window_geometry`. Persisted as JSON.
- Quality values are display strings like `'4K (2160p)'`, `'Audio Only'` — mapped to yt-dlp format strings in `downloader.py` and size estimates in `utils.py`.
- All output dir defaults come from `config.DEFAULT['output_dir']` — never hardcode elsewhere.

## Keyboard shortcuts

- `Ctrl+Return` → start download
- `Ctrl+R` → retry selected failed/paused items
- `Ctrl+P` → pause active download
- `Escape` → cancel all downloads
- `Delete` → remove selected queue items

## Download states

`pending` → `downloading` → `completed` | `error` | `paused` | `cancelled`

- **Pause** cancels the current thread but marks the item `paused` (not `cancelled`). The partial file stays on disk; yt-dlp resumes it automatically on re-download.
- **Retry** resets `error`/`cancelled`/`paused` items back to `pending` and starts the queue.

## Gotchas

- There is **no lint, typecheck, or test suite**. If you add one, wire it into a script or note the command here.
- `install.sh` copies source files (not the whole repo) to the install target — `venv/`, `.git/`, `__pycache__/` are excluded.
- YouTube URLs with a `list=` param on a single-video path get the playlist param stripped (`clean_url` in `utils.py:29`) to avoid accidental playlist expansion.
- `POLL_MS = 150` in `ui/main_window.py` controls the progress polling interval. Changing it affects responsiveness.
- `OptionsFrame` uses `grid` for its inner layout (unlike the rest of the UI which uses `pack`).
