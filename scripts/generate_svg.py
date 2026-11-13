#!/usr/bin/env python3
"""
GitHub Profile SVG Generator
Generates animated SVG cards for the GitHub profile README.
Modeled after AVIVASHISHTA29's approach — fully customized.
"""

import os
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path

# ─── CONFIG ───────────────────────────────────────────────────────────────────
USERNAME     = os.environ.get("GITHUB_USERNAME", "YOUR_USERNAME")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
OUTPUT_DIR   = Path(__file__).parent.parent / "assets"
OUTPUT_DIR.mkdir(exist_ok=True)

HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

# ─── PALETTE (Tokyo Night) ────────────────────────────────────────────────────
COLORS = {
    "bg":        "#0d1117",
    "surface":   "#161b22",
    "border":    "#21262d",
    "accent":    "#58a6ff",
    "accent2":   "#7c3aed",
    "text":      "#c9d1d9",
    "muted":     "#8b949e",
    "green":     "#3fb950",
    "orange":    "#d29922",
    "red":       "#f85149",
}

FONT = "JetBrains Mono, Fira Code, monospace"


# ─── GITHUB API HELPERS ───────────────────────────────────────────────────────
def fetch_user_info():
    r = requests.get(f"https://api.github.com/users/{USERNAME}", headers=HEADERS)
    return r.json() if r.ok else {}


def fetch_contributions():
    """Fetch last 365 days of contribution data via GraphQL."""
    if not GITHUB_TOKEN:
        print("⚠️  No GITHUB_TOKEN — using placeholder data.")
        return _placeholder_contributions()

    query = """
    query($login: String!) {
      user(login: $login) {
        contributionsCollection {
          contributionCalendar {
            weeks {
              contributionDays {
                date
                contributionCount
              }
            }
          }
        }
      }
    }
    """
    r = requests.post(
        "https://api.github.com/graphql",
        headers={**HEADERS, "Content-Type": "application/json"},
        json={"query": query, "variables": {"login": USERNAME}},
    )
    if r.ok:
        data = r.json()
        weeks = (
            data["data"]["user"]["contributionsCollection"]
            ["contributionCalendar"]["weeks"]
        )
        return [day for week in weeks for day in week["contributionDays"]]
    return _placeholder_contributions()


def _placeholder_contributions():
    """Generate realistic-looking placeholder data."""
    import random
    days = []
    base = datetime.now() - timedelta(days=365)
    for i in range(365):
        d = base + timedelta(days=i)
        # Skew toward weekdays
        weight = 0.7 if d.weekday() < 5 else 0.3
        count = random.choices(
            [0, 1, 2, 4, 6, 10, 15],
            weights=[40, 20, 15, 10, 8, 5, 2]
        )[0] if random.random() < weight else 0
        days.append({"date": d.strftime("%Y-%m-%d"), "contributionCount": count})
    return days


# ─── CONTRIBUTION HEATMAP SVG ─────────────────────────────────────────────────
def contribution_color(count: int) -> str:
    if count == 0:   return COLORS["surface"]
    if count < 3:    return "#0e4429"
    if count < 7:    return "#006d32"
    if count < 12:   return "#26a641"
    return COLORS["green"]


