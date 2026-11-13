#!/usr/bin/env python3
"""
make_ascii_svg.py
Converts the marble-bust-with-headphones image into a stylised
ASCII-art SVG with a row-by-row typewriter animation.

Technique:
  1. Load image, crop to square, resize to ASCII grid
  2. For each pixel: pick a density char from the ramp based on luminance
  3. Write each row as an SVG <text> element with progressive animation delay
  4. Output: cards/portrait.svg  (embedded, no external deps)
"""

import base64, math
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter

ROOT    = Path(__file__).parent.parent
ASSETS  = ROOT / "assets"
CARDS   = ROOT / "cards"
CARDS.mkdir(exist_ok=True)

IMG_PATH = ASSETS / "profile.jpg"

# ── ASCII ramp (dense → empty) ──────────────────────────────────────────────
# Fine-tuned for the marble bust: emphasise texture & shadow
RAMP = '@#S%?*+;:,. '[::-1]   # lightest → darkest

COLS = 55   # characters wide
ROWS = 60   # characters tall
CHAR_W = 8  # px per char in SVG
CHAR_H = 13 # px per row

# ── palette ──────────────────────────────────────────────────────────────────
BG_COLOR   = "#0a0a0a"
TEXT_COLOR = "#d4c5a9"   # warm marble/parchment
DIM_COLOR  = "#2a2110"
AMBER      = "#f5a623"
FONT       = "Geist Mono, 'Cascadia Code', 'Fira Code', Menlo, monospace"

def luminance(r, g, b):
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def image_to_ascii(path: Path) -> list[str]:
    img = Image.open(path).convert("RGB")

    # Square crop from center
    w, h = img.size
    side = min(w, h)
    img = img.crop(((w-side)//2, (h-side)//2, (w+side)//2, (h+side)//2))

    # Enhance contrast slightly to bring out marble texture
    img = ImageEnhance.Contrast(img).enhance(1.3)
    img = ImageEnhance.Sharpness(img).enhance(1.5)

    # Resize to ASCII grid (double cols for aspect ratio)
    img = img.resize((COLS * 2, ROWS), Image.LANCZOS)
    img = img.resize((COLS, ROWS), Image.LANCZOS)   # squish back

    rows = []
    px = img.load()
    for y in range(ROWS):
        row = ""
        for x in range(COLS):
            r, g, b = px[x, y]
            lum = luminance(r, g, b)
            idx = int((lum / 255) * (len(RAMP) - 1))
            row += RAMP[idx]
        rows.append(row)
    return rows

def make_portrait_svg(rows: list[str]) -> str:
    SVG_W = COLS * CHAR_W + 24
    SVG_H = ROWS * CHAR_H + 24

    lines = []
    for i, row in enumerate(rows):
        delay  = f"{i * 0.028:.3f}s"
        # Colour: brighter chars get the amber accent, dim chars get marble
        y = 16 + i * CHAR_H
        escaped = row.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
        lines.append(
            f'<text x="12" y="{y}" '
            f'font-family="{FONT}" font-size="11" fill="{TEXT_COLOR}" '
            f'letter-spacing="0" '
            f'style="animation:fadeRow 0.25s ease {delay} both;opacity:0">'
            f'{escaped}</text>'
        )

    css = "\n".join([
        "@keyframes fadeRow{from{opacity:0;transform:translateX(-4px)}to{opacity:1;transform:translateX(0)}}",
    ])

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{SVG_W}" height="{SVG_H}">
<defs><style>{css}</style></defs>
<rect width="{SVG_W}" height="{SVG_H}" fill="{BG_COLOR}"/>
{''.join(chr(10)+l for l in lines)}
</svg>"""
    return svg

def run():
    if not IMG_PATH.exists():
        print(f"⚠  {IMG_PATH} not found — skipping portrait")
        return
    print("  🖼  Converting marble bust to ASCII portrait…")
    rows = image_to_ascii(IMG_PATH)
    svg  = make_portrait_svg(rows)
    out  = CARDS / "portrait.svg"
    out.write_text(svg, encoding="utf-8")
    print(f"  ✓ portrait.svg  ({COLS}×{ROWS} chars, {out.stat().st_size//1024}KB)")

if __name__ == "__main__":
    run()
