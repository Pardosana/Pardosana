"""Centralized configuration for the SalesEngine V14.1 automation engine.

Reads everything from environment variables. No secret value lives in repo.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


def _env(name: str, default: str | None = None) -> str | None:
    value = os.environ.get(name, default)
    if value is None or value == "":
        return None
    return value


@dataclass(frozen=True)
class Config:
    fathom_api_key: str | None
    fathom_base_url: str
    google_client_id: str | None
    google_client_secret: str | None
    google_refresh_token: str | None
    google_calendar_id: str
    llm_provider: str  # "openai" | "anthropic"
    llm_api_key: str | None
    llm_model: str
    llm_temperature: float
    crm_provider: str  # "sharpify" | "noop"
    crm_api_key: str | None
    crm_base_url: str | None
    dry_run: bool

    @classmethod
    def from_env(cls) -> "Config":
        provider = (_env("LLM_PROVIDER", "openai") or "openai").lower()
        crm_provider = (_env("CRM_PROVIDER", "noop") or "noop").lower()
        return cls(
            fathom_api_key=_env("FATHOM_API_KEY"),
            fathom_base_url=_env("FATHOM_BASE_URL", "https://api.fathom.ai/external/v1") or "https://api.fathom.ai/external/v1",
            google_client_id=_env("GOOGLE_CLIENT_ID"),
            google_client_secret=_env("GOOGLE_CLIENT_SECRET"),
            google_refresh_token=_env("GOOGLE_REFRESH_TOKEN"),
            google_calendar_id=_env("GOOGLE_CALENDAR_ID", "primary") or "primary",
            llm_provider=provider,
            llm_api_key=_env("OPENAI_API_KEY") if provider == "openai" else _env("ANTHROPIC_API_KEY"),
            llm_model=_env("LLM_MODEL", "gpt-4o-mini" if provider == "openai" else "claude-sonnet-4-5") or "gpt-4o-mini",
            llm_temperature=float(_env("LLM_TEMPERATURE", "0.2") or "0.2"),
            crm_provider=crm_provider,
            crm_api_key=_env("CRM_API_KEY"),
            crm_base_url=_env("CRM_BASE_URL"),
            dry_run=(_env("DRY_RUN", "0") == "1"),
        )

    def require(self, *names: str) -> list[str]:
        missing: list[str] = []
        for name in names:
            value = getattr(self, name, None)
            if value in (None, ""):
                missing.append(name)
        return missing
