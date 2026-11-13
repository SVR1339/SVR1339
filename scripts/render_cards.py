#!/usr/bin/env python3
"""
render_cards.py — SVR1339 GitHub Profile Card Generator
Modelled on AVIVASHISHTA29's approach but completely re-skinned.

Design system: "SOVEREIGN" — dark marble, electric amber, cold white.
  bg:        #0a0a0a   (deep black)
  surface:   #111111   (card bg)
  border:    #1e1e1e
  amber:     #f5a623   (primary accent — sovereignty)
  white:     #f0f0f0   (primary text)
  muted:     #555555
  rust:      #c0392b   (BUILD)
  violet:    #7c3aed   (FORGE)
  teal:      #0d9488   (DEPLOY)
  marble:    #d4c5a9   (profile image tint)

Fonts embedded as WOFF base64 (Geist + Geist Mono — same as Avi, different look).
Run: python scripts/render_cards.py
"""

import os, json, math, base64, textwrap
from pathlib import Path
from datetime import datetime, timedelta

# ── paths ────────────────────────────────────────────────────────────────────
ROOT   = Path(__file__).parent.parent
CARDS  = ROOT / "cards"
DATA   = ROOT / "data"
ASSETS = ROOT / "assets"
CARDS.mkdir(exist_ok=True)

USERNAME = "SVR1339"
NAME     = "Banda Sai Vardhan Reddy"
HANDLE   = "SVR1339"
ROLE     = "Sovereign Engineer · Builder of Autonomous Systems"
COMPANY  = "HIREPAT Ltd"
SITE     = "bsvr.work"
LOCATION = "Global"
BIO      = "Building systems that run themselves. Rust, Python, TypeScript. Infrastructure for the sovereign developer."

# ── palette ──────────────────────────────────────────────────────────────────
C = {
    "bg":      "#0a0a0a",
    "surface": "#111111",
    "border":  "#1e1e1e",
    "amber":   "#f5a623",
    "white":   "#f0f0f0",
    "muted":   "#555555",
    "rust":    "#c0392b",
    "violet":  "#7c3aed",
    "teal":    "#0d9488",
    "marble":  "#d4c5a9",
    "dim":     "#2a2a2a",
}

MONO  = "Geist Mono, ui-monospace, 'Cascadia Code', Menlo, monospace"
SANS  = "Geist, system-ui, -apple-system, sans-serif"
SERIF = "Georgia, 'Times New Roman', serif"

W = 880   # all cards same width
RX = 0    # sharp corners — sovereign aesthetic

# ── load contribution data ────────────────────────────────────────────────────
def load_contributions():
    p = DATA / "contributions.json"
    if p.exists():
        return json.loads(p.read_text())
    # Placeholder until GitHub Actions fetches real data
    import random, math
    days = []
    base = datetime.now() - timedelta(days=371)
    random.seed(42)
    for i in range(371):
        d = base + timedelta(days=i)
        wd = d.weekday()
        # Heavier on weekdays, spiky bursts
        base_w = 0.75 if wd < 5 else 0.25
        count = 0
        if random.random() < base_w:
            weights = [30,20,15,12,10,8,5]
            count = random.choices([0,1,2,4,7,12,20], weights=weights)[0]
        days.append({"date": d.strftime("%Y-%m-%d"), "count": count})
    return days

CONTRIBUTIONS = load_contributions()

