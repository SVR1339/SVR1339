#!/usr/bin/env python3
"""
fetch_contributions.py — fetches SVR1339's authentic live contribution data via GitHub GraphQL API.
Writes data/contributions.json for render_cards.py to consume.
Works locally via GitHub CLI (`gh api graphql`) or in GitHub Actions via GITHUB_TOKEN / GH_TOKEN.
"""
import json
import os
import shutil
import subprocess
import urllib.request
from pathlib import Path

USERNAME = "SVR1339"
ROOT = Path(__file__).parent.parent
OUT = ROOT / "data" / "contributions.json"
OUT.parent.mkdir(exist_ok=True)

GRAPHQL_QUERY = """
query {
  user(login: "%s") {
    contributionsCollection {
      contributionCalendar {
        totalContributions
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
""" % USERNAME

def parse_and_save(raw_json_str):
    raw = json.loads(raw_json_str)
    cal = raw["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    total = cal["totalContributions"]
    days = []
    for week in cal["weeks"]:
        for day in week["contributionDays"]:
            days.append({
                "date": day["date"],
                "count": day["contributionCount"]
            })
    
    OUT.write_text(json.dumps(days, indent=2))
    print(f"✓ Successfully fetched {len(days)} days · {total:,} total live contributions → data/contributions.json")
    return True

def fetch_via_gh():
    if not shutil.which("gh"):
        return False
    try:
        res = subprocess.run(
            ["gh", "api", "graphql", "-f", f"query={GRAPHQL_QUERY}"],
            capture_output=True, text=True, cwd=str(ROOT)
        )
        if res.returncode == 0 and res.stdout.strip():
            return parse_and_save(res.stdout)
    except Exception as e:
        print("Note: gh cli attempt:", e)
    return False

def fetch_via_token():
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        return False
    try:
        req = urllib.request.Request(
            "https://api.github.com/graphql",
            data=json.dumps({"query": GRAPHQL_QUERY}).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {token}",
                "User-Agent": "SVR1339-Profile-Updater",
                "Content-Type": "application/json",
            }
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read().decode("utf-8")
            return parse_and_save(content)
    except Exception as e:
        print("Note: Token request attempt:", e)
    return False

def main():
    if fetch_via_gh():
        return
    if fetch_via_token():
        return
    if OUT.exists():
        print(f"⚠️ API query failed; keeping existing cached {OUT.name}")
    else:
        print("❌ Error: Unable to fetch live contributions and no local cache found.")

if __name__ == "__main__":
    main()
