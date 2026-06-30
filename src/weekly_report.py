from __future__ import annotations

import json
from pathlib import Path
from typing import Any

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


def load_latest_health_issues() -> list[dict[str, Any]]:
    data_files = sorted(DATA_DIR.glob("*-classified.json"))
    if not data_files:
        return []
    latest = data_files[-1]
    with latest.open("r", encoding="utf-8") as fh:
        payload = json.load(fh)
    return payload.get("health_issues", [])


def write_weekly_report(items: list[dict[str, Any]], health_issues: list[dict[str, Any]] | None = None) -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    path = REPORTS_DIR / "weekly-grant-brief-notebooklm.txt"
    health_issues = health_issues or []
    opportunities = [item for item in items if item.get("item_type") == "opportunity"]
    monitored_pages = [item for item in items if item.get("item_type") == "monitored_page"]
    lines = [
        "HENGYUN Weekly Grant Intelligence Brief",
        "",
        "1. Internal review warning",
        "This is internal grant intelligence only. Human review is required before any eligibility or funding conclusion.",
        "",
        "2. Weekly executive summary",
        "The monitor collected a small set of official-source updates for review. No eligibility or funding conclusions are made without human verification.",
        "",
        "3. Open or urgent opportunities",
    ]
    if opportunities:
        for item in opportunities:
            lines.append(f"- {item['title']} ({item['source']})")
    else:
        lines.append("- No open or urgent opportunities found.")

    lines.extend([
        "",
        "4. High relevance to HENGYUN",
    ])
    if opportunities:
        for item in opportunities:
            if item.get("relevance_to_hengyun") == "High relevance to HENGYUN":
                lines.append(f"- {item['title']} ({item['source']})")
    else:
        lines.append("- No confirmed high-relevance opportunities found.")

    lines.extend([
        "",
        "5. RTSU / prototype funding candidates",
    ])
    if opportunities:
        for item in opportunities:
            if item.get("estimated_fit") == "Strong fit for RTSU":
                lines.append(f"- {item['title']} ({item['source']})")
    else:
        lines.append("- No confirmed RTSU prototype candidates found.")

    lines.extend([
        "",
        "6. STEPS demo funding candidates",
    ])
    if opportunities:
        for item in opportunities:
            if item.get("estimated_fit") == "Strong fit for STEPS demo":
                lines.append(f"- {item['title']} ({item['source']})")
    else:
        lines.append("- No confirmed STEPS demo candidates found.")

    lines.extend([
        "",
        "7. Japan / international opportunities",
        "- None confirmed in this pass.",
        "",
        "8. Closed but useful reference programs",
    ])
    if opportunities:
        for item in opportunities:
            if item.get("opportunity_stage") == "Closed but useful reference":
                lines.append(f"- {item['title']} ({item['source']})")
    else:
        lines.append("- None confirmed in this pass.")

    lines.extend([
        "",
        "9. Items requiring human verification",
    ])
    for item in opportunities:
        lines.append(f"- {item['title']} requires human verification.")
    if not opportunities:
        lines.append("- No confirmed opportunities requiring human verification.")

    lines.extend([
        "",
        "10. Source watch / monitored pages",
    ])
    if monitored_pages:
        for item in monitored_pages:
            lines.append(f"- {item['title']} ({item['source']}) - monitored source page, not a confirmed opportunity")
    else:
        lines.append("- No monitored source pages captured.")

    lines.extend([
        "",
        "11. Source health / fetch issues",
    ])
    if health_issues:
        for issue in health_issues:
            lines.append(f"- {issue['name']} -> status {issue.get('status_code')} ({issue.get('error') or 'needs review'})")
    else:
        lines.append("- No source health issues captured.")
    lines.extend([
        "",
        "11. Recommended actions for the next 30 days",
        "- Review the captured sources and confirm whether official program pages remain active.",
        "- Prepare a short list of candidate programs for internal review.",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


if __name__ == "__main__":
    items = load_latest_items()
    health_issues = load_latest_health_issues()
    write_weekly_report(items, health_issues)
