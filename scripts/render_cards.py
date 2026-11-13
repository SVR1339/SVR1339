#!/usr/bin/env python3
"""
render_cards.py  —  SVR1339 GitHub Profile · v2  "PRINCIPAL ARCHITECT"
=====================================================================
Generates every SVG card for the profile README.
All assets embedded inline — no external HTTP calls at render time.

Design: dark-marble ink-on-paper aesthetic.
  bg         #0a0a0a   deep black
  surface    #111111   card bg
  border     #1e1e1e
  amber      #f5a623   primary accent
  amber2     #c47a0f   darker amber
  white      #f0ede8   warm white / marble
  muted      #555045
  rust       #b83228   BUILD tile
  violet     #6d28d9   FORGE tile
  teal       #0f766e   DEPLOY tile
  marble     #d4c5a9   portrait tint

Cards produced
  cards/hero.svg                   Hero banner (ASCII portrait + bio)
  cards/heatmap.svg                365-day contribution grid
  cards/activity.svg               12-month bar chart + streak
  cards/build.svg                  Tile 1 — BUILD
  cards/forge.svg                  Tile 2 — FORGE
  cards/deploy.svg                 Tile 3 — DEPLOY
  cards/title-dark.svg             Section divider (dark mode)
  cards/title-light.svg            Section divider (light mode)
  cards/repo-hidingjackson.svg     Repo card
  cards/repo-prubeth.svg           Repo card
  cards/repo-hirepath.svg          Repo card
"""

import json, math, base64
from pathlib import Path
from datetime import datetime, timedelta

ROOT   = Path(__file__).parent.parent
CARDS  = ROOT / "cards";  CARDS.mkdir(exist_ok=True)
DATA   = ROOT / "data"
ASSETS = ROOT / "assets"

USERNAME = "SVR1339"
NAME     = "Banda Sai Vardhan Reddy"
COMPANY  = "HIREPAT Ltd"
SITE     = "bsvr.work"
LOCATION = "Global"
ROLE1    = "Principal Engineer"
ROLE2    = "Full-Stack Systems Engineer"
BIO      = "Rust · Python · TypeScript · C++  —  infrastructure for the professional developer."

W = 880   # all cards same width

# ── palette ──────────────────────────────────────────────────────────────────
C = dict(
    bg="#0a0a0a", surface="#111111", surface2="#161616",
    border="#1e1e1e", border2="#262626",
    amber="#f5a623", amber2="#c47a0f",
    white="#f0ede8", muted="#6b6356", dim="#272320",
    rust="#b83228", violet="#6d28d9", teal="#0f766e",
    marble="#d4c5a9", green="#22c55e",
)

MONO  = "\"Geist Mono\",\"Cascadia Code\",\"Fira Code\",Menlo,monospace"
SANS  = "\"Geist\",system-ui,-apple-system,sans-serif"
SERIF = "\"Playfair Display\",Georgia,serif"

# ── shared CSS injected into every SVG ───────────────────────────────────────
BASE_CSS = f"""
  @keyframes fadeUp  {{from{{opacity:0;transform:translateY(10px)}}to{{opacity:1;transform:translateY(0)}}}}
  @keyframes fadeIn  {{from{{opacity:0}}to{{opacity:1}}}}
  @keyframes grow    {{from{{transform:scaleY(0.02)}}to{{transform:scaleY(1)}}}}
  @keyframes pulse   {{0%,100%{{opacity:1}}50%{{opacity:0.3}}}}
  @keyframes scan    {{0%{{transform:translateY(0)}}100%{{transform:translateY(100%)}}}}
  @keyframes typing  {{from{{clip-path:inset(0 100% 0 0)}}to{{clip-path:inset(0 0 0 0)}}}}
  .a0{{animation:fadeUp .5s ease 0.00s both}}  .a1{{animation:fadeUp .5s ease 0.08s both}}
  .a2{{animation:fadeUp .5s ease 0.16s both}}  .a3{{animation:fadeUp .5s ease 0.24s both}}
  .a4{{animation:fadeUp .5s ease 0.32s both}}  .a5{{animation:fadeUp .5s ease 0.40s both}}
  .a6{{animation:fadeUp .5s ease 0.48s both}}  .a7{{animation:fadeUp .5s ease 0.56s both}}
  .a8{{animation:fadeUp .5s ease 0.64s both}}  .a9{{animation:fadeUp .5s ease 0.72s both}}
  .f0{{animation:fadeIn .6s ease 0.00s both}}  .f1{{animation:fadeIn .6s ease 0.12s both}}
  .f2{{animation:fadeIn .6s ease 0.24s both}}  .f3{{animation:fadeIn .6s ease 0.36s both}}
  .f4{{animation:fadeIn .6s ease 0.48s both}}  .f5{{animation:fadeIn .6s ease 0.60s both}}
"""

