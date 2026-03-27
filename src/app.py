"""Main TrayApp for WeeKTray."""

from __future__ import annotations

import threading
import time
from datetime import date, datetime, timedelta
from typing import Any

import pystray
from PIL import Image

from . import autostart, config, renderer, week

VERSION = "1.0.0"


def _seconds_until_midnight() -> float:
    """Return seconds until the next midnight."""
    now = datetime.now()
    tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=5, microsecond=0)
    return (tomorrow - now).total_seconds()


class TrayApp:
    def __init__(self) -> None:
        self._cfg: dict[str, Any] = config.load()
        self._icon: pystray.Icon | None = None
        self._stop_event = threading.Event()

    # ------------------------------------------------------------------
    # Icon / label helpers
    # ------------------------------------------------------------------

    def _build_image(self) -> Image.Image:
        info = week.get_week(self._cfg["week_format"])
        label = week.format_label(info, self._cfg["prefix"])
        return renderer.render_icon(
            label=label,
            text_color=self._cfg["text_color"],
            bg_color=self._cfg["bg_color"],
            font_family=self._cfg["font_family"],
            font_size=self._cfg["font_size"],
        )

    def _build_tooltip(self) -> str:
        info = week.get_week(self._cfg["week_format"])
        return week.format_tooltip(info, self._cfg["prefix"])

    # ------------------------------------------------------------------
    # Menu actions
    # ------------------------------------------------------------------

    def _on_about(self, icon: pystray.Icon, item: pystray.MenuItem) -> None:
        import ctypes  # noqa: PLC0415
        info = week.get_week(self._cfg["week_format"])
        label = week.format_label(info, self._cfg["prefix"])
        tooltip = week.format_tooltip(info, self._cfg["prefix"])
        ctypes.windll.user32.MessageBoxW(
            0,
            f"{tooltip}\n\nWeeKTray v{VERSION}\ngithub.com/j-karlsson/weektray",
            f"WeeKTray — {label}",
            0x40,  # MB_ICONINFORMATION
        )

    def _on_open_config(self, icon: pystray.Icon, item: pystray.MenuItem) -> None:
        config.open_in_editor()

    def _on_reload_config(self, icon: pystray.Icon, item: pystray.MenuItem) -> None:
        self._cfg = config.load()
        self._refresh_icon()

    def _on_toggle_autostart(self, icon: pystray.Icon, item: pystray.MenuItem) -> None:
        new_state = not autostart.is_enabled()
        autostart.set_enabled(new_state)
        self._cfg["autostart"] = new_state
        config.save(self._cfg)

    def _on_exit(self, icon: pystray.Icon, item: pystray.MenuItem) -> None:
        self._stop_event.set()
        icon.stop()

    # ------------------------------------------------------------------
    # Menu builder
    # ------------------------------------------------------------------

    def _build_menu(self) -> pystray.Menu:
        def autostart_label(item: pystray.MenuItem) -> str:  # noqa: ARG001
            return "Autostart: On" if autostart.is_enabled() else "Autostart: Off"

        def autostart_checked(item: pystray.MenuItem) -> bool:  # noqa: ARG001
            return autostart.is_enabled()

        return pystray.Menu(
            pystray.MenuItem("About", self._on_about),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Open Config", self._on_open_config),
            pystray.MenuItem("Reload Config", self._on_reload_config),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(autostart_label, self._on_toggle_autostart, checked=autostart_checked),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Exit", self._on_exit),
        )

    # ------------------------------------------------------------------
    # Refresh logic
    # ------------------------------------------------------------------

    def _refresh_icon(self) -> None:
        if self._icon is None:
            return
        self._icon.icon = self._build_image()
        self._icon.title = self._build_tooltip()

    def _refresh_loop(self) -> None:
        """Background thread: refresh on interval AND at each midnight."""
        while not self._stop_event.is_set():
            interval = float(self._cfg.get("refresh_interval_s", 60))
            secs_to_midnight = _seconds_until_midnight()
            wait = min(interval, secs_to_midnight)
            self._stop_event.wait(timeout=wait)
            if not self._stop_event.is_set():
                self._cfg = config.load()   # pick up any config edits
                self._refresh_icon()

    # ------------------------------------------------------------------
    # Run
    # ------------------------------------------------------------------

    def run(self) -> None:
        image = self._build_image()
        tooltip = self._build_tooltip()
        menu = self._build_menu()

        self._icon = pystray.Icon(
            name="WeeKTray",
            icon=image,
            title=tooltip,
            menu=menu,
        )

        refresh_thread = threading.Thread(target=self._refresh_loop, daemon=True)
        refresh_thread.start()

        self._icon.run()
