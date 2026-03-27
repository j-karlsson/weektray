"""Entry point for WeeKTray.

Enforces a single-instance guard via a Windows named mutex, then launches TrayApp.

Run from the repo root in any of these ways:
    python -m src          (recommended, development)
    python src             (development)
    WeeKTray.exe           (production, PyInstaller build)
"""

from __future__ import annotations

import sys
from pathlib import Path


def _ensure_importable() -> None:
    """Ensure the repo root is on sys.path so absolute imports work when the
    file is executed directly (e.g. python src\\__main__.py)."""
    repo_root = str(Path(__file__).resolve().parent.parent)
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)


def _acquire_mutex() -> object | None:
    """Create a named Windows mutex.

    Returns the mutex handle (to keep it alive) or None on non-Windows.
    If the mutex already exists, exits the process immediately.
    """
    try:
        import ctypes  # noqa: PLC0415

        handle = ctypes.windll.kernel32.CreateMutexW(None, True, "Global\\WeeKTray_SingleInstance")
        last_error = ctypes.windll.kernel32.GetLastError()
        if last_error == 183:  # ERROR_ALREADY_EXISTS
            sys.exit(0)
        return handle
    except (AttributeError, OSError):
        return None  # Non-Windows dev environment


def main() -> None:
    mutex = _acquire_mutex()  # keep reference alive for process lifetime

    try:
        from .app import TrayApp  # package mode: python -m src
    except ImportError:
        _ensure_importable()
        from src.app import TrayApp  # direct mode: python src\__main__.py

    app = TrayApp()
    app.run()

    del mutex  # released on exit


if __name__ == "__main__":
    main()
