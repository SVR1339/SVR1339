#!/usr/bin/env python3
"""
fetch_contributions.py — fetches SVR1339's authentic live contribution data via GitHub GraphQL API.
Writes data/contributions.json for render_cards.py to consume.
"""
import json
import subprocess
from pathlib import Path

USERNAME = "SVR1339"
ROOT = Path(__file__).parent.parent
OUT = ROOT / "data" / "contributions.json"
OUT.parent.mkdir(exist_ok=True)

query = """
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

def fetch():
    res = subprocess.run(
        ["gh", "api", "graphql", "-f", f"query={query}"],
        capture_output=True, text=True, cwd=str(ROOT)
    )
    if res.returncode != 0 or not res.stdout.strip():
        print("Error calling GitHub GraphQL API:", res.stderr)
        return

    try:
        raw = json.loads(res.stdout)
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
    except Exception as e:
        print("Error parsing GraphQL response:", e)

if __name__ == "__main__":
    fetch()
