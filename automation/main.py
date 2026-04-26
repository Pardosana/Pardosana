"""SalesEngine V14.1 automation CLI entrypoint.

Usage examples:

    python -m automation.main --mode pre-call --hours 24
    python -m automation.main --mode post-call --meeting-id <id> --contact me@client.com
    python -m automation.main --dry-run

The CLI never fails hard when credentials are missing — it prints which env vars are
required and returns exit code 0 in `--dry-run` so CI can validate the skeleton.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from .calendar_client import CalendarClient
from .config import Config
from .crm_writer import CRMWriter
from .fathom_client import FathomClient
from .llm_analyzer import LLMAnalyzer
from .post_call import analyze_meeting
from .pre_call import build_brief, event_to_prospect


def _emit(payload: Any) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def cmd_pre_call(cfg: Config, hours: int) -> int:
    missing = cfg.require("google_client_id", "google_client_secret", "google_refresh_token", "llm_api_key")
    if missing:
        _emit({"ok": False, "missing_env": missing, "hint": "Set GOOGLE_CLIENT_ID/SECRET/REFRESH_TOKEN and OPENAI_API_KEY (or ANTHROPIC_API_KEY)."})
        return 0 if cfg.dry_run else 1
    calendar = CalendarClient(
        client_id=cfg.google_client_id or "",
        client_secret=cfg.google_client_secret or "",
        refresh_token=cfg.google_refresh_token or "",
        calendar_id=cfg.google_calendar_id,
    )
    analyzer = LLMAnalyzer(cfg.llm_provider, cfg.llm_api_key, cfg.llm_model, cfg.llm_temperature)
    briefs = []
    for event in calendar.list_upcoming(hours_ahead=hours):
        prospect = event_to_prospect(event)
        briefs.append(build_brief(prospect, analyzer))
    _emit({"ok": True, "briefs": briefs})
    return 0


def cmd_post_call(cfg: Config, meeting_id: str, contact_email: str | None) -> int:
    missing = cfg.require("fathom_api_key", "llm_api_key")
    if missing:
        _emit({"ok": False, "missing_env": missing, "hint": "Set FATHOM_API_KEY and OPENAI_API_KEY (or ANTHROPIC_API_KEY)."})
        return 0 if cfg.dry_run else 1
    fathom = FathomClient(cfg.fathom_api_key or "", cfg.fathom_base_url)
    analyzer = LLMAnalyzer(cfg.llm_provider, cfg.llm_api_key, cfg.llm_model, cfg.llm_temperature)
    crm = CRMWriter(cfg.crm_provider, cfg.crm_api_key, cfg.crm_base_url, dry_run=cfg.dry_run)
    result = analyze_meeting(meeting_id, fathom, analyzer, crm, contact_email)
    _emit({"ok": True, "result": result})
    return 0


def cmd_dry_run(cfg: Config) -> int:
    _emit(
        {
            "ok": True,
            "dry_run": True,
            "config_summary": {
                "fathom_api_key_set": bool(cfg.fathom_api_key),
                "google_oauth_set": all([cfg.google_client_id, cfg.google_client_secret, cfg.google_refresh_token]),
                "google_calendar_id": cfg.google_calendar_id,
                "llm_provider": cfg.llm_provider,
                "llm_model": cfg.llm_model,
                "llm_api_key_set": bool(cfg.llm_api_key),
                "crm_provider": cfg.crm_provider,
            },
        }
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="SalesEngine V14.1 automation engine")
    parser.add_argument("--mode", choices=["pre-call", "post-call", "dry-run"], default="dry-run")
    parser.add_argument("--hours", type=int, default=24, help="Look-ahead window for pre-call mode.")
    parser.add_argument("--meeting-id", help="Fathom meeting id (post-call mode).")
    parser.add_argument("--contact", help="Contact email for CRM writeback (post-call mode).")
    parser.add_argument("--dry-run", action="store_true", help="Force dry-run regardless of env.")
    args = parser.parse_args(argv)

    cfg = Config.from_env()
    if args.dry_run:
        cfg = Config(**{**cfg.__dict__, "dry_run": True})

    if args.mode == "pre-call":
        return cmd_pre_call(cfg, args.hours)
    if args.mode == "post-call":
        if not args.meeting_id:
            _emit({"ok": False, "error": "--meeting-id required in post-call mode"})
            return 2
        return cmd_post_call(cfg, args.meeting_id, args.contact)
    return cmd_dry_run(cfg)


if __name__ == "__main__":
    sys.exit(main())
