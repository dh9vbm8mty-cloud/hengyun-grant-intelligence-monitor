from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
REPORTS_DIR = ROOT / "reports"


def load_latest_items() -> list[dict[str, Any]]:
    data_files = sorted(DATA_DIR.glob("*-classified.json"))
    if not data_files:
        return []
    latest = data_files[-1]
    with latest.open("r", encoding="utf-8") as fh:
        payload = json.load(fh)
    return payload.get("items", [])


def write_daily_reports(items: list[dict[str, Any]], health_issues: list[dict[str, Any]] | None = None) -> list[Path]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    date_str = dt.date.today().isoformat()
    md_path = REPORTS_DIR / f"{date_str}-grant-brief.md"
    notebook_path = REPORTS_DIR / f"{date_str}-grant-brief-notebooklm.txt"
    health_issues = health_issues or []
    opportunities = [item for item in items if item.get("item_type") == "opportunity"]
    monitored_pages = [item for item in items if item.get("item_type") == "monitored_page"]

    md_lines = [
        f"# HENGYUN Grant Intelligence Brief - {date_str}",
        "",
        "This is an internal grant intelligence summary. Human review is required before using any data for decisions.",
        "",
        "## Daily intake",
        "",
    ]
    if opportunities:
        for item in opportunities:
            md_lines.append(f"- {item['title']}")
            md_lines.append(f"  - Source: {item['source']}")
            md_lines.append(f"  - Relevance: {item['relevance_to_hengyun']}")
            md_lines.append(f"  - Summary: {item['summary']}")
            md_lines.append("")
    else:
        md_lines.append("- No opportunities captured in this run.")
        md_lines.append("")

    md_lines.extend([
        "## Source watch / monitored pages",
        "",
    ])
    if monitored_pages:
        for item in monitored_pages:
            md_lines.append(f"- {item['title']}")
            md_lines.append(f"  - Source: {item['source']}")
            md_lines.append(f"  - Note: This is a monitored official source page, not a confirmed opportunity.")
            md_lines.append("")
    else:
        md_lines.append("- No monitored source pages captured in this run.")
        md_lines.append("")

    md_lines.extend([
        "## Source health / fetch issues",
        "",
    ])
    if health_issues:
        for issue in health_issues:
            md_lines.append(f"- {issue['name']} -> status {issue.get('status_code')} ({issue.get('error') or 'needs review'})")
    else:
        md_lines.append("- No source health issues captured.")
    md_lines.extend([
        "",
        "## Recommended actions",
        "",
        "- Review source availability and confirm official program details.",
    ])

    md_path.write_text("\n".join(md_lines), encoding="utf-8")

    notebook_lines = [
        f"HENGYUN Grant Intelligence Brief - {date_str}",
        "",
        "Internal review required.",
        "",
    ]
    if health_issues:
        notebook_lines.append("Source health / fetch issues:")
        for issue in health_issues:
            notebook_lines.append(f"- {issue['name']} -> status {issue.get('status_code')} ({issue.get('error') or 'needs review'})")
        notebook_lines.append("")
    if opportunities:
        notebook_lines.append("Confirmed opportunities:")
        for item in opportunities:
            notebook_lines.append(f"- {item['title']}")
            notebook_lines.append(f"  Source: {item['source']}")
            notebook_lines.append(f"  Summary: {item['summary']}")
            notebook_lines.append("")
    if monitored_pages:
        notebook_lines.append("Monitored pages:")
        for item in monitored_pages:
            notebook_lines.append(f"- {item['title']}")
            notebook_lines.append(f"  Source: {item['source']}")
            notebook_lines.append(f"  Note: monitored source page, not a confirmed opportunity")
            notebook_lines.append("")

    notebook_path.write_text("\n".join(notebook_lines), encoding="utf-8")
    return [md_path, notebook_path]