# ── helpers ───────────────────────────────────────────────────────────────────
def svg_wrap(content, w, h, extra_defs=""):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<defs>
<style>
  @keyframes fadeUp   {{ from {{ opacity:0; transform:translateY(12px); }} to {{ opacity:1; transform:translateY(0); }} }}
  @keyframes fadeIn   {{ from {{ opacity:0; }} to {{ opacity:1; }} }}
  @keyframes grow     {{ from {{ transform:scaleY(0); transform-origin:bottom; }} to {{ transform:scaleY(1); transform-origin:bottom; }} }}
  @keyframes pulse    {{ 0%,100% {{ opacity:1; }} 50% {{ opacity:0.4; }} }}
  @keyframes shimmer  {{ 0% {{ stop-color:{C['amber']}; stop-opacity:0.1; }} 50% {{ stop-color:{C['amber']}; stop-opacity:0.4; }} 100% {{ stop-color:{C['amber']}; stop-opacity:0.1; }} }}
  .fu0  {{ animation: fadeUp 0.5s ease 0.0s both; }}
  .fu1  {{ animation: fadeUp 0.5s ease 0.1s both; }}
  .fu2  {{ animation: fadeUp 0.5s ease 0.2s both; }}
  .fu3  {{ animation: fadeUp 0.5s ease 0.3s both; }}
  .fu4  {{ animation: fadeUp 0.5s ease 0.4s both; }}
  .fu5  {{ animation: fadeUp 0.5s ease 0.5s both; }}
  .fu6  {{ animation: fadeUp 0.5s ease 0.6s both; }}
  .fu7  {{ animation: fadeUp 0.5s ease 0.7s both; }}
  .fu8  {{ animation: fadeUp 0.5s ease 0.8s both; }}
  .fi0  {{ animation: fadeIn 0.6s ease 0.0s both; }}
  .fi1  {{ animation: fadeIn 0.6s ease 0.15s both; }}
  .fi2  {{ animation: fadeIn 0.6s ease 0.3s both; }}
  .fi3  {{ animation: fadeIn 0.6s ease 0.45s both; }}
  .fi4  {{ animation: fadeIn 0.6s ease 0.6s both; }}
</style>
{extra_defs}
</defs>
<rect width="{w}" height="{h}" fill="{C['bg']}"/>
{content}
</svg>"""


def pill(x, y, text, bg=None, fg=None, w=None):
    bg = bg or C["dim"]
    fg = fg or C["muted"]
    pw = w or (len(text) * 7 + 20)
    return f"""
<rect x="{x}" y="{y}" width="{pw}" height="22" rx="4" fill="{bg}"/>
<text x="{x+10}" y="{y+15}" fill="{fg}" font-size="11" font-weight="600"
  font-family="{MONO}" letter-spacing="0.08em">{text}</text>"""


# ══════════════════════════════════════════════════════════════════════════════
# HERO CARD
# ══════════════════════════════════════════════════════════════════════════════
def render_hero():
    H = 420
    # Profile image — the marble bust with headphones
    # Embedded as a referenced external image (GitHub serves it from the repo)
    img_url = "https://raw.githubusercontent.com/SVR1339/SVR1339/main/assets/profile.jpg"

    # Dithered portrait area (right side) — 300x300 image panel
    portrait_x = W - 320
    portrait_y = 60

    # Gradient shimmer on name
    defs = f"""
<linearGradient id="nameShine" x1="0%" y1="0%" x2="100%" y2="0%">
  <stop offset="0%"   stop-color="{C['amber']}" />
  <stop offset="50%"  stop-color="{C['white']}" />
  <stop offset="100%" stop-color="{C['amber']}" />
  <animateTransform attributeName="gradientTransform" type="translate"
    from="-1 0" to="1 0" dur="3s" repeatCount="indefinite"/>
</linearGradient>
<linearGradient id="imgFade" x1="0%" y1="0%" x2="100%" y2="0%">
  <stop offset="0%"  stop-color="{C['bg']}" stop-opacity="1"/>
  <stop offset="40%" stop-color="{C['bg']}" stop-opacity="0"/>
</linearGradient>
<clipPath id="imgClip">
  <rect x="{portrait_x}" y="{portrait_y}" width="300" height="300" rx="0"/>
</clipPath>"""

    content = f"""
<rect width="{W}" height="{H}" fill="{C['bg']}"/>
<rect x="0" y="{H-3}" width="{W}" height="3" fill="{C['amber']}"/>