def generate_heatmap_svg(contributions: list) -> str:
    cell = 13
    gap  = 3
    cols = 53
    rows = 7
    pad_x, pad_y = 48, 32
    w = pad_x + cols * (cell + gap) + 20
    h = pad_y + rows * (cell + gap) + 48

    # Build grid (align to Sunday-start)
    from datetime import datetime as dt
    grid = contributions[-365:] if len(contributions) >= 365 else contributions
    # Pad to full weeks
    while len(grid) % 7 != 0:
        grid.insert(0, {"date": "", "contributionCount": 0})

    month_labels = []
    seen_months  = set()
    cells_svg    = []
    total        = sum(d["contributionCount"] for d in grid)

    for idx, day in enumerate(grid):
        col = idx // 7
        row = idx % 7
        x = pad_x + col * (cell + gap)
        y = pad_y + row * (cell + gap)
        count = day["contributionCount"]
        color = contribution_color(count)
        date  = day.get("date", "")

        # Month label
        if date:
            m = date[5:7]
            if m not in seen_months and row == 0:
                label = datetime.strptime(date, "%Y-%m-%d").strftime("%b")
                month_labels.append(f'<text x="{x}" y="{pad_y - 8}" fill="{COLORS["muted"]}" font-size="10" font-family="{FONT}">{label}</text>')
                seen_months.add(m)

        tip = f"{count} contributions on {date}" if date else ""
        cells_svg.append(
            f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2" ry="2" '
            f'fill="{color}"><title>{tip}</title></rect>'
        )

    day_labels = []
    for i, label in enumerate(["Sun","Mon","Tue","Wed","Thu","Fri","Sat"]):
        if i % 2 == 1:
            yy = pad_y + i * (cell + gap) + cell - 2
            day_labels.append(f'<text x="{pad_x - 6}" y="{yy}" fill="{COLORS["muted"]}" font-size="9" text-anchor="end" font-family="{FONT}">{label}</text>')

    footer_y = h - 12
    legend_x = w - 120
    legend_items = "".join([
        f'<rect x="{legend_x + i*18}" y="{footer_y - 10}" width="12" height="12" rx="2" fill="{contribution_color(c)}" />'
        for i, c in enumerate([0, 2, 5, 10, 15])
    ])

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}">
  <defs>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&amp;display=swap');
      .fade-in {{ animation: fadeIn 1.2s ease forwards; opacity: 0; }}
      @keyframes fadeIn {{ to {{ opacity: 1; }} }}
    </style>
  </defs>
  <rect width="{w}" height="{h}" fill="{COLORS['bg']}" rx="10"/>
  <text x="{pad_x}" y="20" fill="{COLORS['accent']}" font-size="11" font-family="{FONT}" font-weight="600">
    {total} contributions in the last year
  </text>
  {''.join(month_labels)}
  {''.join(day_labels)}
  <g class="fade-in">{''.join(cells_svg)}</g>
  {legend_items}
  <text x="{legend_x - 24}" y="{footer_y}" fill="{COLORS['muted']}" font-size="9" font-family="{FONT}">Less</text>
  <text x="{legend_x + 94}" y="{footer_y}" fill="{COLORS['muted']}" font-size="9" font-family="{FONT}">More</text>
</svg>"""


# ─── INFO CARD SVG ────────────────────────────────────────────────────────────
def generate_info_card_svg(user: dict) -> str:
    name     = user.get("name", USERNAME)
    bio      = user.get("bio", "Building things that matter.")
    location = user.get("location", "Earth")
    repos    = user.get("public_repos", 0)
    followers= user.get("followers", 0)
    following= user.get("following", 0)
    w, h     = 460, 300

    lines = bio.split(". ") if bio else [""]
    bio_lines = "".join([
        f'<tspan x="30" dy="20">{l.strip()}</tspan>' for l in lines[:3]
    ])

    stats = [
        ("Repos",     repos,    COLORS["accent"]),
        ("Followers", followers, COLORS["green"]),
        ("Following", following, COLORS["muted"]),
    ]
    stat_items = "".join([
        f"""<g transform="translate({120 + i*120}, 230)">
          <text x="0" y="0" fill="{c}" font-size="22" font-weight="700" font-family="{FONT}" text-anchor="middle">{v}</text>
          <text x="0" y="18" fill="{COLORS['muted']}" font-size="11" font-family="{FONT}" text-anchor="middle">{k}</text>
        </g>"""
        for i, (k, v, c) in enumerate(stats)
    ])

    typing_css = "".join([
        f".l{i} {{ animation: fade 0.4s ease {i*0.15:.2f}s forwards; opacity:0; }}"
        for i in range(10)
    ])

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}">
  <defs>
    <style>
      @keyframes fade {{ to {{ opacity: 1; }} }}
      {typing_css}
    </style>
  </defs>
  <rect width="{w}" height="{h}" fill="{COLORS['surface']}" rx="12"/>
  <rect x="0" y="0" width="4" height="{h}" fill="{COLORS['accent']}" rx="2"/>

  <text x="30" y="45" fill="{COLORS['text']}" font-size="22" font-weight="700"
    font-family="{FONT}" class="l0">{name}</text>

  <text x="30" y="68" fill="{COLORS['accent']}" font-size="12"
    font-family="{FONT}" class="l1">$ whoami</text>

  <text x="30" y="96" fill="{COLORS['muted']}" font-size="13" font-family="{FONT}">
    <tspan x="30" dy="0" class="l2">{bio_lines}</tspan>
  </text>

  <text x="30" y="175" fill="{COLORS['muted']}" font-size="12" font-family="{FONT}" class="l5">
    📍 {location}
  </text>

  <line x1="20" y1="205" x2="{w-20}" y2="205" stroke="{COLORS['border']}" stroke-width="1"/>
  {stat_items}
</svg>"""


