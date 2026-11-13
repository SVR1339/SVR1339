#!/usr/bin/env python3
"""
Convert the marble-bust-with-headphones image into a high-density,
dark, bold '@' wave style ASCII-art SVG.
Outputs:
  - svr-ascii.svg (standalone terminal window)
  - data/ascii_rows.json (consumed by render_cards.py for hero.svg)
"""
import os, sys, html, json
import numpy as np
from PIL import Image, ImageEnhance, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
SRC = os.path.join(ROOT, "assets", "profile.jpg")
OUT = os.path.join(ROOT, "svr-ascii.svg")
ROWS_JSON = os.path.join(ROOT, "data", "ascii_rows.json")
os.makedirs(os.path.dirname(ROWS_JSON), exist_ok=True)

COLS = 180
ART_W_TARGET = 800
CELL_W = ART_W_TARGET / COLS
CELL_H = CELL_W * 15 / 8
ROWS = round(COLS * 8 / 15)  # 96 rows

PAD = 20
TITLEBAR_H = 30
STATUS_H = 30
ART_W = COLS * CELL_W
ART_H = ROWS * CELL_H
CANVAS_W = ART_W + PAD * 2
CANVAS_H = TITLEBAR_H + ART_H + STATUS_H + PAD

BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
TITLE_TEXT = "#7d8590"
INK = "#e6edf3"
CURSOR = "#58a6ff"

ROW_DUR = 5.8 / ROWS
STAGGER = ROW_DUR

# '@' Wave density ramp: dark glyphs dominated by @, %, #, S, s
RAMP_AT = " .-=+*sS#%@"