{pill(28, 28, f"◈  SOVEREIGN ENGINEER  ·  {COMPANY.upper()}", C['dim'], C['amber'], 320)}

<text x="28" y="120" font-size="82" font-weight="700" font-family="{SANS}"
  fill="url(#nameShine)" class="fu0">SVR</text>
<text x="200" y="120" font-size="82" font-weight="300" font-family="{SANS}"
  fill="{C['white']}" class="fu1">1339</text>

<text x="28" y="155" font-size="15" font-family="{MONO}" fill="{C['amber']}"
  letter-spacing="0.12em" class="fu2">{NAME.upper()}</text>

<text x="28" y="195" font-size="13" font-family="{SANS}" fill="{C['muted']}"
  class="fu3">{BIO[:60]}</text>
<text x="28" y="213" font-size="13" font-family="{SANS}" fill="{C['muted']}"
  class="fu3">{BIO[60:] if len(BIO)>60 else ''}</text>

<text x="28" y="260" font-size="12" font-family="{MONO}" fill="{C['muted']}"
  class="fu4">📍 {LOCATION}  ·  🌐 {SITE}</text>

<text x="28" y="310" font-size="11" font-family="{MONO}" fill="{C['dim']}"
  class="fu5">$ ls ~/builds</text>
<text x="28" y="328" font-size="11" font-family="{MONO}" fill="{C['amber']}"
  class="fu5">HidingJackson/   PRUBETH-CLI/   HIREPATH-TM/   mercury/</text>
<text x="28" y="346" font-size="11" font-family="{MONO}" fill="{C['amber']}"
  class="fu6">prubeth-ide/     smartthings/   nexaplatform/</text>

<text x="28" y="{H-28}" font-size="11" font-family="{MONO}" fill="{C['muted']}"
  class="fu7">{SITE} ↗</text>

<!-- Portrait (marble bust with headphones) -->
<image href="{img_url}" x="{portrait_x}" y="{portrait_y}"
  width="300" height="300" clip-path="url(#imgClip)"
  preserveAspectRatio="xMidYMid meet" class="fi0"/>
<rect x="{portrait_x}" y="{portrait_y}" width="300" height="300"
  fill="url(#imgFade)"/>
"""
    out = svg_wrap(content, W, H, defs)
    (CARDS / "hero.svg").write_text(out, encoding="utf-8")
    print("  ✓ hero.svg")


# ══════════════════════════════════════════════════════════════════════════════
# HEATMAP CARD
# ══════════════════════════════════════════════════════════════════════════════
def contrib_color(n):
    if n == 0:  return C["dim"]
    if n < 3:   return "#3d2b00"
    if n < 7:   return "#7a5500"
    if n < 12:  return "#b87d00"
    return C["amber"]

def render_heatmap():
    days = CONTRIBUTIONS[-371:]
    # pad to week boundary
    while len(days) % 7: days.insert(0, {"date":"","count":0})

    cell, gap = 12, 3
    cols = len(days)//7
    pad_x, pad_y = 48, 56
    HH = pad_y + 7*(cell+gap) + 44

    total = sum(d["count"] for d in days)

    months_seen, month_labels = set(), []
    cells = []
    for i, d in enumerate(days):
        col = i//7
        row = i%7
        x   = pad_x + col*(cell+gap)
        y   = pad_y + row*(cell+gap)
        n   = d["count"]
        clr = contrib_color(n)
        dt  = d.get("date","")
        delay = f"{(i//7)*0.005:.3f}s"
        if dt and row==0:
            m = dt[5:7]
            if m not in months_seen:
                try:
                    lbl = datetime.strptime(dt,"%Y-%m-%d").strftime("%b")
                    month_labels.append(f'<text x="{x}" y="{pad_y-10}" fill="{C["muted"]}" font-size="9" font-family="{MONO}">{lbl}</text>')
                    months_seen.add(m)
                except: pass
        cells.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="1" fill="{clr}" style="animation:fadeIn 0.3s ease {delay} both"><title>{n} on {dt}</title></rect>')

    day_lbl = []
    for i,l in enumerate(["Sun","Mon","Tue","Wed","Thu","Fri","Sat"]):
        if i%2:
            yy = pad_y + i*(cell+gap) + cell-2
            day_lbl.append(f'<text x="{pad_x-6}" y="{yy}" fill="{C["muted"]}" font-size="8" text-anchor="end" font-family="{MONO}">{l}</text>')

    legend_x = W-110
    legend_y = HH-16
    legend = "".join([f'<rect x="{legend_x+i*18}" y="{legend_y-10}" width="12" height="12" rx="1" fill="{contrib_color(c)}"/>' for i,c in enumerate([0,2,5,10,20])])

    content = f"""
