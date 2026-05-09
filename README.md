# nj-downloader

GUI video downloader powered by yt-dlp and CustomTkinter.

## Features

- Download videos from YouTube and 1000+ other sites
- Quality selection: Best, 4K, 1440p, 1080p, 720p, 480p, 360p, Audio Only
- Format: MP4, WebM, MKV
- **Playlist support** — automatically expands playlists into individual selectable items
- **DASH stream awareness** — shows "Video stream" / "Audio stream" / "Merging" phases
- **Theme toggle** — switch between Dark and Light mode (persisted)
- **YouTube tracking param stripping** — pasted URLs don't accidentally trigger playlist downloads
- Download queue with sequential processing
- Subtitle auto-download (English)
- Real-time progress bar, speed, ETA, file size
- Cancel active downloads, remove queue items, clear completed
- Custom output directory
- **App menu integration** — appears in your desktop launcher after install

## Requirements

- Python 3.10+
- ffmpeg (for format merging and audio extraction)

## Install

Choose one:

### User-local install (no sudo)

```bash
./install.sh
```

Installs to `~/.local/share/nj-downloader/` and creates a launcher. The app appears in your app menu (log out/in may be needed).

### System-wide install

```bash
sudo ./install.sh
```

Installs to `/opt/nj-downloader/`, installs system dependencies (ffmpeg, python3, pip), and registers the app for all users.

### Quick start (no install)

```bash
./run.sh
```

Creates a virtual environment, installs dependencies, and launches the app.

### Uninstall

```bash
./install.sh --uninstall          # user-local
sudo ./install.sh --uninstall     # system-wide
```

## Usage

1. Paste a video or playlist URL
2. Click **Add to Queue**
   - Single video → added as one item
   - Playlist → expanded into individual videos (remove unwanted ones)
3. Select quality, format, and options
4. Click **Download All**
5. Monitor progress — DASH streams show separate video/audio phases
6. Files are saved to `~/Downloads/nj-downloader/` (configurable)

### Theme toggle

Click the sun/moon button (☾ / ☀) next to "Add to Queue" to switch between Dark and Light mode. Your preference is saved automatically.