def svg(body, w, h, extra_defs="", bg=None):
    bg_color = bg or C["bg"]
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{w}" height="{h}" viewBox="0 0 {w} {h}">\n'
        f'<defs><style>{BASE_CSS}</style>{extra_defs}</defs>\n'
        f'<rect width="{w}" height="{h}" fill="{bg_color}"/>\n'
        f'{body}\n</svg>'
    )

def write(name, content):
    p = CARDS / name
    p.write_text(content, encoding="utf-8")
    kb = p.stat().st_size / 1024
    print(f"  ✓  {name:<40} {kb:>6.1f} KB")

def amber_rule(w, h, thickness=3):
    return f'<rect x="0" y="{h-thickness}" width="{w}" height="{thickness}" fill="{C["amber"]}"/>'

def top_rule(w, thickness=3):
    return f'<rect x="0" y="0" width="{w}" height="{thickness}" fill="{C["amber"]}"/>'

def mono(x, y, text, size=11, fill=None, cls="", anchor="start", weight="400", spacing="0.08em"):
    fill = fill or C["muted"]
    anchor_attr = f'text-anchor="{anchor}"' if anchor != "start" else ""
    return (f'<text x="{x}" y="{y}" font-family={MONO} font-size="{size}" '
            f'fill="{fill}" font-weight="{weight}" letter-spacing="{spacing}" '
            f'{anchor_attr} class="{cls}">{text}</text>')

def sans(x, y, text, size=14, fill=None, cls="", anchor="start", weight="400"):
    fill = fill or C["white"]
    anchor_attr = f'text-anchor="{anchor}"' if anchor != "start" else ""
    return (f'<text x="{x}" y="{y}" font-family={SANS} font-size="{size}" '
            f'fill="{fill}" font-weight="{weight}" {anchor_attr} class="{cls}">{text}</text>')

def serif(x, y, text, size=18, fill=None, cls="", style=""):
    fill = fill or C["white"]
    return (f'<text x="{x}" y="{y}" font-family={SERIF} font-size="{size}" '
            f'fill="{fill}" font-style="{style}" class="{cls}">{text}</text>')

# ── contribution data ─────────────────────────────────────────────────────────
def load_contribs():
    p = DATA / "contributions.json"
    if p.exists():
        data = json.loads(p.read_text())
        if data:
            return data
    # Realistic placeholder
    import random; random.seed(99)
    days, base = [], datetime.now() - timedelta(days=371)
    for i in range(371):
        d   = base + timedelta(days=i)
        wt  = 0.80 if d.weekday() < 5 else 0.30
        cnt = 0
        if random.random() < wt:
            cnt = random.choices([1,2,3,5,8,13,21], weights=[30,22,18,12,8,6,4])[0]
        days.append({"date": d.strftime("%Y-%m-%d"), "count": cnt})
    return days

CONTRIBS = load_contribs()

