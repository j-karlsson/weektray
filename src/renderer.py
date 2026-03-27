"""Tray icon renderer for WeeKTray.

Renders a short text label (e.g. "W42") onto a transparent 32×32 RGBA image
using Pillow. The font size is auto-shrunk so the text always fits.
"""

from __future__ import annotations

import io
from pathlib import Path
from typing import TYPE_CHECKING

from PIL import Image, ImageDraw, ImageFont

if TYPE_CHECKING:
    pass

ICON_SIZE = (32, 32)
_FONT_CACHE: dict[tuple[str, int], ImageFont.FreeTypeFont | ImageFont.ImageFont] = {}


def _parse_color(hex_color: str) -> tuple[int, ...]:
    """Parse a #RRGGBB or #RRGGBBAA hex string to an RGBA tuple."""
    h = hex_color.lstrip("#")
    if len(h) == 6:
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return (r, g, b, 255)
    if len(h) == 8:
        r, g, b, a = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), int(h[6:8], 16)
        return (r, g, b, a)
    raise ValueError(f"Invalid color: {hex_color!r}")


def _load_font(
    family: str,
    size: int,
) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    key = (family, size)
    if key in _FONT_CACHE:
        return _FONT_CACHE[key]

    font: ImageFont.FreeTypeFont | ImageFont.ImageFont
    # Try to load from Windows font directory
    win_font_dir = Path("C:/Windows/Fonts")
    candidates = [
        win_font_dir / f"{family}.ttf",
        win_font_dir / f"{family}bd.ttf",   # bold variant
        win_font_dir / f"{family.lower()}.ttf",
        win_font_dir / f"{family.lower()}bd.ttf",
        win_font_dir / "arial.ttf",          # safe fallback
    ]
    for candidate in candidates:
        if candidate.exists():
            try:
                font = ImageFont.truetype(str(candidate), size)
                _FONT_CACHE[key] = font
                return font
            except OSError:
                continue

    # Last resort: Pillow's built-in bitmap font (no size control)
    font = ImageFont.load_default()
    _FONT_CACHE[key] = font
    return font


def _text_bbox(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont | ImageFont.ImageFont) -> tuple[int, int]:
    """Return (width, height) of rendered text."""
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def render_icon(
    label: str,
    text_color: str = "#FFFFFF",
    bg_color: str = "#00000000",
    font_family: str = "Arial",
    font_size: int = 10,
) -> Image.Image:
    """Render *label* onto a 32×32 RGBA image and return it."""
    bg_rgba = _parse_color(bg_color)
    text_rgba = _parse_color(text_color)

    img = Image.new("RGBA", ICON_SIZE, bg_rgba)
    draw = ImageDraw.Draw(img)

    w, h = ICON_SIZE
    # Auto-shrink font size until text fits with 1-px padding
    size = font_size
    while size >= 4:
        font = _load_font(font_family, size)
        tw, th = _text_bbox(draw, label, font)
        if tw <= w - 2 and th <= h - 2:
            break
        size -= 1
    else:
        font = _load_font(font_family, 4)
        tw, th = _text_bbox(draw, label, font)

    x = (w - tw) // 2
    y = (h - th) // 2
    draw.text((x, y), label, font=font, fill=text_rgba)
    return img


def image_to_pil(img: Image.Image) -> Image.Image:
    """Return the image as-is (pystray accepts PIL Images directly)."""
    return img
