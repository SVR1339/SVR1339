#!/usr/bin/env python3
"""
generate_pro_stats.py
Generates an elite, realistic, high-volume contribution history for SVR1339.
Outputs: data/contributions.json
"""
import json, datetime, random
from pathlib import Path

random.seed(1339)

ROOT = Path(__file__).parent.parent
DATA_FILE = ROOT / "data" / "contributions.json"
DATA_FILE.parent.mkdir(exist_ok=True)

today = datetime.date.today()
start_date = today - datetime.timedelta(days=364)

days = []
monthly_totals = {}
active_days = 0
best_day = {"date": "", "count": 0}

for i in range(365):
    d = start_date + datetime.timedelta(days=i)
    d_str = d.isoformat()
    weekday = d.weekday()
    month_key = d_str[:7]

    is_active = random.random() < (0.94 if weekday < 5 else 0.78)

    if is_active:
        weights = [15, 25, 25, 18, 10, 7]
        bucket = random.choices([1, 2, 3, 4, 5, 6], weights=weights)[0]
        if bucket == 1:   count = random.randint(3, 6)
        elif bucket == 2: count = random.randint(7, 12)
        elif bucket == 3: count = random.randint(13, 18)
        elif bucket == 4: count = random.randint(19, 26)
        elif bucket == 5: count = random.randint(27, 36)
        else:             count = random.randint(37, 48)
        active_days += 1
    else:
        count = 0

    if count > best_day["count"]:
        best_day = {"date": d_str, "count": count}

    days.append({"date": d_str, "count": count})
    monthly_totals[month_key] = monthly_totals.get(month_key, 0) + count

# Ensure recent streak is solid 45 days
for day in days[-45:]:
    if day["count"] == 0:
        day["count"] = random.randint(6, 14)
        active_days += 1

total_contributions = sum(d["count"] for d in days)
keys = sorted(monthly_totals.keys())[-12:]
monthly = [{"month": k, "total": monthly_totals[k]} for k in keys]

full_data = {
    "total_contributions": total_contributions,
    "current_streak": {
        "length": 45,
        "start": (today - datetime.timedelta(days=45)).isoformat(),
        "end": today.isoformat()
    },
    "longest_streak": {
        "length": 78,
        "start": "2026-03-01",
        "end": "2026-05-18"
    },
    "active_days": active_days,
    "best_day": best_day,
    "monthly": monthly,
    "days": days
}

with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(full_data, f, indent=2)

print(f"✓ PRO dataset generated:")
print(f"  Total contributions: {total_contributions:,}")
print(f"  Active days:         {active_days} / 365")
print(f"  Current streak:      45 days")
print(f"  Longest streak:      78 days")
print(f"  Busiest day:         {best_day['count']} commits on {best_day['date']}")
