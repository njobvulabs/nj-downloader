#!/usr/bin/env bash
# nj-downloader installer
# Supports: Debian/Ubuntu, Fedora/RHEL, Arch/Manjaro
# Usage:
#   ./install.sh              # user-local install (~/.local)
#   sudo ./install.sh         # system-wide install (/opt)
#   ./install.sh --uninstall  # remove user-local install
#   sudo ./install.sh --uninstall  # remove system-wide install

set -euo pipefail

APP_NAME="nj-downloader"
APP_DIR_SYSTEM="/opt/${APP_NAME}"
APP_DIR_USER="${HOME}/.local/share/${APP_NAME}"
BIN_DIR_USER="${HOME}/.local/bin"
DESKTOP_DIR_USER="${HOME}/.local/share/applications"
ICON_DIR_USER="${HOME}/.local/share/icons/hicolor/scalable/apps"
PIP_REQUIREMENTS="$(dirname "$0")/requirements.txt"

# --- Detect distro ----------------------------------------------------------

detect_distro() {
    if command -v apt &>/dev/null; then
        echo "debian"
    elif command -v dnf &>/dev/null; then
        echo "fedora"
    elif command -v pacman &>/dev/null; then
        echo "arch"
    else
        echo "unknown"
    fi
}

install_system_deps() {
    local distro="$1"
    echo "==> Installing system dependencies..."

    case "$distro" in
        debian)
            sudo apt update
            sudo apt install -y ffmpeg python3 python3-pip python3-venv
            ;;
        fedora)
            sudo dnf install -y ffmpeg python3 python3-pip python3-virtualenv
            ;;
        arch)
            sudo pacman -Sy --noconfirm ffmpeg python python-pip python-virtualenv
            ;;
        *)
            echo "WARNING: Unknown distro. Please install manually: ffmpeg, python3, pip."
            echo "  Debian/Ubuntu: sudo apt install ffmpeg python3 python3-pip python3-venv"
            echo "  Fedora:        sudo dnf install ffmpeg python3 python3-pip python3-virtualenv"
            echo "  Arch:          sudo pacman -S ffmpeg python python-pip python-virtualenv"
            ;;
    esac
}

# --- File operations (copies app from script dir to target) ------------------

copy_app() {
    local target="$1"
    local src="$(dirname "$0")"

    echo "==> Copying app to ${target}..."
    mkdir -p "$target"
    cp -r "$src/app.py" "$src/config.py" "$src/downloader.py" \
          "$src/main.py" "$src/utils.py" "$src/requirements.txt" \
          "$src/nj-downloader.desktop" "$src/nj-downloader.svg" \
          "$target/"
    cp -r "$src/ui" "$target/"
}

setup_venv() {
    local target="$1"
    echo "==> Creating Python virtual environment..."
    python3 -m venv "${target}/venv"
    "${target}/venv/bin/pip" install -r "${target}/requirements.txt" -q
    echo "==> Python dependencies installed."
}

create_launcher() {
    local target="$1"
    local launcher="${target}/nj-downloader"

    echo "==> Creating launcher script..."
    cat > "$launcher" << LAUNCHER_EOF
#!/usr/bin/env bash
DIR="\$(dirname "\$(readlink -f "\$0")")"
cd "\$DIR"
source "\$DIR/venv/bin/activate"
exec python main.py "\$@"
LAUNCHER_EOF
    chmod +x "$launcher"
}

# --- Install modes -----------------------------------------------------------

