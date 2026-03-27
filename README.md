# WeeKTray

A lightweight Windows 11 system-tray application that shows the current **week number** next to the clock — fully configurable and portable.

![WeeKTray tray icon showing W42](docs/screenshot.png)

---

## Features

| Feature | Details |
|---|---|
| **Week display** | Renders `W42` (or your custom prefix) as the tray icon |
| **ISO & US weeks** | ISO 8601 (Mon-start) or US (Sun-start) — switchable in config |
| **Configurable prefix** | `W`, `KW`, empty string, or anything you like |
| **Custom font & colors** | Font family, size, text color, background color (RGBA) |
| **Rich tooltip** | Hover to see the full week date range, e.g. `W42 · Mon 14 – Sun 20 Oct 2025 (ISO)` |
| **Autostart** | Right-click → toggle autostart; no manual registry editing |
| **Hot-reload config** | Right-click → Reload Config — no restart needed |
| **Portable** | Single `.exe`, config next to the exe |
| **Single instance** | Second launch exits silently |
| **Midnight refresh** | Icon updates automatically when the week rolls over |

---

## Quick Start

1. **Download** `WeeKTray.exe` from the [latest release](../../releases/latest).
2. **Run** it — a week-number icon appears in the system tray.
3. **Right-click** the icon to access all options.
4. To **enable autostart**, right-click → *Autostart: Off* (it will flip to *On*).

---

## Configuration

WeeKTray reads `config.json` from the **same folder as the `.exe`** (portable mode).  
On first run with *Open Config*, a `config.json` is created automatically.

| Key | Type | Default | Description |
|---|---|---|---|
| `week_format` | string | `"ISO"` | `"ISO"` (ISO 8601, Mon-start) or `"US"` (Sun-start) |
| `prefix` | string | `"W"` | Text before the week number — e.g. `"W"`, `"KW"`, `""` |
| `font_family` | string | `"Arial"` | Windows font name (must exist in `C:\Windows\Fonts`) |
| `font_size` | integer | `10` | Point size; auto-shrunk if text overflows the icon |
| `text_color` | string | `"#FFFFFF"` | Text color as `#RRGGBB` |
| `bg_color` | string | `"#00000000"` | Background color as `#RRGGBBAA` (`AA=00` = transparent) |
| `autostart` | boolean | `false` | Managed via the tray menu — do not edit manually |
| `refresh_interval_s` | integer | `60` | Seconds between icon redraws (also refreshes at midnight) |

### Example `config.json`

```json
{
    "week_format": "ISO",
    "prefix": "W",
    "font_family": "Segoe UI",
    "font_size": 9,
    "text_color": "#00FF99",
    "bg_color": "#00000000",
    "autostart": true,
    "refresh_interval_s": 60
}
```

---

## Tray Context Menu

| Item | Action |
|---|---|
| **About** | Shows current week info and version |
| **Open Config** | Opens `config.json` in Notepad |
| **Reload Config** | Hot-reloads config without restarting |
| **Autostart: On/Off** | Toggles Windows Registry autostart for the current user |
| **Exit** | Quits WeeKTray |

---

## Build from Source

### Prerequisites

- Python 3.11+
- Windows (for tray & autostart features; other platforms can run in dev mode)

### Steps

```bash
git clone https://github.com/j-karlsson/weektray.git
cd weektray

# Create a virtual environment (recommended)
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run in development mode (from the repo root)
python -m src

# Build a standalone .exe
pyinstaller weektray.spec
# Output: dist/WeeKTray.exe
```

### GitHub Actions

Pushing a tag like `v1.2.3` automatically builds and publishes a GitHub Release with `WeeKTray.exe` attached.

```bash
git tag v1.0.0
git push origin v1.0.0
```

---

## Week Number Standards

**ISO 8601** (default, used across Europe and most of the world):
- Week starts on **Monday**
- Week 1 is the week containing the **first Thursday** of the year
- Implemented via Python's `date.isocalendar()`

**US / North American**:
- Week starts on **Sunday**
- Week 1 is the week containing **January 1**
- Implemented via `strftime("%U")`

---

## License

MIT — see [LICENSE](LICENSE).
