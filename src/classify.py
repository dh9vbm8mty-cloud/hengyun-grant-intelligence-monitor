from __future__ import annotations

import datetime as dt
import re
from typing import Any


def normalize_text(value: str | None) -> str:
    return (value or "").lower().replace("\u3000", " ")


def find_signal_hits(text: str, signals: list[str]) -> list[str]:
    lowered = normalize_text(text)
    return [signal for signal in signals if normalize_text(signal) in lowered]


def detect_opportunity_stage(text: str) -> str:
    lowered = normalize_text(text)
    if any(marker in lowered for marker in ["open now", "now open", "applications open", "application open", "currently accepting", "accepting applications", "open for application", "apply now", "申請受理中", "受理中", "開放申請", "開放申請中", "申請期間", "截止日"]):
        return "Open now"
    if any(marker in lowered for marker in ["upcoming", "will open", "opening soon", "scheduled", "to be announced", "即將開放", "預計開放", "將於", "預告"]):
        return "Upcoming"
    if any(marker in lowered for marker in ["closed", "closed deadline", "past application", "archived", "ended", "已截止", "已結束", "歷年", "過往", "已結束申請"]):
        return "Closed but useful reference"
    return "Unknown"


def detect_estimated_fit(text: str) -> str:
    lowered = normalize_text(text)
    rtsu_markers = ["prototype", "prototype development", "engineering development", "technical development", "r&d", "research and development", "startup technical", "engineering", "field testing"]
    steps_markers = ["demonstration", "pilot", "pilot project", "testbed", "field validation", "deployment", "field data", "urban heat", "climate adaptation", "pavement", "thermal management"]
    if any(marker in lowered for marker in rtsu_markers):
        return "Strong fit for RTSU"
    if any(marker in lowered for marker in steps_markers):
        return "Strong fit for STEPS demo"
    return "Needs human review"


def is_generic_agency_title(text: str) -> bool:
    lowered = normalize_text(text)
    if not lowered:
        return False
    generic_markers = [
        "official site",
        "homepage",
        "home page",
        "about",
        "news",
        "announcement",
        "announcements",
        "organization",
        "agency",
        "ministry",
        "department",
        "administration",
        "government",
        "institution",
        "foundation",
        "corporation",
        "company",
        "portal",
        "official website",
        "home |",
    ]
    if any(marker in lowered for marker in generic_markers):
        return True
    if re.search(r"\b(ministry|department|administration|agency|organization|corporation|institution|foundation|bureau|office|board|authority)\b", lowered):
        return True
    if re.search(r"(法人|機構|省|庁|局|部|委員会|政府)", lowered):
        return True
    return False


def has_concrete_opportunity_signal(text: str) -> bool:
    lowered = normalize_text(text)
    english_signals = [
        "open call",
        "call for proposals",
        "application",
        "apply",
        "grant",
        "subsidy",
        "funding",
        "demonstration",
        "pilot",
        "testbed",
        "r&d program",
        "innovation program",
        "startup grant",
        "sbir",
        "public call",
    ]
    japanese_signals = ["公募", "募集", "助成", "補助金", "実証", "研究開発", "事業", "申請", "採択", "公告", "受付", "締切", "予算"]
    if any(signal in lowered for signal in english_signals):
        return True
    return any(signal in lowered for signal in japanese_signals)


def detect_relevance(text: str, keywords: list[str]) -> str:
    lowered = normalize_text(text)
    if any(keyword.lower() in lowered for keyword in ["rtsu", "steps", "smart city", "testbed", "demonstration", "pilot", "urban heat", "climate adaptation", "pavement", "thermal management"]):
        return "High relevance to HENGYUN"
    if any(keyword.lower() in lowered for keyword in keywords):
        return "Medium relevance to HENGYUN"
    return "General funding relevance"


