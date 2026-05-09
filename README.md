# nj-downloader

GUI video downloader powered by yt-dlp and CustomTkinter.

<img width="1366" height="719" alt="nj-downloader" src="https://github.com/user-attachments/assets/152429ca-8bd8-435f-8e65-ff317be3a24d" />


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

## Getting Started

```bash
git clone https://github.com/njobvulabs/nj-downloader.git
cd nj-downloader
```

Then choose one of the options below.

### Quick start — run without installing

```bash
./run.sh
```

Creates a virtual environment, installs dependencies, and launches the app right away.

### User-local install (no sudo, appears in app menu)

```bash
./install.sh
```

Installs to `~/.local/share/nj-downloader/`, creates a launcher symlink in `~/.local/bin/`, and registers the app in your desktop menu. Log out/in may be needed for the menu entry to appear.

### System-wide install (requires sudo)

```bash
sudo ./install.sh
```

Installs to `/opt/nj-downloader/`, automatically installs system dependencies (ffmpeg, python3, pip), and registers the app for all users.

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