<rect width="{W}" height="{HH}" fill="{C['bg']}"/>
<rect x="0" y="{HH-3}" width="{W}" height="3" fill="{C['amber']}"/>
<text x="28" y="28" font-size="13" font-family="{SERIF}" font-style="italic"
  fill="{C['white']}" class="fu0">Every commit, in amber</text>
<text x="{W-28}" y="28" text-anchor="end" font-size="9" font-family="{MONO}"
  fill="{C['amber']}" letter-spacing="0.1em" class="fu0">REFRESHED DAILY · {total:,} TOTAL</text>
{''.join(month_labels)}
{''.join(day_lbl)}
{''.join(cells)}
{legend}
<text x="{legend_x-28}" y="{legend_y}" fill="{C['muted']}" font-size="8" font-family="{MONO}">Less</text>
<text x="{legend_x+94}" y="{legend_y}" fill="{C['muted']}" font-size="8" font-family="{MONO}">More</text>"""

    (CARDS/"heatmap.svg").write_text(svg_wrap(content,W,HH), encoding="utf-8")
    print("  ✓ heatmap.svg")


# ══════════════════════════════════════════════════════════════════════════════
# ACTIVITY CARD (12-month bar chart)
# ══════════════════════════════════════════════════════════════════════════════
def render_activity():
    H = 300
    days = CONTRIBUTIONS[-371:]
    # bucket by month
    months = {}
    for d in days:
        dt = d.get("date","")
        if not dt: continue
        key = dt[:7]
        months[key] = months.get(key,0) + d["count"]
    keys   = sorted(months)[-12:]
    counts = [months[k] for k in keys]
    labels = [datetime.strptime(k,"%Y-%m").strftime("%b") for k in keys]
    total  = sum(counts)
    mx     = max(counts) if counts else 1

    bar_x0, bar_y0 = 28, 220
    bar_w  = (W//2 - 60) // max(len(keys), 1)
    bar_h  = 160
    if not keys:
        # No data yet — render placeholder
        H2 = H
        content = f"""
<rect width="{W}" height="{H2}" fill="{C['bg']}"/>
<rect x="0" y="{H2-3}" width="{W}" height="3" fill="{C['amber']}"/>
<text x="{W//2}" y="{H2//2}" text-anchor="middle" font-size="13" font-family="{MONO}"
  fill="{C['muted']}">— activity data loads after first GitHub Actions run —</text>"""
        (CARDS/"activity.svg").write_text(svg_wrap(content,W,H2), encoding="utf-8")
        print("  ✓ activity.svg (placeholder)")
        return

    bars = []
    for i,(cnt,lbl) in enumerate(zip(counts,labels)):
        bh    = int((cnt/mx)*bar_h) if mx else 0
        bx    = bar_x0 + i*bar_w
        by    = bar_y0 - bh
        clr   = C["amber"] if cnt==mx else C["dim"]
        bars.append(f"""