# ─── SKILLS SVG ───────────────────────────────────────────────────────────────
SKILLS = [
    # (label, color, icon_char)
    ("Python",      "#3776AB", "🐍"),
    ("TypeScript",  "#3178C6", "📘"),
    ("React",       "#61DAFB", "⚛️"),
    ("Node.js",     "#339933", "🟢"),
    ("FastAPI",     "#009688", "⚡"),
    ("Docker",      "#2496ED", "🐳"),
    ("PostgreSQL",  "#336791", "🐘"),
    ("Redis",       "#DC382D", "🔴"),
    ("AWS",         "#FF9900", "☁️"),
    ("Git",         "#F05032", "🔀"),
    ("Linux",       "#FCC624", "🐧"),
    ("PyTorch",     "#EE4C2C", "🔥"),
]

def generate_skills_svg() -> str:
    cols   = 6
    cell_w = 130
    cell_h = 54
    pad    = 20
    rows   = (len(SKILLS) + cols - 1) // cols
    w      = cols * cell_w + pad * 2
    h      = rows * cell_h + pad * 2 + 32

    items = []
    for i, (label, color, icon) in enumerate(SKILLS):
        col = i % cols
        row = i // cols
        x   = pad + col * cell_w
        y   = pad + 32 + row * cell_h
        delay = f"{i * 0.07:.2f}s"
        items.append(f"""
        <g transform="translate({x},{y})" style="animation: slideUp 0.4s ease {delay} forwards; opacity:0;">
          <rect width="{cell_w - 10}" height="{cell_h - 8}" rx="8"
            fill="{COLORS['surface']}" stroke="{color}" stroke-width="1.5" stroke-opacity="0.6"/>
          <text x="12" y="22" font-size="18" font-family="Segoe UI Emoji, sans-serif">{icon}</text>
          <text x="38" y="24" fill="{COLORS['text']}" font-size="13" font-weight="600"
            font-family="{FONT}">{label}</text>
        </g>""")

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}">
  <defs>
    <style>
      @keyframes slideUp {{ from {{ opacity:0; transform:translateY(10px); }} to {{ opacity:1; transform:translateY(0); }} }}
    </style>
  </defs>
  <rect width="{w}" height="{h}" fill="{COLORS['bg']}" rx="10"/>
  <text x="{pad}" y="24" fill="{COLORS['accent']}" font-size="13" font-weight="600"
    font-family="{FONT}">$ ./skills.sh — tech stack</text>
  {''.join(items)}
</svg>"""


# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    print(f"🚀 Generating SVGs for @{USERNAME}...")

    print("  📡 Fetching user info...")
    user = fetch_user_info()

    print("  📡 Fetching contributions...")
    contributions = fetch_contributions()

    print("  🎨 Generating heatmap SVG...")
    heatmap = generate_heatmap_svg(contributions)
    (OUTPUT_DIR / "contrib-heatmap.svg").write_text(heatmap, encoding="utf-8")

    print("  🎨 Generating info card SVG...")
    info_card = generate_info_card_svg(user)
    (OUTPUT_DIR / "info-card.svg").write_text(info_card, encoding="utf-8")

    print("  🎨 Generating skills SVG...")
    skills = generate_skills_svg()
    (OUTPUT_DIR / "skills.svg").write_text(skills, encoding="utf-8")

    print("✅ All SVGs written to ./assets/")
    print(f"   - contrib-heatmap.svg")
    print(f"   - info-card.svg")
    print(f"   - skills.svg")


if __name__ == "__main__":
    main()