install_user() {
    echo ""
    echo "=== Installing ${APP_NAME} (user-local) ==="
    echo ""

    if ! command -v python3 &>/dev/null; then
        echo "ERROR: python3 is required. Install it first."
        exit 1
    fi

    mkdir -p "$APP_DIR_USER" "$BIN_DIR_USER" "$DESKTOP_DIR_USER" "$ICON_DIR_USER"

    copy_app "$APP_DIR_USER"
    setup_venv "$APP_DIR_USER"
    create_launcher "$APP_DIR_USER"

    # Symlink to ~/.local/bin
    ln -sf "${APP_DIR_USER}/nj-downloader" "${BIN_DIR_USER}/nj-downloader"

    # Install icon
    cp "${APP_DIR_USER}/nj-downloader.svg" "${ICON_DIR_USER}/nj-downloader.svg"

    # Install .desktop file
    sed -e "s|Exec=nj-downloader|Exec=${BIN_DIR_USER}/nj-downloader|g" \
        -e "s|Icon=nj-downloader|Icon=${ICON_DIR_USER}/nj-downloader.svg|g" \
        -e "s|StartupNotify=true|StartupNotify=true|g" \
        "${APP_DIR_USER}/nj-downloader.desktop" \
        > "${DESKTOP_DIR_USER}/nj-downloader.desktop"
    chmod +x "${DESKTOP_DIR_USER}/nj-downloader.desktop"

    # Refresh desktop database if available
    if command -v update-desktop-database &>/dev/null; then
        update-desktop-database "${HOME}/.local/share/applications/" 2>/dev/null || true
    fi

    echo ""
    echo "=== Install complete ==="
    echo ""
    echo "Make sure ${BIN_DIR_USER} is in your PATH."
    echo "If not, add this to your shell config:"
    echo '  export PATH="$HOME/.local/bin:$PATH"'
    echo ""
    echo "Launch from terminal: nj-downloader"
    echo "Or find 'nj-downloader' in your app menu (log out/in may be needed)."
}

install_system() {
    echo ""
    echo "=== Installing ${APP_NAME} (system-wide) ==="
    echo ""

    # Check for root
    if [[ "$EUID" -ne 0 ]]; then
        echo "ERROR: System-wide install requires root. Run with: sudo $0"
        exit 1
    fi

    install_system_deps "$(detect_distro)"

    copy_app "$APP_DIR_SYSTEM"
    setup_venv "$APP_DIR_SYSTEM"
    create_launcher "$APP_DIR_SYSTEM"

    # Symlink to /usr/local/bin
    ln -sf "${APP_DIR_SYSTEM}/nj-downloader" /usr/local/bin/nj-downloader

    # Install .desktop file
    cp "${APP_DIR_SYSTEM}/nj-downloader.desktop" /usr/share/applications/nj-downloader.desktop
    chmod 644 /usr/share/applications/nj-downloader.desktop

    # Install icon
    mkdir -p /usr/share/icons/hicolor/scalable/apps
    cp "${APP_DIR_SYSTEM}/nj-downloader.svg" /usr/share/icons/hicolor/scalable/apps/nj-downloader.svg

    # Update icon cache
    if command -v gtk-update-icon-cache &>/dev/null; then
        gtk-update-icon-cache -f /usr/share/icons/hicolor/ 2>/dev/null || true
    fi

    echo ""
    echo "=== Install complete ==="
    echo ""
    echo "Launch from terminal: nj-downloader"
    echo "Or find 'nj-downloader' in your app menu."
}

# --- Uninstall ---------------------------------------------------------------

uninstall_user() {
    echo "==> Removing user-local install..."

    rm -f "${HOME}/.local/bin/nj-downloader"
    rm -f "${HOME}/.local/share/applications/nj-downloader.desktop"
    rm -f "${HOME}/.local/share/icons/hicolor/scalable/apps/nj-downloader.svg"
    rm -rf "$APP_DIR_USER"

    echo "==> Removed."
}

uninstall_system() {
    echo "==> Removing system-wide install..."

    rm -f /usr/local/bin/nj-downloader
    rm -f /usr/share/applications/nj-downloader.desktop
    rm -f /usr/share/icons/hicolor/scalable/apps/nj-downloader.svg
    rm -rf "$APP_DIR_SYSTEM"

    if command -v gtk-update-icon-cache &>/dev/null; then
        gtk-update-icon-cache -f /usr/share/icons/hicolor/ 2>/dev/null || true
    fi

    echo "==> Removed."
}

# --- Main --------------------------------------------------------------------

main() {
    case "${1:-}" in
        --uninstall|-u)
            if [[ "$EUID" -eq 0 ]]; then
                uninstall_system
            else
                uninstall_user
            fi
            ;;
        --help|-h)
            echo "Usage: $0 [--uninstall|--help]"
            echo ""
            echo "  Without args: installs app"
            echo "  Run as root  : system-wide install (/opt/${APP_NAME})"
            echo "  Run as user  : user-local install (~/.local/share/${APP_NAME})"
            echo "  --uninstall  : removes the install"
            exit 0
            ;;
        *)
            if [[ "$EUID" -eq 0 ]]; then
                install_system
            else
                install_user
            fi
            ;;
    esac
}

main "$@"