<rect x="{bx+2}" y="{by}" width="{bar_w-6}" height="{bh}" fill="{clr}" rx="1"
  style="animation:grow 0.5s ease {i*0.05:.2f}s both">
  <title>{cnt} in {lbl}</title>
</rect>
<text x="{bx+bar_w//2}" y="{bar_y0+14}" text-anchor="middle"
  fill="{C['muted']}" font-size="9" font-family="{MONO}">{lbl}</text>""")
        if cnt==mx:
            bars.append(f'<text x="{bx+bar_w//2}" y="{by-6}" text-anchor="middle" fill="{C["amber"]}" font-size="9" font-family="{MONO}">{cnt}</text>')

    # streak/stats panel (right)
    rx   = W//2 + 20
    streak = max((i+1 for i,d in enumerate(reversed(days)) if d["count"]>0), default=0)
    busiest = max(counts) if counts else 0
    days_active = sum(1 for d in days if d["count"]>0)

    stats_items = [
        (f"{streak}", "current streak",    C["amber"]),
        (f"{days_active}/371", "days active", C["white"]),
        (f"{busiest}",  "busiest month",   C["muted"]),
    ]
    stat_svgs = "".join([f"""
<g transform="translate({rx}, {60+i*80})">
  <text x="0" y="0" fill="{clr}" font-size="38" font-weight="700"
    font-family="{MONO}" class="fu{i}">{val}</text>
  <text x="0" y="22" fill="{C['muted']}" font-size="11"
    font-family="{SANS}" class="fu{i}">{lbl}</text>
</g>""" for i,(val,lbl,clr) in enumerate(stats_items)])

    content = f"""
<rect width="{W}" height="{H}" fill="{C['bg']}"/>
<rect x="0" y="{H-3}" width="{W}" height="3" fill="{C['amber']}"/>
<text x="28" y="36" font-size="13" font-family="{SERIF}" font-style="italic"
  fill="{C['white']}" class="fu0">The last 12 months</text>
<text x="{W-28}" y="36" text-anchor="end" font-size="9" font-family="{MONO}"
  fill="{C['amber']}" letter-spacing="0.1em" class="fu0">{total:,} CONTRIBUTIONS</text>
<line x1="{W//2}" y1="50" x2="{W//2}" y2="{H-30}" stroke="{C['border']}" stroke-width="1"/>
{''.join(bars)}
{stat_svgs}"""

    (CARDS/"activity.svg").write_text(svg_wrap(content,W,H), encoding="utf-8")
    print("  ✓ activity.svg")


# ══════════════════════════════════════════════════════════════════════════════
# THREE WORLD TILES: BUILD / FORGE / DEPLOY
# ══════════════════════════════════════════════════════════════════════════════
def render_tile(fname, label, value, sub, color):
    TW, TH = 293, 160   # 880/3 ≈ 293
    content = f"""
<rect width="{TW}" height="{TH}" fill="{color}"/>
<rect x="0" y="{TH-4}" width="{TW}" height="4" fill="{C['bg']}"/>
<text x="20" y="36" font-size="11" font-weight="700" font-family="{MONO}"
  fill="{C['bg']}" letter-spacing="0.14em" class="fu0">{label}</text>
<text x="20" y="96" font-size="52" font-weight="700" font-family="{SANS}"
  fill="{C['bg']}" class="fu1">{value}</text>
<text x="20" y="130" font-size="11" font-family="{SANS}"
  fill="{C['bg']}" opacity="0.75" class="fu2">{sub}</text>"""
    out = svg_wrap(content, TW, TH)
    (CARDS/fname).write_text(out, encoding="utf-8")
    print(f"  ✓ {fname}")

def render_tiles():
    render_tile("build.svg",  "BUILD · SOVEREIGN SYSTEMS", "14+",  "autonomous + stealth tools",   C["rust"])
    render_tile("forge.svg",  "FORGE · DEVELOPER TOOLS",   "PRUBETH", "AI-powered dev runtime",    C["violet"])
    render_tile("deploy.svg", "DEPLOY · GLOBAL INFRA",     "GLOBAL",  "HIREPAT · bsvr.work",       C["teal"])


# ══════════════════════════════════════════════════════════════════════════════
# SECTION TITLE CARDS
# ══════════════════════════════════════════════════════════════════════════════
def render_title(fname, text, bg, fg):
    TH = 56
    content = f"""
