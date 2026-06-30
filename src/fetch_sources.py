from __future__ import annotations

import datetime as dt
import html
import json
import re
from pathlib import Path
from typing import Any

import requests
import yaml

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config.yaml"
DATA_DIR = ROOT / "data"


def load_config() -> dict[str, Any]:
    with CONFIG_PATH.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def extract_page_title(html_text: str) -> str:
    match = re.search(r"<title[^>]*>(.*?)</title>", html_text, re.IGNORECASE | re.DOTALL)
    if not match:
        return ""
    title = re.sub(r"<[^>]+>", " ", match.group(1))
    title = html.unescape(title)
    title = re.sub(r"\s+", " ", title).strip()
    return title


def clean_text_from_html(html_text: str) -> str:
    text = re.sub(r"<script.*?</script>", " ", html_text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<style.*?</style>", " ", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def fetch_source_snapshot(source: dict[str, Any]) -> dict[str, Any]:
    url = source.get("url", "")
    try:
        response = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        status_code = response.status_code
        html_text = response.text
        page_title = extract_page_title(html_text)
        text = clean_text_from_html(html_text)[:8000]
    except Exception as exc:  # pragma: no cover - network resilience
        return {
            "name": source.get("name"),
            "url": url,
            "status_code": "error",
            "error": str(exc),
            "snippet": "",
            "page_title": "",
            "fetched_at": dt.datetime.utcnow().isoformat() + "Z",
        }

    return {
        "name": source.get("name"),
        "url": url,
        "status_code": status_code,
        "snippet": text,
        "page_title": page_title,
        "fetched_at": dt.datetime.utcnow().isoformat() + "Z",
    }


def save_snapshot(snapshot: dict[str, Any], date_str: str | None = None) -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if date_str is None:
        date_str = dt.date.today().isoformat()
    path = DATA_DIR / f"{date_str}-source-snapshots.json"
    with path.open("w", encoding="utf-8") as fh:
        json.dump(snapshot, fh, indent=2, ensure_ascii=False)
    return path


def collect_sources() -> list[dict[str, Any]]:
    config = load_config()
    sources = config.get("sources", [])
    snapshots = []
    for source in sources:
        snapshots.append(fetch_source_snapshot(source))
    return snapshots
