#!/usr/bin/env python3
"""
Generate high-fidelity, high-contrast 3D Roman marble bust ASCII art with headphones.
Features:
  - Natural whitespace and delicate punctuation for highlights (forehead, nose, lit cheek)
  - Dense, bold '@' wave glyphs for deep contours, beard curls, and headphones
  - True 1:1 square aspect ratio (180 cols x 96 rows, cell ratio 15:8)
"""
import os, sys, html, json
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance

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
ROWS = round(COLS * 8 / 15)  # exactly 96 rows

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

RAMP_PAPER = "  ..::--==++**ssSS##%%@@@@"
RAMP_TERM = " .:=+*sS#%@@"

def generate():
    im = Image.open(SRC).convert("L")
    arr = np.array(im)

    # 1. 1:1 Square bounding box centered on sculpture
    ys, xs = np.where(arr > 25)
    cx = int((xs.min() + xs.max()) / 2)
    cy = int((ys.min() + ys.max()) / 2)
    bw = xs.max() - xs.min()
    bh = ys.max() - ys.min()
    side = int(max(bw, bh) * 1.05)

    sq_im = Image.new("L", (side, side), 0)
    x0 = cx - side // 2
    y0 = cy - side // 2

    crop_x0 = max(0, x0)
    crop_y0 = max(0, y0)
    crop_x1 = min(im.width, x0 + side)
    crop_y1 = min(im.height, y0 + side)
    cropped = im.crop((crop_x0, crop_y0, crop_x1, crop_y1))
    sq_im.paste(cropped, (crop_x0 - x0, crop_y0 - y0))

    grid = sq_im.resize((COLS, ROWS), Image.LANCZOS)
    g_arr = np.array(grid).astype(np.float32) / 255.0

    # Difference of Gaussians (DoG) for sharp contour extraction
    g1 = grid.filter(ImageFilter.GaussianBlur(radius=0.8))
    g2 = grid.filter(ImageFilter.GaussianBlur(radius=2.5))
    arr_g1 = np.array(g1).astype(np.float32) / 255.0
    arr_g2 = np.array(g2).astype(np.float32) / 255.0
    dog = np.clip((arr_g2 - arr_g1) * 3.6, 0.0, 1.0)

    # Edges
    edges = grid.filter(ImageFilter.FIND_EDGES)
    e_arr = np.array(edges).astype(np.float32) / 255.0

    paper_rows = []
    term_rows = []

    for y in range(ROWS):
        p_chars = []
        t_chars = []
        for x in range(COLS):
            v = g_arr[y, x]
            e = e_arr[y, x]
            d = dog[y, x]

            if v < 0.12:
                p_chars.append(" ")
                t_chars.append(" ")
            else:
                # PAPER 3D SCULPTURE:
                # Bright marble highlights -> let paper show through (spaces or subtle dots)
                # Shadows & contours -> dense bold '@' wave characters
                shadow = np.clip((0.96 - v) / 0.84, 0.0, 1.0)
                contour = max(e * 1.6, d * 1.9)
                ink = max(contour * 0.88, pow(shadow, 1.35))

                if ink < 0.09:
                    p_chars.append(" ")
                else:
                    idx_p = int(ink * (len(RAMP_PAPER) - 1))
                    idx_p = min(len(RAMP_PAPER) - 1, max(0, idx_p))
                    p_chars.append(RAMP_PAPER[idx_p])

                # TERMINAL PHOSPHOR:
                lum = min(1.0, max(0.0, v * 0.92 + contour * 0.45))
                idx_t = int(round(lum * (len(RAMP_TERM) - 1)))
                idx_t = max(0, min(len(RAMP_TERM) - 1, idx_t))
                t_chars.append(RAMP_TERM[idx_t])

        paper_rows.append("".join(p_chars))
        term_rows.append("".join(t_chars))

    with open(ROWS_JSON, "w", encoding="utf-8") as f:
        json.dump({"paper": paper_rows, "terminal": term_rows, "cols": COLS, "rows": ROWS}, f, indent=2)
    print(f"✓ Saved {ROWS} rows of {COLS} cols to {ROWS_JSON}")

    # Build standalone terminal card svr-ascii.svg
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
                 f'svr1339@github:~$ whoami <tspan fill="{INK}">Sai Vardhan</tspan></text>')
    status_chars = len("svr1339@github:~$ whoami Sai Vardhan ")
    parts.append(f'<rect x="{PAD + status_chars * 13 * 0.6:.1f}" y="{status_y-12:.1f}" width="8" height="14" fill="{CURSOR}">'
                 f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.51;1" '
                 f'dur="1s" repeatCount="indefinite"/></rect>')

    parts.append("</svg>")
    svg_content = "".join(parts)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"✓ Wrote {OUT} ({len(svg_content)} bytes)")

if __name__ == "__main__":
    generate()
