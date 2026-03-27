"""Week-number calculation helpers for WeeKTray.

Supports two standards:
  ISO 8601  — week starts Monday, week 1 contains the first Thursday (strftime %V)
  US        — week starts Sunday, week 1 is the week containing January 1 (strftime %U)
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import NamedTuple


class WeekInfo(NamedTuple):
    number: int          # 1-53
    year: int            # ISO week year (may differ from calendar year for ISO)
    standard: str        # "ISO" or "US"
    week_start: date     # first day of this week
    week_end: date       # last day of this week


def _iso_week(today: date) -> WeekInfo:
    iso_year, iso_week, iso_weekday = today.isocalendar()
    # ISO week starts Monday (weekday 1)
    start = today - timedelta(days=iso_weekday - 1)
    end = start + timedelta(days=6)
    return WeekInfo(iso_week, iso_year, "ISO", start, end)


def _us_week(today: date) -> WeekInfo:
    # US weeks start Sunday; strftime %U counts 0-based from Jan 1 Sunday-aligned
    week_num = int(today.strftime("%U"))
    year = today.year
    # Sunday of this week
    sunday = today - timedelta(days=today.weekday() + 1) if today.weekday() != 6 else today
    saturday = sunday + timedelta(days=6)
    return WeekInfo(week_num, year, "US", sunday, saturday)


def get_week(standard: str = "ISO", today: date | None = None) -> WeekInfo:
    """Return WeekInfo for *today* (defaults to current date) under *standard*."""
    if today is None:
        today = date.today()
    if standard.upper() == "ISO":
        return _iso_week(today)
    return _us_week(today)


def format_label(info: WeekInfo, prefix: str = "W") -> str:
    """Return the tray icon label string, e.g. 'W42' or 'KW5'."""
    return f"{prefix}{info.number}"


def format_tooltip(info: WeekInfo, prefix: str = "W") -> str:
    """Return a rich tooltip string, e.g. 'W42 · Mon 14 Oct – Sun 20 Oct 2025 (ISO)'."""
    label = format_label(info, prefix)
    # Use .day (int) to avoid platform-specific strftime padding flags (%-d vs %#d)
    start_str = f"{info.week_start.strftime('%a')} {info.week_start.day} {info.week_start.strftime('%b')}"
    end_str = f"{info.week_end.strftime('%a')} {info.week_end.day} {info.week_end.strftime('%b %Y')}"
    return f"{label} · {start_str} – {end_str} ({info.standard})"