# ══════════════════════════════════════════════════════════════════════════════
# HERO CARD  —  full-width banner  880 × 440
# Left: big type + bio + terminal snippet
# Right: ASCII portrait (read from cards/portrait.svg, embed inline)
# ══════════════════════════════════════════════════════════════════════════════
def render_hero():
    H = 440
    portrait_path = CARDS / "portrait.svg"

    # Try to embed portrait as a foreign-object block; fallback to placeholder
    if portrait_path.exists():
        portrait_raw = portrait_path.read_text(encoding="utf-8")
        # Measure its declared width/height
        import re
        wm = re.search(r'width="(\d+)"', portrait_raw)
        hm = re.search(r'height="(\d+)"', portrait_raw)
        pw = int(wm.group(1)) if wm else 460
        ph = int(hm.group(1)) if hm else 420
        # Scale to fit right panel
        scale = min(410/pw, 420/ph)
        sw, sh = int(pw*scale), int(ph*scale)
        px = W - sw - 10
        py = (H - sh) // 2
        # Encode the portrait SVG as a data URI image (GitHub renders this)
        portrait_b64 = base64.b64encode(portrait_raw.encode()).decode()
        portrait_block = (
            f'<image href="data:image/svg+xml;base64,{portrait_b64}" '
            f'x="{px}" y="{py}" width="{sw}" height="{sh}"/>'
        )
        # Left-to-right fade mask over the portrait seam
        fade_x = px - 60
        fade_block = (
            f'<defs><linearGradient id="hFade" x1="0" y1="0" x2="1" y2="0">'
            f'<stop offset="0%" stop-color="{C["bg"]}" stop-opacity="1"/>'
            f'<stop offset="100%" stop-color="{C["bg"]}" stop-opacity="0"/>'
            f'</linearGradient></defs>'
            f'<rect x="{fade_x}" y="0" width="80" height="{H}" fill="url(#hFade)"/>'
        )
    else:
        portrait_block = ""
        fade_block = ""
        pw = 0

    left_w = W - 420   # text area width

    # Animated gradient on name
    name_defs = (
        f'<linearGradient id="nGrad" x1="0%" y1="0%" x2="100%" y2="0%">'
        f'<stop offset="0%"   stop-color="{C["amber"]}"><animate attributeName="stop-color" values="{C["amber"]};{C["white"]};{C["amber"]}" dur="4s" repeatCount="indefinite"/></stop>'
        f'<stop offset="100%" stop-color="{C["white"]}"><animate attributeName="stop-color" values="{C["white"]};{C["amber"]};{C["white"]}" dur="4s" repeatCount="indefinite"/></stop>'
        f'</linearGradient>'
    )

    # Pulsing status dot
    status_dot = (
        f'<circle cx="30" cy="34" r="5" fill="{C["amber"]}">'
        f'<animate attributeName="opacity" values="1;0.2;1" dur="2s" repeatCount="indefinite"/>'
        f'</circle>'
    )

    body = f"""
{portrait_block}
{fade_block}

{top_rule(W)}

{status_dot}
{mono(44, 38, f"PRINCIPAL ENGINEER  ·  {COMPANY.upper()}", size=10, fill=C["amber"], cls="a0", weight="600")}

<text x="28" y="118" font-family={SANS} font-size="88" font-weight="800"
  fill="url(#nGrad)" class="a1">SVR</text>
<text x="195" y="118" font-family={SANS} font-size="88" font-weight="200"
  fill="{C["white"]}" opacity="0.9" class="a2">1339</text>

{mono(28, 148, f"$ whoami", size=12, fill=C["amber"], cls="a3", weight="600")}
{sans(28, 172, NAME, size=16, fill=C["white"], cls="a4", weight="300")}

{mono(28, 206, BIO, size=11, fill=C["muted"], cls="a5")}

{mono(28, 244, f"$ ls ~/builds", size=11, fill=C["amber"], cls="a6", weight="600")}
{mono(28, 262, "HidingJackson/    PRUBETH-CLI/     HIREPATH-TM/", size=11, fill=C["marble"], cls="a7")}
{mono(28, 278, "mercury/          prubeth-ide/     smartthings/", size=11, fill=C["marble"], cls="a7")}

{mono(28, 318, f"$ cat about.txt", size=11, fill=C["amber"], cls="a8", weight="600")}
{mono(28, 336, "Rust · Python · TypeScript · C++ · C#", size=11, fill=C["muted"], cls="a8")}
{mono(28, 352, f"📍 {LOCATION}  ·  🌐 {SITE}  ·  🏢 {COMPANY}", size=11, fill=C["muted"], cls="a9")}

{mono(28, H-20, f"{SITE} ↗", size=11, fill=C["amber"], cls="a9")}

{amber_rule(W, H)}
"""
    extra = name_defs
    write("hero.svg", svg(body, W, H, extra_defs=extra))


