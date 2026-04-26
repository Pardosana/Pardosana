"""Pre-call brief orchestration.

Given a Google Calendar event (or a manual prospect dict), produce a structured
pre-call brief grounded in the V14.1 master script.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .calendar_client import CalendarEvent
from .llm_analyzer import LLMAnalyzer, PreCallBrief


def event_to_prospect(event: CalendarEvent) -> dict[str, Any]:
    return {
        "title": event.summary,
        "starts_at": event.start_iso,
        "attendees": [a for a in event.attendees if a],
        "description": event.description,
    }


def build_brief(prospect: dict[str, Any], analyzer: LLMAnalyzer) -> dict[str, Any]:
    brief: PreCallBrief = analyzer.pre_call(prospect)
    return {"prospect": prospect, "brief": asdict(brief)}