def generate():
    im = Image.open(SRC).convert("L")
    arr_full = np.array(im)

    # 1. Square crop centered on the sculpture to maintain true 1:1 classical proportions
    ys, xs = np.where(arr_full > 18)
    cx = (xs.min() + xs.max()) // 2
    cy = (ys.min() + ys.max()) // 2
    side = max(xs.max() - xs.min(), ys.max() - ys.min()) + 40
    x0 = max(0, cx - side // 2)
    y0 = max(0, cy - side // 2)
    im_sq = im.crop((x0, y0, min(im.width, x0 + side), min(im.height, y0 + side)))

    if im_sq.width != im_sq.height:
        sz = max(im_sq.width, im_sq.height)
        canvas = Image.new("L", (sz, sz), 0)
        canvas.paste(im_sq, ((sz - im_sq.width) // 2, (sz - im_sq.height) // 2))
        im_sq = canvas

    # Resize to exact ASCII resolution
    im_scaled = im_sq.resize((COLS, ROWS), Image.LANCZOS)

    # Local contrast & edge sharpening for bold, defined '@' waves
    im_eq = ImageOps.equalize(im_scaled)
    im_blend = Image.blend(im_scaled, im_eq, 0.65)
    im_sharp = ImageEnhance.Sharpness(im_blend).enhance(2.5)
    im_contrast = ImageEnhance.Contrast(im_sharp).enhance(1.6)
    arr_s = np.array(im_contrast) / 255.0

    # 1. Dark '@' Wave Paper Rows (for hero.svg)
    paper_rows = []
    for y in range(ROWS):
        chars = []
        for x in range(COLS):
            val = arr_s[y, x]
            if val < 0.12:
                chars.append(" ")
            else:
                norm = (val - 0.12) / 0.88
                norm_inv = pow(1.0 - norm, 0.52)
                idx = int(norm_inv * (len(RAMP_AT) - 1) + 0.5)
                idx = max(1, min(len(RAMP_AT) - 1, idx))
                chars.append(RAMP_AT[idx])
        paper_rows.append("".join(chars))

    # 2. Terminal Mode Rows
    term_rows = []
    for y in range(ROWS):
        chars = []
        for x in range(COLS):
            val = arr_s[y, x]
            if val < 0.12:
                chars.append(" ")
            else:
                norm = (val - 0.12) / 0.88
                idx = int(norm * (len(RAMP_AT) - 1) + 0.5)
                idx = max(0, min(len(RAMP_AT) - 1, idx))
                chars.append(RAMP_AT[idx])
        term_rows.append("".join(chars))

    with open(ROWS_JSON, "w", encoding="utf-8") as f:
        json.dump({"terminal": term_rows, "paper": paper_rows}, f)
    print(f"✓ Saved bold '@' wave ASCII rows ({len(paper_rows)} rows) to data/ascii_rows.json")

    # 3. Assemble svr-ascii.svg (standalone terminal card)
    art_top = TITLEBAR_H + PAD * 0.35
    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_W}" height="{CANVAS_H}" '
        f'viewBox="0 0 {CANVAS_W} {CANVAS_H}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">'
    )
    parts.append('<defs>'
                 f'<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
                 f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/>'
                 f'</linearGradient></defs>')
    parts.append(f'<rect width="{CANVAS_W}" height="{CANVAS_H}" rx="12" fill="url(#bg)"/>')
    parts.append(f'<rect x="0.5" y="0.5" width="{CANVAS_W-1}" height="{CANVAS_H-1}" rx="12" '
                 f'fill="none" stroke="{FRAME}" stroke-width="1"/>')
    parts.append(f'<line x1="0" y1="{TITLEBAR_H}" x2="{CANVAS_W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>')

    for i, dotcol in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        parts.append(f'<circle cx="{PAD + i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dotcol}"/>')
    parts.append(f'<text x="{CANVAS_W/2}" y="{TITLEBAR_H/2 + 4}" fill="{TITLE_TEXT}" font-size="12" '
                 f'text-anchor="middle">svr1339@github: ~$ ./sculpture.sh</text>')

    font_size = CELL_H * 0.90
    for ry, line in enumerate(term_rows):
        y = art_top + ry * CELL_H + CELL_H * 0.74
        row_y = art_top + ry * CELL_H
        delay = ry * STAGGER
        safe = html.escape(line)
        text = (f'<text xml:space="preserve" x="{PAD}" y="{y:.1f}" fill="{INK}" font-weight="700" '
                f'font-size="{font_size:.1f}" textLength="{ART_W}" lengthAdjust="spacing">{safe}</text>')

        parts.append(
            f'<clipPath id="r{ry}"><rect x="{PAD}" y="{row_y:.1f}" height="{CELL_H}" width="0">'
            f'<animate attributeName="width" from="0" to="{ART_W}" begin="{delay:.3f}s" '
            f'dur="{ROW_DUR:.2f}s" fill="freeze"/></rect></clipPath>'
        )
        parts.append(f'<g clip-path="url(#r{ry})">{text}</g>')
        parts.append(
            f'<rect y="{row_y+1:.1f}" width="{CELL_W}" height="{CELL_H-2}" fill="{CURSOR}" opacity="0">'
            f'<animate attributeName="x" from="{PAD}" to="{PAD+ART_W}" begin="{delay:.3f}s" '
            f'dur="{ROW_DUR:.2f}s" fill="freeze"/>'
            f'<set attributeName="opacity" to="0.85" begin="{delay:.3f}s"/>'
            f'<set attributeName="opacity" to="0" begin="{delay+ROW_DUR:.3f}s"/></rect>'
        )

    status_line_y = TITLEBAR_H + ART_H + PAD * 0.35
    status_y = status_line_y + 19
    parts.append(f'<line x1="0" y1="{status_line_y:.1f}" x2="{CANVAS_W}" y2="{status_line_y:.1f}" stroke="{FRAME}"/>')
    parts.append(f'<text x="{PAD}" y="{status_y:.1f}" fill="{TITLE_TEXT}" font-size="13">'
                 f'svr1339@github:~$ whoami <tspan fill="{INK}">Banda Sai Vardhan Reddy</tspan></text>')
    status_chars = len("svr1339@github:~$ whoami Banda Sai Vardhan Reddy ")
    parts.append(f'<rect x="{PAD + status_chars * 13 * 0.6:.1f}" y="{status_y-12:.1f}" width="8" height="14" fill="{CURSOR}">'
                 f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.51;1" '
                 f'dur="1s" repeatCount="indefinite"/></rect>')
    parts.append("</svg>")

    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))
    print("✓ Saved bold '@' wave terminal SVG to svr-ascii.svg")

if __name__ == "__main__":
    generate()
