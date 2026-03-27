"""Entry point for WeeKTray.

Enforces a single-instance guard via a bound localhost socket, then launches TrayApp.

Run from the repo root in any of these ways:
    python -m src          (recommended, development)
    python src             (development)
    WeeKTray.exe           (production, PyInstaller build)
"""

from __future__ import annotations

import socket
import sys
from pathlib import Path

# A fixed high port used solely as a single-instance lock.
# If the port is already bound, another instance is running.
_LOCK_PORT = 47835
_lock_socket: socket.socket | None = None


def _acquire_instance_lock() -> bool:
    """Bind a localhost socket to act as a single-instance guard.

    Returns True if this is the first instance, False if another is running.
    Keeps the socket open for the lifetime of the process.
    """
    global _lock_socket  # noqa: PLW0603
    try:
        _lock_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _lock_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 0)
        _lock_socket.bind(("127.0.0.1", _LOCK_PORT))
        return True
    except OSError:
        return False  # Port already in use — another instance is running


def _ensure_importable() -> None:
    """Ensure the repo root is on sys.path so absolute imports work when the
    file is executed directly (e.g. python src\\__main__.py)."""
    repo_root = str(Path(__file__).resolve().parent.parent)
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)


def main() -> None:
    if not _acquire_instance_lock():
        sys.exit(0)

    try:
        from .app import TrayApp  # package mode: python -m src
    except ImportError:
        _ensure_importable()
        from src.app import TrayApp  # direct mode: python src\__main__.py

    app = TrayApp()
    app.run()


if __name__ == "__main__":
    main()

