from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

from fetch_sources import collect_sources, load_config, save_snapshot
from classify import classify_opportunities
from report import write_daily_reports

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"


def run() -> list[dict[str, Any]]:
    config = load_config()
    snapshots = collect_sources()
    save_snapshot({"sources": snapshots, "config": config})
    items = classify_opportunities(snapshots, config.get("keywords", []), config)
    health_issues = [snapshot for snapshot in snapshots if snapshot.get("status_code") in {403, 404, "error"}]
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    date_str = date.today().isoformat()
    payload = {"items": items, "generated_at": date_str, "health_issues": health_issues}
    output_path = DATA_DIR / f"{date_str}-classified.json"
    with output_path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
    write_daily_reports(items, health_issues)
    return items


if __name__ == "__main__":
    run()
