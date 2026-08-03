"""
Statistics layer.

Responsibility: turn raw contribution days into trainer stats. No SVG or
rendering logic belongs in this file.

Level is based on ROLLING CONSISTENCY (% of the last N weeks with at least
one contribution) rather than cumulative totals. This was a deliberate
choice: a lifetime-total metric quietly rewards tenure/volume over actual
consistency, and unfairly punishes anyone with a shorter GitHub history.
Rolling consistency stays fair regardless of how long you've been coding.
"""

import json
import os
from datetime import datetime, timezone

import config


def compute_level(consistency_pct: float, thresholds: list) -> dict:
    for i, (lower, upper, label) in enumerate(thresholds):
        if lower <= consistency_pct <= upper:
            band_size = (upper - lower) or 1
            progress = ((consistency_pct - lower) / band_size) * 100
            return {
                "level": i + 1,
                "label": label,
                "progressPercent": round(min(max(progress, 0), 100), 1),
            }
    top_index = len(thresholds) - 1
    return {"level": top_index + 1, "label": thresholds[top_index][2], "progressPercent": 100.0}


def main():
    with open("data/contributions.json") as f:
        data = json.load(f)

    # Reuse the exact same week grouping the heatmap renders (Sun-Sat, as
    # GitHub's own calendar groups them) so stats and visual always agree.
    recent_weeks = data["weeks"][-config.ROLLING_WINDOW_WEEKS :]

    total_weeks = len(recent_weeks) or config.ROLLING_WINDOW_WEEKS
    active_weeks = sum(1 for week in recent_weeks if sum(d["count"] for d in week) > 0)
    consistency_pct = round((active_weeks / total_weeks) * 100, 1) if total_weeks else 0.0

    level_info = compute_level(consistency_pct, config.LEVEL_THRESHOLDS)

    trainer = {
        "username": data["username"],
        "activeWeeks": active_weeks,
        "totalWeeks": total_weeks,
        "consistencyPercent": consistency_pct,
        "level": level_info["level"],
        "levelLabel": level_info["label"],
        "progressPercent": level_info["progressPercent"],
        "partner": config.PARTNER_NAME,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
    }

    os.makedirs("data", exist_ok=True)
    with open("data/trainer.json", "w") as f:
        json.dump(trainer, f, indent=2)

    print(
        f"Level {trainer['level']} ({trainer['levelLabel']}) — "
        f"{active_weeks}/{total_weeks} weeks active ({consistency_pct}%)"
    )


if __name__ == "__main__":
    main()