def build_monitored_page(source: dict[str, Any]) -> dict[str, Any]:
    title = source.get("page_title") or source.get("name") or "Monitored source page"
    return {
        "title": title,
        "date": dt.date.today().isoformat(),
        "source": source.get("name"),
        "url": source.get("url"),
        "source_category": source.get("source_category", "Public agency source"),
        "source_quality": "Needs human verification",
        "grant_category": source.get("grant_category", "General funding background"),
        "relevance_to_hengyun": "General funding relevance",
        "opportunity_stage": "Not suitable",
        "estimated_fit": "Needs human review",
        "funding_amount_if_available": "Needs human verification",
        "match_funding_or_self_funding_requirement": "Needs human verification",
        "deadline_if_available": "Needs human verification",
        "eligibility_notes": "Needs human verification",
        "required_partners_or_site": "Needs human verification",
        "required_documents": "Needs human verification",
        "risk_or_blocker": "Source page is being monitored but is not yet a confirmed opportunity.",
        "recommended_action": "Keep monitoring the source for later confirmation of an actual program page.",
        "summary": "Official source page is being monitored but does not yet contain sufficient opportunity language to be treated as a confirmed grant opportunity.",
        "keywords": [],
        "item_type": "monitored_page",
    }


def build_opportunity(source: dict[str, Any], keyword_hits: list[str], signals: list[str], context_keywords: list[str]) -> dict[str, Any]:
    status_code = source.get("status_code")
    is_health_issue = status_code in {403, 404, "error"}
    title_base = source.get("page_title") or source.get("name") or "Official source update"
    title = f"{title_base}"
    text = f"{source.get('page_title') or ''}\n{source.get('snippet') or ''}"
    summary = "Official source content appears to describe a potential grant or funding opportunity. Human review is required before any funding or eligibility conclusion."

    if is_health_issue:
        source_category = "Source health / fetch issue"
        relevance = "General funding relevance"
        risk = f"Fetch issue detected: {source.get('error') or f'HTTP {status_code}'}"
        action = "Verify that the source is still accessible and confirm the official program page before using it."
        stage = "Unknown"
        fit = "Needs human review"
        opportunity = False
    else:
        title_text = source.get("page_title") or source.get("name") or ""
        if is_generic_agency_title(title_text):
            return build_monitored_page(source)
        signal_hits = find_signal_hits(text, signals)
        has_context = any(keyword in normalize_text(text) for keyword in context_keywords)
        has_concrete_signal = has_concrete_opportunity_signal(text)
        opportunity = bool(signal_hits and has_context and has_concrete_signal)
        if not opportunity:
            return build_monitored_page(source)
        source_category = source.get("source_category", "Secondary / needs verification")
        relevance = detect_relevance(text, keyword_hits)
        risk = "Needs human verification"
        action = "Confirm source and program details with the internal team before acting."
        stage = detect_opportunity_stage(text)
        fit = detect_estimated_fit(text)

    return {
        "title": title,
        "date": dt.date.today().isoformat(),
        "source": source.get("name"),
        "url": source.get("url"),
        "source_category": source_category,
        "source_quality": "Needs human verification",
        "grant_category": source.get("grant_category", "General funding background"),
        "relevance_to_hengyun": relevance,
        "opportunity_stage": stage,
        "estimated_fit": fit,
        "funding_amount_if_available": "Needs human verification",
        "match_funding_or_self_funding_requirement": "Needs human verification",
        "deadline_if_available": "Needs human verification",
        "eligibility_notes": "Needs human verification",
        "required_partners_or_site": "Needs human verification",
        "required_documents": "Needs human verification",
        "risk_or_blocker": risk,
        "recommended_action": action,
        "summary": summary,
        "keywords": keyword_hits,
        "item_type": "opportunity" if opportunity else "monitored_page",
    }


def classify_opportunities(snapshots: list[dict[str, Any]], keywords: list[str], config: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    config = config or {}
    signals = config.get("opportunity_signals", [])
    context_keywords = config.get("program_context_keywords", [])
    items = []
    for snapshot in snapshots:
        snippet = snapshot.get("snippet") or ""
        title = snapshot.get("page_title") or ""
        combined_text = f"{title}\n{snippet}"
        keyword_hits = [kw for kw in keywords if kw.lower() in normalize_text(combined_text)]
        item = build_opportunity(snapshot, keyword_hits, signals, context_keywords)
        items.append(item)
    return items