# ══════════════════════════════════════════════════════════════════════════════
# HEATMAP CARD  —  "Every commit, in amber"
# ══════════════════════════════════════════════════════════════════════════════
HEAT_COLORS = ["#1a1612", "#3d2b00", "#7a5500", "#b87d00", "#f5a623", "#ffc94d"]

def heat_color(n):
    if n == 0:  return HEAT_COLORS[0]
    if n < 2:   return HEAT_COLORS[1]
    if n < 5:   return HEAT_COLORS[2]
    if n < 10:  return HEAT_COLORS[3]
    if n < 18:  return HEAT_COLORS[4]
    return HEAT_COLORS[5]

def render_heatmap():
    days = CONTRIBS[:]
    while len(days) % 7: days.insert(0, {"date":"","count":0})
    days = days[-371:]
    total = sum(d["count"] for d in days)

    cell, gap = 13, 3
    cols      = len(days) // 7
    px, py    = 52, 64
    H         = py + 7*(cell+gap) + 54

    seen_months, month_svg = set(), []
    cell_svg = []
    for i, d in enumerate(days):
        col = i // 7; row = i % 7
        x = px + col*(cell+gap); y = py + row*(cell+gap)
        n = d["count"]; dt = d.get("date","")
        clr = heat_color(n)
        delay = f"{(col*0.008):.3f}s"
        tip = f"{n} contributions · {dt}"
        cell_svg.append(
            f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2" fill="{clr}" '
            f'style="animation:fadeIn 0.4s ease {delay} both">'
            f'<title>{tip}</title></rect>'
        )
        if dt and row == 0:
            m = dt[5:7]
            if m not in seen_months:
                try:
                    lbl = datetime.strptime(dt, "%Y-%m-%d").strftime("%b")
                    month_svg.append(mono(x, py-12, lbl, size=9, fill=C["muted"]))
                    seen_months.add(m)
                except: pass

    day_svg = []
    for i, lbl in enumerate(["Sun","Mon","Tue","Wed","Thu","Fri","Sat"]):
        if i % 2 == 1:
            yy = py + i*(cell+gap) + cell - 1
            day_svg.append(mono(px-6, yy, lbl, size=8, fill=C["muted"], anchor="end"))

    # Legend
    lx = W - 120; ly = H - 14
    legend = "".join(
        f'<rect x="{lx+i*18}" y="{ly-11}" width="13" height="13" rx="2" fill="{c}"/>'
        for i,c in enumerate(HEAT_COLORS)
    )

    body = f"""
{top_rule(W)}
{serif(28, 36, "Every commit, in amber", size=15, fill=C["white"], style="italic", cls="a0")}
{mono(W-28, 36, f"REFRESHED DAILY  ·  {total:,} TOTAL", size=9, fill=C["amber"],
      anchor="end", weight="600", cls="a0")}
{''.join(month_svg)}
{''.join(day_svg)}
{''.join(cell_svg)}
{legend}
{mono(lx-30, ly, "Less", size=8, fill=C["muted"])}
{mono(lx+108, ly, "More", size=8, fill=C["muted"])}
{amber_rule(W, H)}
"""
    write("heatmap.svg", svg(body, W, H))


