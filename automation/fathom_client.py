"""Thin Fathom API client.

Docs: https://developers.fathom.ai/api-overview#authentication

The free public API exposes meetings and transcripts behind an API key. We keep this
client deliberately minimal — auth, list, fetch transcript, with rate-limit pacing.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Iterable

import requests


@dataclass(frozen=True)
class FathomMeeting:
    meeting_id: str
    title: str
    started_at: str
    duration_seconds: int
    invitees: list[str]
    raw: dict[str, Any]


@dataclass(frozen=True)
class FathomTranscript:
    meeting_id: str
    text: str
    segments: list[dict[str, Any]]
    summary: str | None
    action_items: list[str]


class FathomClient:
    """Minimal wrapper around the Fathom public API."""

    def __init__(self, api_key: str, base_url: str = "https://api.fathom.ai/external/v1", request_pace: float = 1.0):
        if not api_key:
            raise ValueError("Fathom API key is required.")
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._request_pace = request_pace
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"Bearer {api_key}",
                "Accept": "application/json",
                "User-Agent": "SalesEngine-V14.1/automation",
            }
        )

    def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        url = f"{self._base_url}{path}"
        response = self._session.get(url, params=params, timeout=30)
        response.raise_for_status()
        time.sleep(self._request_pace)  # be polite, 60 req/min limit
        return response.json()

    def list_meetings(self, after: str | None = None, limit: int = 50) -> Iterable[FathomMeeting]:
        params: dict[str, Any] = {"limit": limit}
        if after:
            params["created_after"] = after
        payload = self._get("/meetings", params=params)
        for item in payload.get("meetings", []):
            yield FathomMeeting(
                meeting_id=item.get("id") or item.get("meeting_id", ""),
                title=item.get("title", ""),
                started_at=item.get("started_at", ""),
                duration_seconds=int(item.get("duration_seconds", 0) or 0),
                invitees=[i.get("email", "") for i in item.get("invitees", []) if isinstance(i, dict)],
                raw=item,
            )

    def fetch_transcript(self, meeting_id: str) -> FathomTranscript:
        payload = self._get(f"/meetings/{meeting_id}/transcript")
        segments = payload.get("segments", []) or []
        text = "\n".join(seg.get("text", "") for seg in segments if isinstance(seg, dict))
        return FathomTranscript(
            meeting_id=meeting_id,
            text=text,
            segments=segments,
            summary=payload.get("summary"),
            action_items=[a for a in payload.get("action_items", []) if isinstance(a, str)],
        )
