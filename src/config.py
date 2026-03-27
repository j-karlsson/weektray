"""Configuration management for WeeKTray.

Loads config.json from the same directory as the executable (portable mode).
Missing keys are back-filled from DEFAULTS so new fields are always available.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

DEFAULTS: dict[str, Any] = {
    "week_format": "ISO",       # "ISO" | "US"
    "prefix": "",              # e.g. "W", "KW", "" — displayed as "{prefix}{week}"
    "font_family": "Arial",     # Windows font name
    "font_size": 40,            # point size; renderer auto-shrinks if needed
    "text_color": "#FFFFFF",    # hex RGB
    "bg_color": "#00000000",    # hex RGBA (transparent by default)
    "autostart": False,         # managed via tray menu; written back here
    "refresh_interval_s": 60,   # seconds between icon redraws
}


def _config_dir() -> Path:
    """Return the directory that holds config.json.

    When running as a PyInstaller bundle, that is next to the .exe.
    When running as plain Python (dev mode), that is the repo root.
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    # dev: two levels up from src/config.py → repo root
    return Path(__file__).resolve().parent.parent


def config_path() -> Path:
    return _config_dir() / "config.json"


def default_config_path() -> Path:
    """Return the bundled config.default.json path (read-only reference)."""
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / "config.default.json"  # noqa: SLF001
    return Path(__file__).resolve().parent.parent / "config.default.json"


def load() -> dict[str, Any]:
    """Load config.json, merging with DEFAULTS for any missing keys."""
    path = config_path()
    data: dict[str, Any] = {}
    if path.exists():
        try:
            with path.open(encoding="utf-8") as fh:
                data = json.load(fh)
            # Strip internal comment key if someone copied from default
            data.pop("_comment", None)
        except (json.JSONDecodeError, OSError):
            data = {}
    # Back-fill defaults for any missing keys
    merged = {**DEFAULTS, **{k: v for k, v in data.items() if k in DEFAULTS}}
    return merged


def save(cfg: dict[str, Any]) -> None:
    """Persist current config to disk."""
    path = config_path()
    # Only write known keys
    cleaned = {k: cfg[k] for k in DEFAULTS if k in cfg}
    with path.open("w", encoding="utf-8") as fh:
        json.dump(cleaned, fh, indent=4)
        fh.write("\n")


def open_in_editor() -> None:
    """Open config.json in Notepad (creates it first if missing)."""
    import subprocess  # noqa: PLC0415
    path = config_path()
    if not path.exists():
        # Create from defaults so the user has something to edit
        save(DEFAULTS.copy())
    subprocess.Popen(["notepad.exe", str(path)])  # noqa: S603, S607
