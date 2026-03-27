"""Windows Registry autostart management for WeeKTray.

Writes / removes an entry under:
  HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run

This approach requires no elevation (UAC) and only affects the current user.
"""

from __future__ import annotations

import sys
from pathlib import Path

APP_NAME = "WeeKTray"
_REG_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"


def _exe_path() -> str:
    """Return the path that should be registered for autostart."""
    if getattr(sys, "frozen", False):
        return str(Path(sys.executable).resolve())
    # In dev mode, point at the Python interpreter + this package
    python = Path(sys.executable).resolve()
    src_dir = Path(__file__).resolve().parent
    return f'"{python}" "{src_dir}"'


def is_enabled() -> bool:
    """Return True if the autostart registry entry exists."""
    try:
        import winreg  # noqa: PLC0415
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _REG_KEY) as key:
            winreg.QueryValueEx(key, APP_NAME)
            return True
    except (OSError, ImportError):
        return False


def enable() -> None:
    """Add the autostart registry entry."""
    try:
        import winreg  # noqa: PLC0415
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, _REG_KEY, 0, winreg.KEY_SET_VALUE
        ) as key:
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, _exe_path())
    except ImportError:
        pass  # Not running on Windows


def disable() -> None:
    """Remove the autostart registry entry if it exists."""
    try:
        import winreg  # noqa: PLC0415
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, _REG_KEY, 0, winreg.KEY_SET_VALUE
        ) as key:
            try:
                winreg.DeleteValue(key, APP_NAME)
            except OSError:
                pass  # Already absent
    except ImportError:
        pass


def set_enabled(state: bool) -> None:
    """Enable or disable autostart based on *state*."""
    if state:
        enable()
    else:
        disable()