<rect width="{W}" height="{TH}" fill="{bg}"/>
<text x="28" y="36" font-size="15" font-weight="600" font-family="{MONO}"
  fill="{fg}" letter-spacing="0.08em">{text}</text>
<text x="{W-28}" y="36" text-anchor="end" font-size="11" font-family="{MONO}"
  fill="{fg}" opacity="0.5">SVR1339</text>"""
    out = svg_wrap(content, W, TH)
    (CARDS/fname).write_text(out, encoding="utf-8")
    print(f"  ✓ {fname}")

def render_titles():
    render_title("title-dark.svg",  "$ ls ~/builds  —  What I'm building", C["bg"],      C["amber"])
    render_title("title-light.svg", "$ ls ~/builds  —  What I'm building", "#f5f5f4",    "#0a0a0a")


# ══════════════════════════════════════════════════════════════════════════════
# REPO CARDS
# ══════════════════════════════════════════════════════════════════════════════
REPOS = [
    {
        "name":  "HidingJackson",
        "desc":  "Sovereign stealth proxy · WinTUN · 600+ global nodes",
        "lang":  "Rust",
        "stars": 0,
        "color": C["rust"],
        "file":  "repo-hidingjackson.svg",
    },
    {
        "name":  "PRUBETH-CLI",
        "desc":  "Elite autonomous developer CLI · multi-model AI runtime",
        "lang":  "Python",
        "stars": 0,
        "color": C["violet"],
        "file":  "repo-prubeth.svg",
    },
    {
        "name":  "HIREPATH-TM",
        "desc":  "AI job platform · resume tailoring · auto-apply · billing",
        "lang":  "TypeScript",
        "stars": 0,
        "color": C["teal"],
        "file":  "repo-hirepath.svg",
    },
]

def render_repo_card(r):
    TW, TH = 293, 130
    content = f"""
<rect width="{TW}" height="{TH}" fill="{C['surface']}"/>
<rect x="0" y="0" width="4" height="{TH}" fill="{r['color']}"/>
<rect x="0" y="{TH-2}" width="{TW}" height="2" fill="{C['border']}"/>
<text x="20" y="32" font-size="14" font-weight="700" font-family="{MONO}"
  fill="{C['white']}" class="fu0">{r['name']}</text>
<text x="20" y="56" font-size="10" font-family="{SANS}" fill="{C['muted']}"
  class="fu1">{r['desc'][:48]}</text>
<text x="20" y="72" font-size="10" font-family="{SANS}" fill="{C['muted']}"
  class="fu1">{r['desc'][48:] if len(r['desc'])>48 else ''}</text>
<text x="20" y="{TH-16}" font-size="10" font-family="{MONO}" fill="{r['color']}"
  class="fu2">{r['lang']}</text>
<text x="{TW-20}" y="{TH-16}" text-anchor="end" font-size="10"
  font-family="{MONO}" fill="{C['muted']}" class="fu2">★ {r['stars']}</text>"""
    out = svg_wrap(content, TW, TH)
    (CARDS/r["file"]).write_text(out, encoding="utf-8")
    print(f"  ✓ {r['file']}")

def render_repos():
    for r in REPOS: render_repo_card(r)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print(f"\n🗿  Rendering profile cards for @{USERNAME}...\n")
    render_hero()
    render_heatmap()
    render_activity()
    render_tiles()
    render_titles()
    render_repos()
    print(f"\n✅  All cards written to ./cards/\n")
