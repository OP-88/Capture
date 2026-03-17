#!/bin/bash
# capture-secure.sh: Runs Capture in a bubblewrap sandbox with zero network access.
# This provides OS-level security similar to the Snap confinement.

set -e

# Path to the project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if ! command -v bwrap >/dev/null 2>&1; then
    echo "ERROR: bubblewrap (bwrap) is not installed. This is required for sandboxing."
    echo "Install it with: sudo dnf install bubblewrap"
    exit 1
fi

echo "Launching Capture in a secure sandbox (Network Disabled)..."

# Build the sandbox
# --unshare-net: Disconnects the process from the host network
# --dev /dev: Mounts a minimal /dev
# --proc /proc: Mounts /proc
# --tmpfs /tmp: Mounts a temporary /tmp
# --ro-bind /usr /usr: Mounts /usr as read-only
# --ro-bind /bin /bin: Mounts /bin as read-only
# --ro-bind /lib /lib: Mounts /lib as read-only
# --ro-bind /lib64 /lib64: Mounts /lib64 as read-only
# --ro-bind /etc /etc: Mounts /etc as read-only (needed for fonts, etc)
# --bind $HOME $HOME: Mounts HOME (needed for user data and config)
# --dir /run/user/$(id -u): Mounts XDG_RUNTIME_DIR (needed for Wayland/X11)
# --bind /run/user/$(id -u) /run/user/$(id -u): Binds the runtime dir
# --setenv DISPLAY "$DISPLAY": Passes DISPLAY env var
# --setenv XDG_RUNTIME_DIR "$XDG_RUNTIME_DIR": Passes runtime dir

exec bwrap \
    --unshare-net \
    --dev /dev \
    --proc /proc \
    --tmpfs /tmp \
    --ro-bind /usr /usr \
    --ro-bind /bin /bin \
    --ro-bind /lib /lib \
    --ro-bind /lib64 /lib64 \
    --ro-bind /etc /etc \
    --bind "$HOME" "$HOME" \
    --bind "/run/user/$(id -u)" "/run/user/$(id -u)" \
    --setenv DISPLAY "$DISPLAY" \
    --setenv XDG_RUNTIME_DIR "$XDG_RUNTIME_DIR" \
    --setenv WAYLAND_DISPLAY "$WAYLAND_DISPLAY" \
    --setenv PATH "/usr/bin:/bin" \
    --chdir "$PROJECT_ROOT" \
    python3 run.py