# ══════════════════════════════════════════════════════════════════════════════
# ACTIVITY CARD  —  "The last 12 months"  880 × 310
# Left: 12-month animated bar chart
# Right: streak · days active · busiest month
# ══════════════════════════════════════════════════════════════════════════════
def render_activity():
    H = 310
    days = CONTRIBS[-371:]

    # Monthly buckets
    months = {}
    for d in days:
        dt = d.get("date",""); n = d["count"]
        if dt: months[dt[:7]] = months.get(dt[:7], 0) + n
    keys   = sorted(months)[-12:]
    counts = [months[k] for k in keys]
    labels = [datetime.strptime(k,"%Y-%m").strftime("%b") for k in keys]
    total  = sum(counts)
    mx     = max(counts, default=1)

    # Bar chart (left half)
    bx0, by0 = 32, 240
    bw       = max(1, (W//2 - 60) // max(len(keys),1))
    bh_max   = 170

    bars = []
    for i, (cnt, lbl) in enumerate(zip(counts, labels)):
        bh    = int((cnt / mx) * bh_max) if mx else 0
        bx    = bx0 + i * bw
        by    = by0 - bh
        clr   = C["amber"] if cnt == mx else C["dim"]
        stroke= C["amber"] if cnt == mx else "none"
        delay = f"{i*0.06:.2f}s"
        bars.append(f"""
<rect x="{bx+2}" y="{by}" width="{bw-6}" height="{bh}" fill="{clr}"
  rx="2" transform-origin="{bx+bw//2} {by0}"
  style="animation:grow 0.6s cubic-bezier(.4,0,.2,1) {delay} both">
  <title>{cnt} contributions in {lbl}</title>
</rect>
{mono(bx+bw//2, by0+14, lbl, size=8, fill=C["muted"], anchor="middle")}
""")
        if cnt == mx:
            bars.append(mono(bx+bw//2, by-6, str(cnt), size=9, fill=C["amber"], anchor="middle", cls="a5"))

    # Divider
    mid = W // 2
    divider = f'<line x1="{mid}" y1="50" x2="{mid}" y2="{H-30}" stroke="{C["border2"]}" stroke-width="1"/>'

    # Current streak
    streak = 0
    for d in reversed(days):
        if d["count"] > 0: streak += 1
        else: break
    days_active = sum(1 for d in days if d["count"] > 0)
    busiest_m   = labels[counts.index(mx)] if counts else "—"

    stats = [
        (str(streak),       "day streak",          C["amber"]),
        (f"{days_active}", "days active / 371",    C["white"]),
        (f"{mx:,}",        f"best month ({busiest_m})", C["marble"]),
    ]
    stat_svgs = "".join([f"""
<g transform="translate({mid+32},{52+i*82})" class="a{i}">
  <text x="0" y="0" font-family={MONO} font-size="42" font-weight="700"
    fill="{clr}">{val}</text>
  <text x="0" y="22" font-family={SANS} font-size="11" fill="{C["muted"]}">{lbl}</text>
</g>""" for i,(val,lbl,clr) in enumerate(stats)])

    body = f"""
{top_rule(W)}
{serif(28, 36, "The last 12 months", size=15, fill=C["white"], style="italic", cls="a0")}
{mono(W-28, 36, f"{total:,} CONTRIBUTIONS", size=9, fill=C["amber"], anchor="end", weight="600", cls="a0")}
{divider}
{''.join(bars)}
{stat_svgs}
{amber_rule(W, H)}
"""
    write("activity.svg", svg(body, W, H))


# ══════════════════════════════════════════════════════════════════════════════
# THREE WORLD TILES  293 × 180
# ══════════════════════════════════════════════════════════════════════════════
TILES = [
    ("build.svg",  "BUILD", "Core Systems",      "14+ autonomous tools",          C["rust"],   "rust"),
    ("forge.svg",  "FORGE", "Developer Runtime",      "PRUBETH · AI-powered CLI",      C["violet"], "violet"),
    ("deploy.svg", "DEPLOY","Global Infrastructure",  "HIREPAT · bsvr.work",           C["teal"],   "teal"),
]

def render_tile(fname, label, value, sub, color, _key):
    TW, TH = 294, 180
    # Animated tilt/bounce on load
    extra_css = "@keyframes tiltIn{from{transform:perspective(600px) rotateX(20deg);opacity:0}to{transform:perspective(600px) rotateX(0);opacity:1}}"
    body = f"""
<rect width="{TW}" height="{TH}" fill="{color}"/>
<rect x="0" y="0" width="{TW}" height="4" fill="rgba(255,255,255,0.25)"/>
<rect x="0" y="{TH-4}" width="{TW}" height="4" fill="{C['bg']}"/>
{mono(18, 32, label, size=10, fill=C["bg"], weight="700", spacing="0.18em")}
<text x="18" y="104" font-family={SANS} font-size="38" font-weight="800"
  fill="{C['bg']}" class="a1" style="animation:tiltIn 0.5s ease 0.1s both">{value}</text>
{sans(18, 138, sub, size=12, fill=C["bg"], cls="a2")}
<circle cx="{TW-24}" cy="28" r="10" fill="rgba(255,255,255,0.15)"/>
<text x="{TW-24}" y="34" font-family="{MONO}" font-size="13" fill="rgba(255,255,255,0.7)"
  text-anchor="middle">↗</text>
"""
    write(fname, svg(body, TW, TH, extra_defs=f"<style>{extra_css}</style>", bg=color))

def render_tiles():
    for args in TILES: render_tile(*args)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION TITLE CARDS
# ══════════════════════════════════════════════════════════════════════════════
def render_title(fname, text, bg_clr, fg_clr, accent):
    TH = 60
    body = f"""
<rect width="{W}" height="{TH}" fill="{bg_clr}"/>
<rect x="0" y="0" width="4" height="{TH}" fill="{accent}"/>
{mono(20, 36, text, size=13, fill=fg_clr, weight="600", spacing="0.1em")}
{mono(W-20, 36, USERNAME, size=10, fill=accent, anchor="end", weight="400")}
"""
    write(fname, svg(body, W, TH, bg=bg_clr))

def render_titles():
    render_title("title-dark.svg",  "$ ls ~/builds  ·  What I'm building", C["bg"],      C["white"], C["amber"])
    render_title("title-light.svg", "$ ls ~/builds  ·  What I'm building", "#f4f1ec",    "#0a0a0a",  "#c47a0f")


# ══════════════════════════════════════════════════════════════════════════════
# REPO CARDS  294 × 140
# ══════════════════════════════════════════════════════════════════════════════
REPOS = [
    ("repo-hidingjackson.svg", "HidingJackson",
     "High-performance stealth proxy · WinTUN · Fake-IP · 600+ global nodes",
     "Rust", 0, C["rust"]),
    ("repo-prubeth.svg", "PRUBETH-CLI",
     "Elite autonomous dev CLI · multi-model AI software engineering runtime",
     "Python", 0, C["violet"]),
    ("repo-hirepath.svg", "HIREPATH-TM",
     "AI job platform · resume tailoring · auto-apply · subscription billing",
     "TypeScript", 0, C["teal"]),
]

def render_repo(fname, name, desc, lang, stars, accent):
    TW, TH = 294, 140
    desc_lines = [desc[i:i+42] for i in range(0, min(len(desc),84), 42)]
    desc_svg = "".join(
        mono(18, 62+i*16, l, size=10, fill=C["muted"], cls=f"a{i+2}")
        for i,l in enumerate(desc_lines)
    )
    body = f"""
<rect width="{TW}" height="{TH}" fill="{C['surface']}"/>
<rect x="0" y="0" width="{TW}" height="{TH}" rx="0"
  fill="none" stroke="{C['border2']}" stroke-width="1"/>
<rect x="0" y="0" width="3" height="{TH}" fill="{accent}"/>
<rect x="0" y="{TH-3}" width="{TW}" height="3" fill="{accent}" opacity="0.4"/>
{mono(18, 32, name, size=14, fill=C["white"], weight="700", cls="a0", spacing="0")}
{desc_svg}
{mono(18, TH-18, lang, size=10, fill=accent, cls="a5", weight="600")}
{mono(TW-18, TH-18, f"★ {stars}", size=10, fill=C["muted"], anchor="end", cls="a5")}
"""
    write(fname, svg(body, TW, TH))

def render_repos():
    for args in REPOS: render_repo(*args)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print(f"\n🗿  Rendering PRINCIPAL ARCHITECT cards for @{USERNAME} …\n")
    render_hero()
    render_heatmap()
    render_activity()
    render_tiles()
    render_titles()
    render_repos()
    total_kb = sum(f.stat().st_size for f in CARDS.glob("*.svg")) / 1024
    print(f"\n✅  {len(list(CARDS.glob('*.svg')))} cards · {total_kb:.0f} KB total → ./cards/\n")
