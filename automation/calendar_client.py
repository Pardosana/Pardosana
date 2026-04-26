"""Google Calendar client backed by an OAuth refresh token.

We deliberately avoid forcing an interactive OAuth flow on the operator. The flow is:

1. Operator runs `python automation/oauth_bootstrap.py` once → produces a refresh token.
2. Refresh token is stored as `GOOGLE_REFRESH_TOKEN` env var (or Devin org secret).
3. This client trades the refresh token for short-lived access tokens on demand.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

import requests


GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_CALENDAR_BASE = "https://www.googleapis.com/calendar/v3"


@dataclass(frozen=True)
class CalendarEvent:
    event_id: str
    summary: str
    start_iso: str
    end_iso: str
    attendees: list[str]
    description: str
    raw: dict[str, Any]


class CalendarClient:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        refresh_token: str,
        calendar_id: str = "primary",
    ):
        for label, value in (("client_id", client_id), ("client_secret", client_secret), ("refresh_token", refresh_token)):
            if not value:
                raise ValueError(f"Google {label} is required.")
        self._client_id = client_id
        self._client_secret = client_secret
        self._refresh_token = refresh_token
        self._calendar_id = calendar_id
        self._access_token: str | None = None
        self._expires_at: datetime | None = None

    def _refresh(self) -> str:
        response = requests.post(
            GOOGLE_TOKEN_URL,
            data={
                "client_id": self._client_id,
                "client_secret": self._client_secret,
                "refresh_token": self._refresh_token,
                "grant_type": "refresh_token",
            },
            timeout=20,
        )
        response.raise_for_status()
        payload = response.json()
        self._access_token = payload["access_token"]
        self._expires_at = datetime.now(timezone.utc) + timedelta(seconds=int(payload.get("expires_in", 3500)) - 60)
        return self._access_token

    def _token(self) -> str:
        if self._access_token and self._expires_at and self._expires_at > datetime.now(timezone.utc):
            return self._access_token
        return self._refresh()

    def list_upcoming(self, hours_ahead: int = 24) -> list[CalendarEvent]:
        now = datetime.now(timezone.utc)
        time_min = now.isoformat()
        time_max = (now + timedelta(hours=hours_ahead)).isoformat()
        response = requests.get(
            f"{GOOGLE_CALENDAR_BASE}/calendars/{self._calendar_id}/events",
            headers={"Authorization": f"Bearer {self._token()}"},
            params={
                "timeMin": time_min,
                "timeMax": time_max,
                "singleEvents": "true",
                "orderBy": "startTime",
                "maxResults": 50,
            },
            timeout=20,
        )
        response.raise_for_status()
        items = response.json().get("items", [])
        events: list[CalendarEvent] = []
        for item in items:
            events.append(
                CalendarEvent(
                    event_id=item.get("id", ""),
                    summary=item.get("summary", ""),
                    start_iso=(item.get("start", {}) or {}).get("dateTime", "") or (item.get("start", {}) or {}).get("date", ""),
                    end_iso=(item.get("end", {}) or {}).get("dateTime", "") or (item.get("end", {}) or {}).get("date", ""),
                    attendees=[a.get("email", "") for a in item.get("attendees", []) if isinstance(a, dict)],
                    description=item.get("description", "") or "",
                    raw=item,
                )
            )
        return events
