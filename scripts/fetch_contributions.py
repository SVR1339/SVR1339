#!/usr/bin/env python3
"""
fetch_contributions.py — scrapes SVR1339's public contribution data
No auth required (uses the public GitHub calendar endpoint).
Writes data/contributions.json for render_cards.py to consume.
"""
import json, urllib.request, re
from pathlib import Path
from datetime import datetime

USERNAME = "SVR1339"
OUT = Path(__file__).parent.parent / "data" / "contributions.json"
OUT.parent.mkdir(exist_ok=True)

def fetch():
    url = f"https://github.com/users/{USERNAME}/contributions"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    html = urllib.request.urlopen(req, timeout=15).read().decode()

    days = []
    # Parse SVG rect elements: data-date and data-count
    for m in re.finditer(r'data-date="([^"]+)"[^>]*data-count="([^"]+)"', html):
        days.append({"date": m.group(1), "count": int(m.group(2))})

    if not days:
        # Fallback: parse <rect> with title tags
        for m in re.finditer(r'<rect[^>]+data-date="([^"]+)"[^>]+data-count="(\d+)"', html):
            days.append({"date": m.group(1), "count": int(m.group(2))})

    days.sort(key=lambda d: d["date"])
    OUT.write_text(json.dumps(days, indent=2))
    total = sum(d["count"] for d in days)
    print(f"✓ Fetched {len(days)} days · {total:,} total contributions → data/contributions.json")

if __name__ == "__main__":
    fetch()
